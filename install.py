#! /usr/bin/env python

import os
import socket
import django
import requests
from string import Template
from subprocess import call
from six.moves import input

assert not os.path.exists('local_settings.py'), 'Local_settings already defined'

default_hostname = socket.gethostname()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

tpl_url = 'https://gist.githubusercontent.com/filipp/cba2ffecd0d5790f7245/raw/9d5b140ed23c1bbdbadbd5c674d3a00c00d80047/local_settings.py'

fh = open('local_settings.py', 'w')

print("** Creating local configuration file **")
args = {}
args['dbadmin']  = input('DB admin username [pgsql]: ') or os.getenv('pgsql')
args['dbhost']   = input('1/10 Database host [localhost]: ') or 'localhost'
args['dbname']   = input('2/10 Database [servo]: ') or 'servo'
args['dbuser']   = input('3/10 DB user [servo]: ') or 'servo'
args['dbpwd']    = input('4/10 DB password []: ') or ''

assert call(['createuser', args['dbuser'], '-U', args['dbadmin']]) == 0, 'Could not create DB user'

args['secret_key'] = os.urandom(32).encode('base-64').strip()
args['install_locale'] = input('51/10 Locale [sv_SE.UTF-8]: ') or 'sv_SE.UTF-8'
default_country = args['install_locale'].split('_')[0]
args['install_country'] = input('6/10 Country [%s]: ' % default_country) or default_country
default_lang = args['install_locale'].split('_')[1][:2]
args['install_language'] = input('7/10 Language [%s]: ' % default_lang) or default_lang
args['timezone'] = input('8/10 Timezone [Europe/Stockholm]: ') or 'Europe/Stockholm'
args['install_id'] = input('9/10 Installation ID [22]: ') or '22'
args['hostname'] = input('10/10 Hostname [%s]: ' % default_hostname) or default_hostname

raw = requests.get(tpl_url).text
template = Template(raw)

s = template.substitute(**args)

call(['createdb', args['dbname'], '-O', args['dbuser'], '-U', args['dbadmin']])

fh.write(s)
fh.close()

print("** Setting up database tables **")
call(['./manage.py', 'migrate'])
call(['psql', '-c', 'ALTER SEQUENCE servo_order_id_seq RESTART WITH 12345', args['dbname'], args['dbuser']])

print("** Creating directories **")
call(['./manage.py', 'makedirs'])

print("** Creating Super User **")
call(['./manage.py', 'createsuperuser'])

loc = {}
django.setup() # To avoid django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
print("** Creating initial Service Location **")
loc['title']    = input('1/6 Name [PretendCo Inc]: ') or 'PretendCo Inc'
loc['email']    = input('2/6 Email [service@pretendo.com]: ') or 'service@pretendo.com'
loc['phone']    = input('3/6 Phone [123456789]: ') or '123456789'
loc['address']  = input('4/6 Address [Somestreet 1]: ') or 'Somestreet 1'
loc['zip_code'] = input('5/6 Postal code [1234]: ') or '1234'
loc['city']     = input('6/6 City [Stockholm]: ') or 'Stockholm'

from servo.models.common import Location
from servo.models.account import User

first_loc = Location(**loc)
first_loc.save()
su = User.objects.filter(pk=1).update(location=first_loc)

print("** Creating self-signed SSL certificate **")
subj = "/C=%s/ST=%s/L=%s/O=%s/OU=%s/CN=%s" % (
    args['install_country'],
    loc['city'],
    loc['city'],
    loc['title'],
    loc['title'],
    args['hostname']
)

call(['openssl', 'req', '-nodes', '-x509', '-newkey', 'rsa:2048',
      '-days', '365', '-subj', subj,
      '-keyout', 'servo.key', '-out', 'servo.crt'])

print("""
Your Servo installation is ready for action at https://%s.
For testing purposes, you can also run it with ./manage runserver.
""" % args['hostname'])
