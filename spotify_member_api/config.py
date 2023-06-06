#!/usr/bin/env python
"""This file **(config.py)** contains the settings of the application

**Application Run Port**::

    APP_PORT = 5002

**Application Proxies**::

    PROXIES = [
        {
            'name': 'Proxy Name 1',
            'http': 'socks5://user:password@server:port',
            'https': 'socks5://user:password@server:port',
        },
        {
            'name': 'Proxy Name 2',
            'http': 'http://user:password@server:port',
            'https': 'http://user:password@server:port',
        },
    ]
    
.. note::
    Proxies are used in the order they appear while giving a 
    correct answer in a GET request to the address specified in the 
    configuration parameter: **CHECK_PROXY_URL**

**URL to Check Proxy Availability**::

    CHECK_PROXY_URL = 'https://www.spotify.com'

**HTTP Headers**::

    HTTP_HEADERS = {"Accept": "text/html,application/xhtml+xml,"
                          "application/xml;q=0.9,image/webp,image/apng,"
                          "*/*;q=0.8",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/59.0.3071.115 Safari/537.36",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "DNT": "1"}

"""

APP_PORT = 5002

PROXIES = [

]

FAMILY_PLAN_MAX = 5
CHECK_PROXY_URL = 'https://www.spotify.com'
PLAN_MEMBER_URL = 'https://www.spotify.com/us/family/member/'
GET_CSRF_URL = 'https://accounts.spotify.com/en/login?continue=https:%2F%2Fwww.spotify.com%2Fint%2Faccount%2Foverview%2F'
LOGIN_URL = 'https://accounts.spotify.com/api/login'
FAMILY_GET_PLAN = 'https://www.spotify.com/us/family/api/get-family-plan/'
OVERVIEW_URL = 'https://www.spotify.com/us/account/overview/'
PROFILE_URL = 'https://www.spotify.com/us/account/profile/'
INVITE_BY_EMAIL = 'https://www.spotify.com/us/family/api/' \
                  'master-invite-by-email/'
CONFIRM_INVITATION_URL = 'https://www.spotify.com/us/family/redeem/?token='
ACCEPT_INVITATION_URL = 'https://www.spotify.com/us/family/api/member-join/'
CANCEL_INVITATION_URL = 'https://www.spotify.com/us/family/api/' \
                        'master-cancel-invite/'
DELETE_MEMBER_URL = 'https://www.spotify.com/us/family/api/' \
                    'master-remove-member/'
SUBSCRIPTION_URL_CHANGE = 'https://www.spotify.com/us/account/subscription/change/intent/?target=familyplan'
SET_ADDRESS = 'https://www.spotify.com/us/family/api/' \
               'master-set-address/'

HTTP_HEADERS = {"Accept": "text/html,application/xhtml+xml,"
                          "application/xml;q=0.9,image/webp,image/apng,"
                          "*/*;q=0.8",
                "User-Agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "DNT": "1"}
