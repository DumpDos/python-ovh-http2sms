# -*- coding: utf-8 -*-
from datetime import datetime
from json import loads
import requests
import re


class   OvhHttp2Sms(object):
    '''
    API Documentation:
       http://guides.ovh.com/Http2Sms

    How to use:
       # Instanciate + settings
       hSMS = OvhHttp2Sms(account = 'sms-nic-X', login = 'my_login', password = 'my_pa33w0rd')
       hSMS.setOptions(sender = 'Thibault', no_stop = 1)

       # Send simple message
       hSMS.setMessage("Hello,\n\n How are you?")
       print hSMS.sendTo('+33223344555')
       print hSMS.sendTo(['+33223344555', '+33223344666', '+33223344777'])

       # Send message containing variables --> *|var_name|*
       hSMS.setMessage("Hello *|name|*,\n\n How are you?")
       print hSMS.sendTo({'+33223344555' : {'name' : 'Thibault'},
                          '+33223344666' : {'name' : 'Eleanore'}})
    '''

    __OVH_HTTP2SMS_URL = 'https://www.ovh.com/cgi-bin/sms/http2sms.cgi?'
    __OVH_HTTP2SMS_OPT = {
        'sender'    : '__opt_set_sender',
        'no_stop'   : '__opt_set_no_stop',
        'defered'   : '__opt_set_defered',
        'sms_class' : '__opt_set_sms_class',
        'tag'       : '__opt_set_tag',
    }
    __SEND_METHOD = {
        type('')  : '__send_from_string',
        type(u'') : '__send_from_string',
        type([])  : '__send_from_list',
        type(())  : '__send_from_list',
        type({})  : '__send_from_dict',
    }

    def __init__(self, account, login, password):
        self.__request_opt = {
            'account'  : account,
            'login'    : login,
            'password' : password,
            'from'     : None,
            'noStop'   : None,
            'deferred' : None,
            'tag'      : None,
            'class'    : 1
        }

    def     __regexp_reverse(self, data, dict):
        hReg = re.compile('\*\|(.+?)\|\*', re.VERBOSE)
        return hReg.sub(lambda m : dict.get(m.group(1), ''), data)

    def __opt_set_sender(self, data):
        assert type(data) == str
        self.__request_opt['from'] = data

    def __opt_set_no_stop(self, data):
        assert type(data) == int
        if data not in [0, 1]:
            raise Exception('"%(opt_data)d" is not a valid choice' % {'opt_data' : data})
        self.__request_opt['noStop'] = data

    def __opt_set_defered(self, data):
        assert type(data) == datetime
        self.__request_opt['defered'] = data.strftime('%H%M%d%m%Y')

    def __opt_set_sms_class(self, data):
        assert type(data) == int
        if data not in [0, 1, 2, 3]:
            raise Exception('"%(opt_data)d" is not a valid choice' % {'opt_data' : data})
        self.__request_opt['class'] = data

    def __opt_set_sms_tag(self, data):
        assert type(data) == str
        self.__request_opt['tag'] = data.strip()[:20]

    def __send_from_string(self, data):
        return {data: self.__call_ovh_url(data, self.__message)}

    def __send_from_list(self, data):
        data = [x for i, x in enumerate(data) if x not in data[(i + 1):]]
        dic_ret_val = {}
        for d in data:
            dic_ret_val[d] = self.__call_ovh_url(d, self.__message)
        return dic_ret_val

    def __send_from_dict(self, data):
        dic_ret_val = {}
        for k, v in data.iteritems():
            msg = self.__regexp_reverse(self.__message, v)
            dic_ret_val[k] = self.__call_ovh_url(k, msg)
        return dic_ret_val

    def __call_ovh_url(self, to, message):
        if to.startswith('+') is True:
            to = to.replace('+', '%2B')
        req = '%(base_url)scontentType=text/json&%(opt)s&to=%(to)s&message=%(msg)s' % {'base_url' : self.__OVH_HTTP2SMS_URL,
                                                                                       'opt'      : '&'.join(self.__for_url_opt),
                                                                                       'msg'      : message,
                                                                                       'to'       : to}
        ret_val = requests.get(req)
        return loads(ret_val.text)

    def setMessage(self, msg):
        self.__message = msg.strip().replace('\n', '%0D').replace('<br>', '%0D').replace('<br/>', '%0D').replace('&', '%26')

    def setOptions(self, **kwargs):
        for k, v in kwargs.iteritems():
            try:
                call = getattr(self, '_%(cls_name)s%(func_name)s' % {'cls_name'  : self.__class__.__name__,
                                                                     'func_name' : self.__OVH_HTTP2SMS_OPT[k]})
                call(v)
            except KeyError:
                raise Exception('Unknown option "%(opt_name)s"' % {'opt_name' : k})

    def sendTo(self, dst):
        self.__for_url_opt = []
        map(lambda o: self.__for_url_opt.append('%s=%s' % (o[0], o[1])) if o[1] is not None else None, self.__request_opt.iteritems())
        call = getattr(self, '_%(cls_name)s%(func_name)s' % {'cls_name'  : self.__class__.__name__,
                                                             'func_name' : self.__SEND_METHOD[type(dst)]})
        return call(dst)
