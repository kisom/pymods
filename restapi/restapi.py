# -*- coding: utf-8 -*-
# file: rest.py
# author: kyle isom <coder@kyleisom.net>
#
# rest interface

import base64
import httplib
import sys
import time
import urllib2

class RestApi:
    api_base = None                                   # base URI for API
    secure   = None
    debug    = None                                   # used for __trace__
    authtype = None                                   # type of auth token
    auth_token = None                                 # authentication token
    content_t  = None                                 # content type
    headers    = None                                 # default headers
    authenticated   = None

    last_error = None
    last_req   = None

    supported_methods = [ 'GET', 'POST' ]

    def __init__(self, api_base, debug = False, authtype = None,
                 username = None, password = None, auth_token = None,
                 content_t = None):
        """
        ADD DOCS
        """
        self.api_base = api_base.lower()

        if self.api_base.startswith('https'):
            self.secure   = True
            self.api_base = self.api_base.strip('https://')
        self.api_base = self.api_base.strip('http://')
        self.debug    = debug
        self.authtype = authtype.lower()

        self.__trace__('initialising...')

        if not content_t:
            self.__trace__('setting content type to default')
            self.__set_default_content_type__()
        else:
            self.__trace__('setting content-type to %s' % content_t)
            self.content_t = content_t
        
        if username and password and 'basic' == authtype.lower():
            self.__trace__('setting up basic authentication...')
            self.auth_token =  base64.encodestring('%s:%s' % (username,
                                                              password))
            self.auth_token = 'Basic %s' % ( self.auth_token.strip() )
        elif authtype and auth_token:
            self.__trace__('using authentication token')
            self.auth_token = auth_token.strip()

        # build default request headers
        self.headers = {
                         'Content-Type': self.content_t,
                         'Accept': '*/*'
                        }
        if self.authtype:
            if 'basic' == self.authtype:
                self.headers['Authorization'] = self.auth_token

        self.__modify_headers__()

        # if using authentication, try to authenticate
        if authtype:
            self.authenticated = self.__auth__()
            if self.authenticated:
                self.__trace__('authenticated.')
            else:
                self.__trace__('authentication FAILED!', err = True)

    def __modify_headers__(self):
        # override this to change the content type
        pass

    def __set_default_content_type__(self):
        self.__trace__('setting content type application/x-www-form-urlencoded')
        self.content_t = 'application/x-www-form-urlencoded'

    def __trace__(self, message, err = False):
        if not self.debug: return
        else:
            if err: print '[!]',
            else:   print '[+]',
            
            print '%s> ' % self.__class__,
            print message



    def __fetch__(self, request, data = None, method = "GET"):
        self.__trace__( 'building request...' )
        if not method in self.supported_methods:
            self.__trace__('%s is an unsupported method!' % method)
            return None

        if not self.secure:
            req = httplib.HTTPConnection(self.api_base)
        else:
            req = httplib.HTTPSConnection(self.api_base)
            
        req.request(method, request, data, self.headers)

        response = req.getresponse()
        res = { 'status': response.status,
                'data': self.__process_data__(response.read()) }

        
        self.last_req = req
        self.__trace__( 'request->%s' % request )
        #self.__trace__('request type: %s' % req.get_method())

        if self.api_base.startswith('https'):
            self.__trace__('WARNING: urllib2 does *not* verify SSL certs')

        return res

    def __process_data__(self, data):
        return data

    def __auth__(self):
        if 'basic' == self.authtype:
            try:
                res = self.get('/')

            except urllib2.HTTPError as e:
                if 401 == e.getcode():
                    self.__trace__('should be setting the error here...')
                    self.last_error = e
                    return False
                else:
                    raise
            else:
                return True        

    def get(self, request, *args):
        #req = self.__build__(request, args)
        res = self.__fetch__(request, data = None, method = 'GET')

        return res

    def post(self, request, data, *args):
        # build request and send data
        self.__trace__('posting %s to %s' % (data, request))
        #req  = self.__build__(request, args)
        res  = self.__fetch__(request, data = data, method = 'POST')

        return res

