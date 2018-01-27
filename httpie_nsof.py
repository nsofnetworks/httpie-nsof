"""
Nsof OAuth2 plugin for HTTPie.

"""
import urlparse
import tempfile
import json
import time
import os
import requests
import httpie
import jwt
import sys


__version__ = '0.9'
__author__ = 'Alon Horowitz'
__licence__ = 'Apache 2.0'


class NsofAuth(object):
    def __init__(self, org, username, password):
        self.org = org
        self.username = username
        self.password = password
        self.eorg = os.getenv('EORG', org)
        self.verbose = bool(os.getenv('VERBOSE', False))

    def __call__(self, r):
        host_url = self._get_host_url(r)
        access_token = self._load_token_if_valid('access_token', host_url)
        if not access_token:
            tokens = self._refresh_authentication(host_url)
            if not tokens:
                tokens = self._authenticate(host_url)
            if tokens:
                access_token = tokens['access_token']
                self._store_token('access_token',
                                  host_url,
                                  access_token,
                                  store_eorg=True)
                if 'refresh_token' in tokens:
                    self._store_token('refresh_token',
                                      host_url,
                                      tokens['refresh_token'])
        if access_token:
            r.headers['Authorization'] = 'Bearer %s' % access_token
        return r

    def _refresh_authentication(self, host_url):
        refresh_token = self._load_token_if_valid('refresh_token', host_url)
        if not refresh_token:
            return None
        request_data = {"grant_type": "refresh_token",
                        "refresh_token": refresh_token}
        return self._request_token(host_url, request_data)

    def _authenticate(self, host_url):
        request_data = {"grant_type": "password",
                        "username": self.username,
                        "password": self.password}
        return self._request_token(host_url, request_data)

    def _is_auth_endpoint_exists(self, host_url):
        url = self._get_auth_url(host_url)
        response = requests.options(url=url)
        return response.status_code == 200

    def _request_token(self, host_url, request_data):
        if not self._is_auth_endpoint_exists(host_url):
            return None
        if self.eorg != self.org:
            request_data['scope'] = "org:%s" % self.eorg
        url = self._get_auth_url(host_url)
        msg = "httpie-nsof: [%s] %s body=%s" % (self.eorg, url, request_data)
        self._vprint(msg)
        response = requests.post(url=url, json=request_data)
        response.raise_for_status()
        return response.json()

    def _get_host_url(self, r):
        parsed_url = urlparse.urlparse(r.url)
        netloc_no_port = parsed_url.netloc.split(':')[0]
        if parsed_url.scheme:
            return "%s://%s" % (parsed_url.scheme, netloc_no_port)
        return netloc_no_port

    def _get_auth_url(self, host_url):
        return "%s/v1/%s/oauth/token" % (host_url, self.org)

    def _load_token_if_valid(self, name, host_url):
        path = self._get_token_path(name)
        try:
            with open(path) as f:
                token_info = json.load(f)
        except:
            return None
        if token_info['host_url'] != host_url:
            return None
        if token_info.get('eorg', self.eorg) != self.eorg:
            return None
        payload = jwt.decode(token_info['token'], verify=False)
        if time.time() > (payload['exp'] - 30):
            return None
        return token_info['token']

    def _store_token(self, name, host_url, token, store_eorg=False):
        path = self._get_token_path(name)
        token_info = {'token': token, 'host_url': host_url}
        if store_eorg:
            token_info['eorg'] = self.eorg
        with open(path, 'w') as f:
            json.dump(token_info, f)

    def _get_token_path(self, name):
        tmpdir = tempfile.gettempdir()
        return os.path.join(tmpdir, "httpie-nsof.%s" % name)

    def _vprint(self, msg):
        if self.verbose:
            print msg


class NsofAuthPlugin(httpie.plugins.AuthPlugin):
    name = 'Nsof OAuth 2'
    auth_type = 'nsof'
    description = ''
    auth_require = False

    def get_auth(self, username=None, password=None):
        if username is None:
            org = os.getenv("HTTPIE_NSOF_ORG")
            username = os.getenv("HTTPIE_NSOF_USERNAME")
        else:
            if '/' not in username:
                print >> sys.stderr, "httpie-nsof error: wrong username format"
                sys.exit(httpie.ExitStatus.PLUGIN_ERROR)
            org, username = username.split("/")
        password = password or os.getenv("HTTPIE_NSOF_PASSWORD")
        self._verify_input(org=org, username=username, password=password)
        return NsofAuth(org, username, password)

    def _verify_input(self, **input_params):
        missing = [k for k, v in input_params.iteritems() if not v]
        if missing:
            msg = "httpie-nsof error: missing %s" % ', '.join(missing)
            print >> sys.stderr, msg
            sys.exit(httpie.ExitStatus.PLUGIN_ERROR)
