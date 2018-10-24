# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.views.generic import RedirectView

from servo.views.account import *


urlpatterns = [
    url(r'^$', RedirectView.as_view(url='orders', permanent=False)),

    url(r'^search/$', search, name="accounts-search"),
    url(r'^orders/$', orders, name="accounts-list_orders"),
    url(r'^settings/$', settings, name="accounts-settings"),
    url(r'^stats/$', stats, name="accounts-stats"),
    url(r'^updates/$', updates, name="accounts-updates"),
    url(r'^notifications/clear/$', clear_notifications, name="accounts-clear_notifications"),
]
