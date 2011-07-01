# -*- coding: utf-8 -*-
# file: rest.py
# author: kyle isom <coder@kyleisom.net>
#
# rest interface

import base64
import json
import sys
import time
import urllib2

from restapi import RestApi


class JsonApi (RestApi):
    
    def __set_default_content_type__(self):
        self.__trace__('setting content type application/json')
        self.content_t = 'application/json'

    def get(self, request, *args):
        res = RestApi.post(self, request, args)
        if res:
            res = json.loads(res)

        return res

    def post(self, request, data, *args):
        if not type(data) == type(str()):
            data = json.dumps(data)
            
        res  = RestApi.post(self, request, data, args)

        if res:
            res  = json.loads(res)

        return res

        
