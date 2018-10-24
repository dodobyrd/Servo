# -*- coding: utf-8 -*-

import json
import gsxws

from django import forms
from django_countries import countries
from django.utils.translation import ugettext as _

from servo.models import User, Repair, Template
from servo.forms import (BaseForm, AutocompleteTextarea,
                         DateTimePickerInput, ChoiceField,)


class ImportForm(BaseForm):
    """Import GSX repair."""

    confirmation = forms.CharField(min_length=8,
                                   max_length=15,
                                   label=_('Confirmation'),
                                   help_text=_('Please enter the GSX dispatch ID'))


class GsxCustomerForm(BaseForm):
    """Form for GSX customer data."""

    firstName = forms.CharField(max_length=100, label=_('First name'))
    lastName = forms.CharField(max_length=100, label=_('Last name'))
    emailAddress = forms.CharField(max_length=100, label=_('Email'))
    primaryPhone = forms.CharField(max_length=100, label=_('Phone'))
    addressLine1 = forms.CharField(max_length=100, label=_('Address'))
    zipCode = forms.CharField(max_length=100, label=_('ZIP Code'))
    city = forms.CharField(max_length=100, label=_('City'))
    country = ChoiceField(label=_('Country'), choices=countries)
    state = ChoiceField(choices=(('ZZ', _('Other')),), initial="ZZ")


class GsxComponentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        components = kwargs.get('components')
        del(kwargs['components'])
        super(GsxComponentForm, self).__init__(*args, **kwargs)

        if len(components):
            components = json.loads(components)
            for k, v in components.items():
                self.fields[k] = forms.CharField(label=k, required=True, initial=v)

    def clean(self, *args, **kwargs):
        super(GsxComponentForm, self).clean(*args, **kwargs)
        self.json_data = json.dumps(self.cleaned_data)


class StatusForm(forms.Form):
    """Form for updating GSX repair status."""
    status = ChoiceField(label=_('Status'), choices=gsxws.repairs.REPAIR_STATUSES)

    def __init__(self, *args, **kwargs):
        super(StatusForm, self).__init__(*args, **kwargs)
        empty_choice = ('', '----',)
        choices = list(gsxws.repairs.REPAIR_STATUSES)
        choices.insert(0, empty_choice)
        self.fields['status'].choices = choices


class GsxRepairForm(forms.ModelForm):
    class Meta:
        model = Repair
        exclude = []
        widgets = {
            'device': forms.HiddenInput(),
            'parts': forms.CheckboxSelectMultiple(),
            'unit_received_at': DateTimePickerInput(attrs={'readonly': 'readonly'})
        }

    def __init__(self, *args, **kwargs):
        from servo.lib.utils import empty
        super(GsxRepairForm, self).__init__(*args, **kwargs)
        repair = self.instance
        techs = User.techies.filter(location=repair.order.location)
        c = [(u.tech_id, u.get_full_name()) for u in techs]
        c.insert(0, ('', '-------------------',))
        self.fields['tech_id'] = forms.ChoiceField(choices=c,
                                                   required=False,
                                                   label=_('Technician'))
        self.fields['parts'].initial = repair.order.get_parts()

        if repair.can_mark_complete is False:
            del(self.fields['mark_complete'])
            del(self.fields['replacement_sn'])

        template_choices = Template.templates()
        for f in ('notes', 'symptom', 'diagnosis',):
            self.fields[f].widget = AutocompleteTextarea(choices=template_choices)
        
        empty_choice = (('NA', _('Not available')),)
        self.fields['issue_code'] = forms.ChoiceField(
            label=_('Issue code'),
            choices=empty_choice
        )
        self.fields['symptom_code'] = forms.ChoiceField(
            label=_('Symptom group'),
            choices=empty_choice
        )
        
        try:
            symptom_codes = self.instance.get_symptom_code_choices()
            self.fields['symptom_code'].choices = symptom_codes

            if empty(self.instance.symptom_code):
                # default to the first choice
                self.instance.symptom_code = symptom_codes[0][0]
        except gsxws.GsxError as e:
            self.fields['symptom_code'].errors = [e]

        try:
            issue_codes = self.instance.get_issue_code_choices()
            self.fields['issue_code'].choices = issue_codes
        except gsxws.GsxError as e:
            self.fields['issue_code'].errors = [e]

    def clean(self, *args, **kwargs):
        cd = super(GsxRepairForm, self).clean(*args, **kwargs)
        if self.instance.has_serialized_parts():
            if cd.get('mark_complete') and not cd.get('replacement_sn'):
                error = _('Replacement serial number must be set when completing repair.')
                raise forms.ValidationError(error)

        return cd

    def clean_attachment(self):
        max_filesize = 10 * 1024 * 1024  # 10MB
        from django.template.defaultfilters import filesizeformat
        f = self.cleaned_data.get('attachment')
        if f and f.size > max_filesize:
            size = filesizeformat(max_filesize)
            error = _('Attachment should be no larger than %s') % size
            raise forms.ValidationError(error)

        return f
