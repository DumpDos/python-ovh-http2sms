#!/usr/bin/python
# coding: utf-8
# DumpDos 2018

#--- Librairies ---#

import ovhhttp2sms

hSMS = ovhhttp2sms.OvhHttp2Sms(account = '', login = '', password = '')
hSMS.setOptions(sender='', no_stop=1)
hSMS.setMessage("")
hSMS.sendTo('')
