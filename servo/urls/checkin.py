from django.conf.urls import patterns, url
from servo.views.checkin import *


urlpatterns = patterns(
    '',
    url(r'^$', index, name='checkin-index'),
    url(r'^customer/$', get_customer, name='checkin-get_customer'),
    url(r'^reset/$', reset, name='checkin-reset'),
    url(r'^status/$', status, name='checkin-status'),
    url(r'^checkin/print/(\w+)/$', print_confirmation, name='checkin-print'),
    url(r'^thanks/(\w+)/$', thanks, name='checkin-thanks'),
    url(r'^terms/$', terms, name='checkin-terms'),

)