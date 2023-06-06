#!/usr/bin/env python3
"""On this file **(common/spotify.py)** you will find the description of
 useful functions to interact with Spotify Web site.

"""

from http import cookies
from bs4 import BeautifulSoup
import requests
import json
import config as cfg
import logging

GET_CSRF_URL = cfg.GET_CSRF_URL
LOGIN_URL = cfg.LOGIN_URL
FAMILY_GET_PLAN = cfg.FAMILY_GET_PLAN
OVERVIEW_URL = cfg.OVERVIEW_URL
PROXIES = cfg.PROXIES
HTTP_HEADERS = cfg.HTTP_HEADERS
CHECK_PROXY_URL = cfg.CHECK_PROXY_URL
PROFILE_URL = cfg.PROFILE_URL
FAMILY_PLAN_MAX = cfg.FAMILY_PLAN_MAX
INVITE_BY_EMAIL = cfg.INVITE_BY_EMAIL
CONFIRM_INVITATION_URL = cfg.CONFIRM_INVITATION_URL
ACCEPT_INVITATION_URL = cfg.ACCEPT_INVITATION_URL
CANCEL_INVITATION_URL = cfg.CANCEL_INVITATION_URL
DELETE_MEMBER_URL = cfg.DELETE_MEMBER_URL
PLAN_MEMBER_URL = cfg.PLAN_MEMBER_URL
SUBSCRIPTION_URL_CHANGE = cfg.SUBSCRIPTION_URL_CHANGE

def check_proxy_availability(url, proxy):
    """Test if an http address can be reached using a specified proxy

    :param url: URL address to check if it can reached through specified proxy.
    :param proxy: Proxy params to configure test.
    :return: False or the response of the request
    :raise: RequestException
    """

    try:
        c_sess = requests.Session()
        client_response = c_sess.get(url, headers=HTTP_HEADERS, proxies=proxy)
        response = client_response.status_code == 200
        return response
    except requests.exceptions.RequestException:
        return False


def get_available_proxy():
    """Returns the configuration of an available proxy.

    :return: Dictionary with proxy configurations
    """

    proxy_params = ['http', 'https', 'HTTP', 'HTTPS']
    for proxy_conf in PROXIES:
        proxy = {}
        for k in proxy_params:
            if k in proxy_conf:
                proxy[k.lower()] = proxy_conf[k]
        if check_proxy_availability(CHECK_PROXY_URL, proxy):
            return proxy
    return {}


def get_csrf_login(c_sess):
    """Return a valid csrf value for a request to login.

    :param c_sess: Active session
    :return: String
    :raise: ValueError
    """

    cj = requests.cookies.RequestsCookieJar()
    c = cookies.SimpleCookie()
    c['__bon'] = 'MHwwfC0xNDAxNTMwNDkzfC01ODg2NDI4MDcwNnwxfDF8MXwx='
    c['__bon']['path'] = '/'
    c['__bon']['domain'] = 'accounts.spotify.com'
    cj.update(c)
    c_sess.cookies = cj
    header = {}
    header["Host"] = "accounts.spotify.com"
    header["Connection"] = "keep-alive"
    header["User-Agent"] = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729"
    header["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
    try:
        request_response = c_sess.get(GET_CSRF_URL, verify=True,
                                       headers=header,
                                       proxies=get_available_proxy())
    except requests.exceptions.RequestException:
        raise ValueError({
            'message': "Invalid response. Get CSRF token.",
            'type': 'http',
            'data': {
                'url': GET_CSRF_URL,
                'http_code': 'unknown'
            },
        })

    if request_response and request_response.status_code == 200:
        head = request_response.headers['Set-Cookie'].split(';')[0].split('=')
        return head[1]
    else:
        raise ValueError({
            'message': "Invalid Response. Get CSRF token.",
            'type': 'http',
            'data': {
                'url': GET_CSRF_URL,
                'http_code': request_response.status_code,
            }
        })

def upgrade_account_family_2(c_sess):
    account_profile_data = get_account_profile(c_sess)
    if account_profile_data['premium'] is True and account_profile_data['can_invite'] is True and ((5 - len(account_profile_data['members']) - len(account_profile_data['invites'])) != 5) or account_profile_data['available_spots'] == 5:
        raise ValueError({
            'message': "This account is already family owner",
            'type': 'logic',
            'data': {
                'data': account_profile_data['email']
            },
        })
    if account_profile_data['premium'] is True and account_profile_data['available_spots'] == 5 and account_profile_data['can_invite'] is False:
            raise ValueError({
         'message': "This account belongs to a family plan",
         'data': {
               'data': account_profile_data['email']
         },
         })
    if account_profile_data['premium'] is False:
        raise ValueError({
            'message': "This is a none premium account",
            'data': {
                'data': account_profile_data['email']
            },
        })
    head = HTTP_HEADERS
    head['Referer'] = 'https://www.spotify.com/us/account/subscription/change/'
    try:
        request_response = c_sess.get(SUBSCRIPTION_URL_CHANGE, verify=True,
                                     headers=head,
                                      proxies=get_available_proxy())
    except requests.exceptions.RequestException:
        raise ValueError({
            'message': "Page get subscription change."
        })
    if request_response.status_code != 200:
        raise ValueError({
            'message': "Invalid response get subscription change.",
        })
    soup = BeautifulSoup(request_response.text, 'html.parser')
    details = ''
    details_d = soup.find('div', {'class': 'switch-subscriptions-details'})
    if details_d:
       details = details_d.getText()   
    if 'If you confirm, your plan will change immediately.' not in details: return "Failed"
    if soup.findAll('form')[0]:
       LINK = CHECK_PROXY_URL + soup.findAll('form')[0].get('action')
          
    post_request = c_sess.post(LINK, verify=True,
                     headers=head,
                     proxies=get_available_proxy())
    if post_request.status_code != 200:
         raise ValueError({
            'message': "Invalid response. Get Subscription Change.",
            'type': 'http',
            'data': {
                  'url': LINK,
                  'http_code': post_request.status_code,
                  'text': post_request.text
            },
         })
    return "Success"
def do_login(c_sess, username, password):
    """Perform a login action on the Spotify site.

    :param c_sess: Active Session
    :param username: Spotify username
    :param password: Spotify password
    :return: True
    :raise: ValueError
    """

    csrf = get_csrf_login(c_sess)

    login_data = {'remember': 'true', 'username': username, 'csrf_token': csrf,
                  'password': password}
    header=HTTP_HEADERS
    header["Host"] = "accounts.spotify.com"
    header["Content-Type"] = "application/x-www-form-urlencoded"
    
    try:
        response_post = c_sess.post(LOGIN_URL, verify=True, headers=header,
                                    proxies=get_available_proxy(),
                                    data=login_data)
    except requests.exceptions.RequestException:
        raise ValueError({
            'message': "Request User Login",
            'type': 'http',
            'data': {
                'username': username,
                'url': LOGIN_URL,
                'http_code': 'unknown'
            },
        })

    if response_post.status_code == 200:
        response = json.loads(response_post.text)
        if response["displayName"]:
            return True
        else:
            raise ValueError({
                'message': "Success Login Response "
                           "without 'displayName' property.",
                'type': 'http',
                'data': {
                    'username': username,
                    'url': LOGIN_URL,
                    'http_code': 'unknown'
                },
            })
    else:
        response_text = json.loads(response_post.text)

        if response_text['error'] and response_text['error'] == \
                'errorInvalidCredentials':
            raise ValueError({
                'message': "Invalid Credentials",
                'type': 'auth',
                'data': {
                    'data': {
                        'username': username,
                    }
                },
            })
        else:
            raise ValueError({
                'message': "Unknown response from login request.",
                'type': 'http',
                'data': {
                    'url': LOGIN_URL,
                    'http_code': response_post.status_code,
                    'text': response_post.text
                },
            })


def get_account_profile(c_sess):
    """Returns the data of the spotify account of the specified session.

    :param c_sess: Active Spotify session
    :return: Dictionary
    :raise: ValueError
    """
    header = HTTP_HEADERS
    header["Host"] = "www.spotify.com"
    header["Referer"] = "https://accounts.spotify.com/en-US/login?continue=https:%2F%2Fwww.spotify.com%2Fde%2Faccount%2Foverview%2F"
    try:
        request_response = c_sess.get(OVERVIEW_URL, verify=True,
                                      headers=header,
                                      proxies=get_available_proxy())
    except requests.exceptions.RequestException:
        raise ValueError({
            'message': "Request Page Account Profile",
            'type': 'http',
            'data': {
                'url': OVERVIEW_URL,
                'http_code': 'unknown',
                'text': ''
            },
        })
    if request_response.status_code != 200:
        raise ValueError({
            'message': "Request Page Account Profile",
            'type': 'http',
            'data': {
                'url': OVERVIEW_URL,
                'http_code': request_response.status_code,
                'text': request_response.text
            },
        })

    soup = BeautifulSoup(request_response.text, 'html.parser')
    premium = ''
    premium_d = soup.findAll('h3', {'class': 'product-name'})

    if premium_d: 
       premium = premium_d[0].getText()
    else:
       premium_d = soup.findAll('div', attrs={'class': 'well card subscription'})
       for a in premium_d:
           premium = a.h3.text
           break
    country = ''
    country_d = soup.find('p', {'id': 'card-profile-country'})
    if country_d:
        country = country_d.getText()

    members = []
    invites = []
    username = ''
    full_name = ''
    can_invite = False
    is_premium = False
    email = 0
    available_spots = 0
    email_d = soup.find('p', {'id': 'card-profile-email'})
    if email_d:
        email = email_d.getText()
    if premium == 'Premium for Family':
        is_premium = True
        result_operation = get_family_plan(c_sess)
        members = result_operation['members']
        invites = result_operation['invites']
        username = result_operation['username']
        full_name = result_operation['full_name']
        can_invite = result_operation['can_invite']
        available_spots = FAMILY_PLAN_MAX - len(members) - len(invites)
    if premium == 'Spotify Premium':
        is_premium = True
    if premium == 'Premium for Students':
        is_premium = True
    if premium == 'Premium paused':
        is_premium = False
    return {
        'premium': is_premium,
        'members': members,
        'invites': invites,
        'available_spots': available_spots,
        'can_invite': can_invite,
        'username': username,
        'full_name': full_name,
        'country': country,
        'email': email,
        'csrf': request_response.headers['X-Csrf-Token']
    }


def get_profile(c_sess):
    """Returns the information of the user of the active session
    from the form: 'Edit Profile'

    :param c_sess: Active Spotify session
    :return: Dictionary
    :raise: ValueError
    """
    header=HTTP_HEADERS
    header["Host"] = "www.spotify.com"
    header["Referer"] = "https://www.spotify.com/us/account/overview/"
    try:
        request_response = c_sess.get(PROFILE_URL, verify=True,
                                      headers=header,
                                      proxies=get_available_proxy())
    except requests.exceptions.RequestException:
        raise ValueError({
            'message': "Request Page Account Profile.",
            'type': 'http',
            'data': {
                'url': PROFILE_URL,
                'http_code': 'unknown',
                'text': ''
            },
        })

    if request_response.status_code != 200:
        raise ValueError({
            'message': "Request Page Account",
            'type': 'http',
            'data': {
                'url': PROFILE_URL,
                'http_code': request_response.status_code,
                'text': request_response.text
            },
        })
    soup = BeautifulSoup(request_response.text, 'html.parser')
    email = ''

    email_d = soup.find("input", {"id": "profile_email"})
    if email_d:
       email= email_d.get('value', '')
    
    postal_code = ''
    postal_code_d = soup.find("input", {"id": "profile_postalCode"})
    if postal_code_d:
       postal_code = postal_code_d.get('value')

    gender = ''
    gender_d = soup.find("select", {"id": "profile_gender"})
    if gender_d:
        gender = gender_d.find('option', {'selected': True}).get('value')

    birth_m = ''
    birth_m_d = soup.find("select", {
        "id": "profile_birthdate_month"})
    if birth_m_d:
        birth_m = birth_m_d.find('option', {'selected': True}).get('value')

    birth_d = ''
    birth_d_d = soup.find("select", {"id": "profile_birthdate_day"}
                          )
    if birth_d_d:
        birth_d = birth_d_d.find('option', {'selected': True}).get('value')

    birth_y = ''
    birth_y_d = soup.find("select", {"id": "profile_birthdate_year"}
                          )
    if birth_y_d:
        birth_y = birth_y_d.find('option', {'selected': True}).get('value')

    country = ''
    country_d = soup.find("select", {"id": "profile_country"}
                          )
    if country_d:
        country = country_d.find('option', {'selected': True}).get('value')

    phone_mobile = soup.find("input", {"id": "profile_mobile_number"}
                             ).get('value')

    p_mob_br = ''
    p_mob_br_d = soup.find("select", {"id": "profile_mobile_brand"}
                           ).find('option', {'selected': True})

    if p_mob_br_d:
        p_mob_br = p_mob_br_d.get('value')

    p_mob_pr = ''
    p_mob_pr_d = soup.find("select", {"id": "profile_mobile_provider"}
                           ).find('option', {'selected': True})
    if p_mob_pr_d:
        p_mob_pr = p_mob_pr_d.get('value')

    third_party_email = soup.find("input",
                                  {"id": "profile_send_third_party_email"}
                                  ).get('value')

    token = soup.find("input", {"id": "profile__token"}).get('value')

    return {'profile[email]': email,
            'profile[postalCode]': postal_code,
            'profile[gender]': gender,
            'profile[birthdate][month]': birth_m,
            'profile[birthdate][day]': birth_d,
            'profile[birthdate][year]': birth_y,
            'profile[country]': country,
            'profile[mobile][number]': phone_mobile,
            'profile[mobile][brand]': p_mob_br,
            'profile[mobile][provider]': p_mob_pr,
            "profile[_token]": token,
            "profile[send][third_party_email]": third_party_email}


def get_family_plan(c_sess):
    """Return information about Premium Family Plan

    :param c_sess: Active Spotify session
    :return: Dictionary
    :raise: ValueError
    """

    try:
        request_response = c_sess.get(FAMILY_GET_PLAN, verify=True,
                                      headers=HTTP_HEADERS,
                                      proxies=get_available_proxy())
    except requests.exceptions.RequestException:
        raise ValueError({
            'message': "Request Family Plan.",
            'type': 'http',
            'data': {
                'url': FAMILY_GET_PLAN,
                'http_code': 'unknown',
                'text': ''
            },
        })

    if request_response.status_code != 200:
        raise ValueError({
            'message': "Request Family Plan",
            'type': 'http',
            'data': {
                'url': FAMILY_GET_PLAN,
                'http_code': request_response.status_code,
                'text': ''
            },
        })

    data = json.loads(request_response.text)

    members = []
    invites = []
    username = data['data']['currentUser']['username']
    full_name = data['data']['currentUser']['fullName']
    can_invite = data['data']['currentUser']['canInvite']
    is_master = data['data']['currentUser']['isMaster']
    if is_master and data['data']['members']:
        for member in data['data']['members']:
            members.append({
                'username': member['username'],
                'email': member['email'],
                'full_name': member['fullName'],
                'membershipUuid': member['membershipUuid'],
            })
    if is_master and data['data']['invites']:
        for inv in data['data']['invites']:
            invites.append({
                'last_name': inv['lastName'],
                'token': inv['token'],
                'email': inv['email'],
                'redeem_Link': inv['redeemLink'],
                'first_name': inv['firstName'],
            })
    return {'can_invite': can_invite,
            'username': username,
            'full_name': full_name,
            'members': members,
            'invites': invites}


def confirm_invitation(c_sess, i_data):
    """Confirm an invitation for a premium family plan.

    :param c_sess: Spotify Active Session (Member User)
    :param i_data: Data to confirm invitation
    :return: Bool
    :raise: ValueError
    """

    account_profile_data = get_account_profile(c_sess)
    if account_profile_data['premium'] is True:
        raise ValueError({
            'message': "Confirm Invitation. This is a Premium Account",
            'type': 'logic',
            'data': {
                'data': i_data
            },
        })
    head = HTTP_HEADERS
    confirm_url = CONFIRM_INVITATION_URL + i_data['token']
    try:
        request_response = c_sess.get(confirm_url, verify=True,
                                      headers=head,
                                      proxies=get_available_proxy())
    except requests.exceptions.RequestException:
        raise ValueError({
            'message': "Request Page. Get CSRF token",
            'type': 'http',
            'data': {
                'url': confirm_url,
                'http_code': 'unknown',
                'text': ''
            },
        })

    csrf_invitation = request_response.headers['X-Csrf-Token']
    head['x-csrf-token'] = csrf_invitation
    head["Host"] = "www.spotify.com"
    head["Origin"] = "https://www.spotify.com"
    head["Referer"] = confirm_url
    try:
        post_response = c_sess.post(ACCEPT_INVITATION_URL, verify=True,
                                    headers=head, data=json.dumps(i_data),
                                    proxies=get_available_proxy())

    except requests.exceptions.RequestException:
        raise ValueError({
            'message': "Request to Confirm Invitation",
            'type': 'http',
            'data': {
                'url': ACCEPT_INVITATION_URL,
                'http_code': 'unknown',
                'text': ''
            },
        })

    if post_response.status_code != 200:
        raise ValueError({
            'message': "Invalid response. Confirm Invitation.",
            'type': 'http',
            'data': {
                'url': ACCEPT_INVITATION_URL,
                'http_code': post_response.status_code,
                'text': post_response.text
            },
        })

    i_data = json.loads(post_response.text)
    if i_data['success'] is True:
        return True
    else:
        raise ValueError({
            'message': "Invalid response. Confirm Invitation",
            'type': 'http',
            'data': {
                'url': INVITE_BY_EMAIL,
                'http_code': post_response.status_code,
                'text': post_response.text,
            },
        })


def create_invitation(c_sess, i_data):
    """Create an invitation and return the token generated by Spotify

    :param c_sess: Spotify active session
    :param i_data: Data to confirm invitation
    :return: String
    :raise: ValueError
    """

    try:
        account_profile_data = get_account_profile(c_sess)

        if account_profile_data['premium'] is False:
            raise ValueError({
                'message': "Create Invitation. Premium account Required",
                'type': 'logic',
                'data': {
                    'data': i_data
                },
            })

        # check if is member
        if account_profile_data['members']:
            for mem in account_profile_data['members']:
                if mem['email'] == i_data['email']:
                    raise ValueError({
                        'message': "This account is already a member of a plan",
                        'type': 'logic',
                        'data': {
                            'data': i_data
                        },
                    })

        # Check if invitation exists
        if account_profile_data['invites']:
            for inv in account_profile_data['invites']:
                if inv['email'] == i_data['email']:
                    return inv['token']

        csrf = account_profile_data['csrf']
        head = HTTP_HEADERS
        head['x-csrf-token'] = csrf

        post_response = c_sess.post(INVITE_BY_EMAIL, verify=True,
                                    headers=head, data=json.dumps(i_data),
                                    proxies=get_available_proxy())
    except requests.exceptions.RequestException:
        raise ValueError({
            'message': "Request to Create Invitation.",
            'type': 'http',
            'data': {
                'url': INVITE_BY_EMAIL,
                'http_code': 'unknown',
                'text': '',
                'data': i_data
            },
        })

    if post_response.status_code != 200:
        raise ValueError({
            'message': "Invalid response. Create Invitation.",
            'type': 'http',
            'data': {
                'url': INVITE_BY_EMAIL,
                'http_code': post_response.status_code,
                'text': post_response.text,
                'data': {}
            },
        })

    i_data = json.loads(post_response.text)
    if i_data["success"] is True:
        return i_data['token']
    else:
        raise ValueError({
            'message': "Invalid response. Create Invitation.",
            'type': 'http',
            'data': {
                'url': INVITE_BY_EMAIL,
                'http_code': post_response.status_code,
                'text': post_response.text,
                'data': {}
            },
        })


def cancel_invitation(c_sess, token):
    """Cancel an invitation to belong to a premium family plan

    :param c_sess: Spotify active session
    :param token: Token to cancel invitation
    :return: Bool
    :raise: ValueError
    """

    account_profile_data = get_account_profile(c_sess)

    if account_profile_data['premium'] is False:
        raise ValueError({
            'message': "Cancel Invitation. Premium account Required.",
            'type': 'logic',
            'data': {
                'data': {
                    'token': token
                }
            },
        })

    try:
        request_response = c_sess.get(OVERVIEW_URL, verify=True,
                                      headers=HTTP_HEADERS,
                                      proxies=get_available_proxy())
    except requests.exceptions.RequestException:
        raise ValueError({
            'message': "Request Page to Cancel Invitation",
            'type': 'http',
            'data': {
                'url': OVERVIEW_URL,
                'http_code': 'unknown',
                'data': {
                    'token': token
                }
            },
        })

    csrf_cancel_invitation = request_response.headers['X-Csrf-Token']
    head = HTTP_HEADERS
    head['x-csrf-token'] = csrf_cancel_invitation
    try:
        post_response = c_sess.post(CANCEL_INVITATION_URL, verify=True,
                                    headers=head,
                                    data=json.dumps({'token': token}),
                                    proxies=get_available_proxy())
    except requests.exceptions.RequestException:
        raise ValueError({
            'message': "Request to Cancel Invitation.",
            'type': 'http',
            'data': {
                'url': CANCEL_INVITATION_URL,
                'http_code': 'unknown',
                'data': {
                    'token': token,
                    'data': post_response.text
                }
            },
        })
    if post_response.status_code != 200:
        raise ValueError({
            'message': "Invalid response. Cancel Invitation.",
            'type': 'http',
            'data': {
                'url': CANCEL_INVITATION_URL,
                'http_code': post_response.status_code,
                'data': {
                    'token': token,
                    'data': post_response.text
                }
            },
        })

    response_text = json.loads(post_response.text)
    if response_text['success']:
        return True
    else:
        raise ValueError({
            'message': "Invalid response. Cancel Invitation.",
            'type': 'http',
            'data': {
                'url': CANCEL_INVITATION_URL,
                'http_code': post_response.status_code,
                'data': {
                    'data': post_response.text
                }
            },
        })


def update_profile(c_sess, data):
    """Update a user's profile

    :param c_sess: Spotify active session
    :param data: Data to update
    :return: Bool
    :raise: ValueError
    """

    form_data = get_profile(c_sess)
    data_now = form_data

    if form_data:
        for d in data:
            if d in form_data:
                form_data[d] = data[d]
        try:
            post_response = c_sess.post(PROFILE_URL, verify=True,
                                        headers=HTTP_HEADERS, data=form_data,
                                        proxies=get_available_proxy())
        except requests.exceptions.RequestException:
            raise ValueError({
                'message': "Request Update Profile.",
                'type': 'http',
                'data': {
                    'url': PROFILE_URL,
                    'http_code': 'unknown',
                    'data': form_data
                },
            })

        if post_response.status_code != 200:
            raise ValueError({
                'message': "Invalid Response. Update Profile.",
                'type': 'http',
                'data': {
                    'url': PROFILE_URL,
                    'http_code': post_response.status_code,
                    'data': {
                        'form_data': form_data,
                        'response': post_response.text
                    }
                },
            })

        data_now['profile[_token]'] = ''
        form_data['profile[_token]'] = ''
        items = set(data_now.items()) & set(form_data.items())
        if len(items) == len(data_now):
            return True
        else:
            raise ValueError({
                'message': "Update Profile",
                'type': 'http',
                'data': {
                    'url': PROFILE_URL,
                    'http_code': post_response.status_code,
                    'text': post_response.text,
                    'data': {
                        'form_data': form_data,
                        'response': post_response.text
                    }
                },
            })


def delete_member(c_sess, uuid):
    """Remove a member of a premium family plan

    :param c_sess: Spotify active session
    :param uuid: UUID of the member to remove
    :return: Bool
    :raise: ValueError
    """

    account_profile_data = get_account_profile(c_sess)

    if account_profile_data['premium'] is False:
        raise ValueError({
            'message': "Delete Member. Premium account Required",
            'type': 'logic',
            'data': {
                'data': {
                    'uuid': uuid
                }
            },
        })

    delete_member_url = PLAN_MEMBER_URL + uuid
    try:
        request_response = c_sess.get(delete_member_url, verify=True,
                                      headers=HTTP_HEADERS,
                                      proxies=get_available_proxy())
    except requests.exceptions.RequestException:
        raise ValueError({
            'message': "Request Page of Plan Member",
            'type': 'http',
            'data': {
                'url': DELETE_MEMBER_URL,
                'http_code': 'unknown',
                'data': {}
            },
        })

    csrf_remove_member = request_response.headers['X-Csrf-Token']
    head = HTTP_HEADERS
    head['x-csrf-token'] = csrf_remove_member
    try:
        post_response = c_sess.post(DELETE_MEMBER_URL, verify=True,
                                    headers=head,
                                    data=json.dumps({'membershipUuid': uuid}),
                                    proxies=get_available_proxy())
    except requests.exceptions.RequestException:
        raise ValueError({
            'message': "Request to Remove Member",
            'type': 'http',
            'data': {
                'url': DELETE_MEMBER_URL,
                'http_code': 'unknown',
                'text': '',
                'data': {
                    'membershipUuid': uuid
                }
            },
        })

    if post_response.status_code != 200:
            raise ValueError({
                'message': "Invalid response. Remove member.",
                'type': 'http',
                'data': {
                    'url': DELETE_MEMBER_URL,
                    'http_code': post_response.status_code,
                    'data': {
                        'data': post_response.text,
                        'membershipUuid': uuid
                    }
                },
            })

    response_text = json.loads(post_response.text)
    if response_text['success'] is True:
        return True
    else:
        if response_text['failure']['error_code'] == 303:
            raise ValueError({
                'message': "No matching account found",
                'type': 'http',
                'data': {
                    'url': DELETE_MEMBER_URL,
                    'http_code': post_response.status_code,
                    'data': {
                        'data': post_response.text,
                        'membershipUuid': uuid
                    }
                },
            })
        else:
            raise ValueError({
                'message': "Invalid response. Remove member.",
                'type': 'http',
                'data': {
                    'url': DELETE_MEMBER_URL,
                    'http_code': post_response.status_code,
                    'text': post_response.text,
                    'data': {
                        'membershipUuid': uuid
                    }
                },
            })
