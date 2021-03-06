# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-29 09:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servo', '0048_auto_20160225_2328'),
    ]

    operations = [
        migrations.AddField(
            model_name='gsxaccount',
            name='timezone',
            field=models.CharField(choices=[(b'PST', b'UTC - 8h (Pacific Standard Time)'), (b'PDT', b'UTC - 7h (Pacific Daylight Time)'), (b'CST', b'UTC - 6h (Central Standard Time)'), (b'CDT', b'UTC - 5h (Central Daylight Time)'), (b'EST', b'UTC - 5h (Eastern Standard Time)'), (b'EDT', b'UTC - 4h (Eastern Daylight Time)'), (b'GMT', b'UTC (Greenwich Mean Time)'), (b'CET', b'UTC + 1h (Central European Time)'), (b'CEST', b'UTC + 2h (Central European Summer Time)'), (b'USZ1', b'UTC + 3h (Kaliningrad Time)'), (b'MSK', b'UTC + 4h (Moscow Time)'), (b'IST', b'UTC + 5.5h (Indian Standard Time)'), (b'YEKST', b'UTC + 6h (Yekaterinburg Time)'), (b'OMSST', b'UTC + 7h (Omsk Time)'), (b'KRAST', b'UTC + 8h (Krasnoyarsk Time)'), (b'CCT', b'UTC + 8h (Chinese Coast Time)'), (b'IRKST', b'UTC + 9h (Irkutsk Time)'), (b'JST', b'UTC + 9h (Japan Standard Time)'), (b'YAKST', b'UTC + 10h (Yakutsk Time)'), (b'AEST', b'UTC + 10h (Australian Eastern Standard Time)'), (b'VLAST', b'UTC + 11h (Vladivostok Time)'), (b'AEDT', b'UTC + 11h (Australian Eastern Daylight Time)'), (b'ACST', b'UTC + 9.5h (Austrailian Central Standard Time)'), (b'ACDT', b'UTC + 10.5h (Australian Central Daylight Time)'), (b'NZST', b'UTC + 12h (New Zealand Standard Time)'), (b'MAGST', b'UTC + 12h (Magadan Time)')], default=b'CEST', max_length=4, verbose_name='Timezone'),
        ),
    ]
