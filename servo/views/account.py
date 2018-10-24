# -*- coding: utf-8 -*-

import csv
from datetime import date

from django.contrib import auth
from django.utils import timezone, translation

from django.contrib import messages
from django.urls import reverse
from django.http import QueryDict, HttpResponse
from dateutil.relativedelta import relativedelta
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, render, get_object_or_404

from servo.lib.utils import paginate
from servo.views.order import prepare_list_view

from servo.models import Order, User
from servo.forms.account import ProfileForm, RegistrationForm, LoginForm


def settings(request):
    """User editing their profile."""
    title = _("Profile Settings")
    form = ProfileForm(instance=request.user)

    if request.method == "POST":

        form = ProfileForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            user = form.save()
            messages.success(request, _("Settings saved"))
            User.refresh_nomail()

            if form.cleaned_data['password1']:
                request.user.set_password(form.cleaned_data['password1'])
                request.user.save()

            lang = user.activate_locale()
            translation.activate(lang)
            request.session[translation.LANGUAGE_SESSION_KEY] = lang
            request.session['django_timezone'] = user.timezone

            return redirect(settings)
        else:
            messages.error(request, _("Error in profile data"))

    return render(request, "accounts/settings.html", locals())


def orders(request):
    """
    This is basically like orders/index, but limited to the user
    First, filter by the provided search criteria,
    then check if we have a saved search filter
    then default to user id
    Always update saved search filter
    """
    args = request.GET.copy()
    default = {'state': Order.STATE_OPEN}

    if len(args) < 2:
        f = request.session.get("account_search_filter", default)
        args = QueryDict('', mutable=True)
        args.update(f)

    # On the profile page, filter by the user, no matter what
    args.update({'followed_by': request.user.pk})
    request.session['account_search_filter'] = args

    data = prepare_list_view(request, args)
    data['title'] = _("My Orders")

    del(data['form'].fields['assigned_to'])

    return render(request, "accounts/orders.html", data)


def login(request):
    """User trying to log in."""
    title = _("Sign In")
    form = LoginForm()

    if 'username' in request.POST:

        form = LoginForm(request.POST)

        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        else:
            message = _('Please enable cookies to use this system')
            url = request.path
            return render(request, 'checkin/error.html', locals())

        if form.is_valid():
            user = auth.authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )

            if user is None:
                messages.error(request, _("Incorrect username or password"))
            elif not user.is_active:
                messages.error(request, _("Your account has been deactivated"))
            else:
                auth.login(request, user)

                if user.location is not None:
                    lang = user.activate_locale()
                    request.session['django_language'] = lang
                    request.session['django_timezone'] = user.timezone

                messages.success(request, _(u"%s logged in") % user.get_full_name())

                if request.GET.get('next'):
                    return redirect(request.GET['next'])
                else:
                    return redirect(orders)
        else:
            messages.error(request, _("Invalid input for login"))

    request.session.set_test_cookie()
    return render(request, "accounts/login.html", locals())


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.info(request, _("You have logged out"))

        return redirect(login)

    return render(request, "accounts/logout.html")


def register(request):
    """
    New user applying for access
    """
    form = RegistrationForm()
    data = {'title': _("Register")}

    if request.method == 'POST':

        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = User(is_active=False)
            user.email = form.cleaned_data['email']
            user.last_name = form.cleaned_data['last_name']
            user.first_name = form.cleaned_data['first_name']
            user.set_password(form.cleaned_data['password'])
            user.save()

            messages.success(request, _(u'Your registration is now pending approval.'))

            return redirect(login)

    data['form'] = form
    return render(request, 'accounts/register.html', data)


def clear_notifications(request):
    from datetime import datetime
    ts = [int(x) for x in request.GET.get('t').split('/')]
    ts = datetime(*ts, tzinfo=timezone.get_current_timezone())
    notif = request.user.notifications.filter(handled_at=None)
    notif.filter(triggered_at__lt=ts).update(handled_at=timezone.now())
    messages.success(request, _('All notifications cleared'))
    return redirect(request.META['HTTP_REFERER'])


def search(request):
    """
    User searching for something from their homepage
    """
    query = request.GET.get("q")

    if not query or len(query) < 3:
        messages.error(request, _('Search query is too short'))
        return redirect('accounts-list_orders')

    request.session['search_query'] = query

    # Redirect Order ID:s to the order
    try:
        order = Order.objects.get(code__iexact=query)
        return redirect(order)
    except Order.DoesNotExist:
        pass

    kwargs = request.GET.copy()
    kwargs.update({'followed_by': request.user.pk})
    data = prepare_list_view(request, kwargs)

    data['title'] = _("Search results")
    orders = data['queryset']
    data['orders'] = orders.filter(customer__fullname__icontains=query)

    return render(request, "accounts/orders.html", data)


def stats(request):
    from servo.views.stats import prep_view, BasicStatsForm
    data = prep_view(request)
    form = BasicStatsForm(initial=data['initial'])
    if request.method == 'POST':
        form = BasicStatsForm(request.POST, initial=data['initial'])
        if form.is_valid():
            request.session['stats_filter'] = form.cleaned_data
    data['form'] = form
    return render(request, "accounts/stats.html", data)


def updates(request):
    title = _('Updates')
    kind = request.GET.get('kind', 'note_added')
    events = request.user.notifications.filter(action=kind)
    page = request.GET.get("page")
    events = paginate(events, page, 100)

    return render(request, "accounts/updates.html", locals())
