import hashlib
import json
from flask import request
import datetime
import copy

class RestKeyGen(object):

    def make_cache_key(self, *args, key_prefix=""):
        """cache key"""
        md = hashlib.md5()
        for arg in args:
            if arg is None:
                md.update("None".encode('utf-8'))
            elif  type(arg) == dict or type(arg) == list or type(arg) == tuple or type(arg) == str:
                md.update(json.dumps(arg).encode('utf-8'))
        hex_digest = str(md.hexdigest())
        if key_prefix and hex_digest:
            cache_key = key_prefix + '_' + hex_digest
        else:
            cache_key = hex_digest
        return cache_key

    def make_metric_cache_key(self, *args, **kwargs):
        """ metric cache key"""
        metric_name = kwargs.get('metric_name', None)
        key_materials = []
        key_materials.append(request.url)
        client_id = request.headers.get('client-id', '')
        if request.args and len(request.args) > 0 :
            key_materials.append(request.args)
        if request.method == "POST" and request.json and len(request.json) > 0:
            json = copy.deepcopy(request.json)
            if 'start_date' in json:
                start_date = None
                try:
                    inp_datetime = datetime.datetime.fromisoformat(json['start_date'])
                    start_date = inp_datetime.timestamp()
                except ValueError:
                    start_date = json['start_date']
                try:
                    json['start_date'] = str((int(start_date) // 60) * 60)
                except ValueError:
                    pass
            if 'end_date' in json:
                end_date = None
                try:
                    inp_datetime = datetime.datetime.fromisoformat(json['end_date'])
                    end_date = inp_datetime.timestamp()
                except ValueError:
                    end_date = json['end_date']
                try:
                    json['end_date'] = str((int(end_date) // 60) * 60)
                except ValueError:
                    pass
            key_materials.append(json)
        if client_id:
            key_materials.append(client_id)
        return self.make_cache_key(*key_materials, key_prefix=metric_name)
