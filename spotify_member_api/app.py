#!/usr/bin/env python3

"""On this file **(app.py)** you will find the description of the resources that
expose the API

"""

import common.spotify as spotify
from flask_restful import reqparse
import requests
from flask import Flask
from flask_restplus import Api
from flask_restplus import Resource
from flask_restplus import fields
import config as cfg

app = Flask(__name__)

api = Api(app, version='1.0', title='Spotify Family Plan API',
          description='Spotify Family Plan API')

error_model = api.model('ErrorData', {
    'url': fields.String(required=True, description='URL'),
    'http_code': fields.String(required=True, description='HTTP code'),
    'data': fields.Raw()
})

response_error = api.model('Error', {
    'message': fields.String(required=True, description='Message'),
    'type': fields.String(required=True,
                          description='Type', enum=['http', 'auth', 'logic']),
    'data': fields.Nested(error_model)
})

response_family_member = api.model('FamilyMember', {
    'membershipUuid': fields.String(required=True,
                                    description='Membership UUID'),
    'email': fields.String (required=True, description='Email'),
    'username': fields.String (required=True, description='Username'),
    'full_name': fields.String (required=True, description='Full Name')
})

response_family_invite = api.model('FamilyInvite', {
    'last_name': fields.String(required=True, description='Last Name'),
    'token': fields.String(required=True, description='Token'),
    'email': fields.String(required=True, description='Email'),
    'redeem_Link': fields.String(required=True,
                                 description='Link to accept invitation'),
    'first_name': fields.String(required=True, description='First Name'),
})

response_family_plan = api.model('ResponseFamilyPlan', {
    'country': fields.String(required=True, description='Country'),
    'can_invite': fields.Boolean(required=True, description='Can invite'),
    'username': fields.String(required=True, description='Spotify username'),
    'full_name': fields.String(required=True,
                               description='Spotify full name'),
    'premium': fields.Boolean(required=True,
                              description='Is premium account'),
    'available_spots': fields.Integer(required=True,
                                      description='Available spots'),
    'email': fields.String(required=True, description='Email'),
    'members': fields.List(fields.Nested(response_family_member)),
    'invites': fields.List(fields.Nested(response_family_invite))
})

address_model = api.model('Address', {
    'line1': fields.String(required=True, description='Line 1'),
    'line2': fields.String(required=True, description='Line 2'),
    'postalCode': fields.String(required=True, description='Postal Code'),
    'city': fields.String(required=True, description='City'),
    'partnerCheck': fields.String(required=True, description='Partner Check',
                                  default=''),
})

create_member_resource_fields = api.model('CreateMemberResource', {
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Password'),
    'country': fields.String(required=False, description='Set country'
                                                         ' to member account'),
    'address': fields.Nested(address_model)
})

@api.route('/upgrade/<username>:<password>')
@api.doc(params={'password': 'Spotify account password'})
@api.doc(params={'username': 'Spotify account username'})
class FamilyMember(Resource):
    """

    Resource with specific actions on a member of the spotify premium plan.

    """
    @api.doc(responses={200: 'Member Upgraded'})
    @api.response(400, 'Failed', response_error)
    def get(self, username, password):
        try:
            session = requests.Session()
            spotify.do_login(session, username, password)
            d = spotify.upgrade_account_family_2(session)
        except ValueError as e:
            return {'errors': e.args}, 400
        return d
@api.route('/family/<username>:<password>/<uuid>')
@api.doc(params={'password': 'Spotify account password'})
@api.doc(params={'username': 'Spotify account username'})
@api.doc(params={'uuid': 'UUID of the member to remove'})
class FamilyMember(Resource):
    """

    Resource with specific actions on a member of the spotify premium plan.

    """
    @api.doc(responses={204: 'Member Removed'})
    @api.response(400, 'Failed', response_error)
    def delete(self, username, password, uuid):
        """Function to remove a member from Spotify Premium Plan

        Example of Request::

            Method: DELETE
            URL: /family/{username}:{password}/{uuid}

        :param username: Username of the Spotify premium account to
         which the member user belongs.
        :param password: Password of the Spotify premium account to
         which the member user belongs.
        :param uuid: User identifier of the Spotify premium plan
        :return: If the operation is correct: HTTP Code Status: 204 and the
         body of the answer without content. If an error occurs: HTTP Code
         Status 400 and the body of response with data (JSON) about the error.

         Example of Successful Response::

            Http Code: 204 and No Content

         Example of Error Response::

             Http Code: 400 and JSON Content:
             {
                  "data": {
                    "http_code": "string",
                    "data": {},
                    "url": "string"
                  },
                  "message": "string",
                  "type": "http"
             }

        """
        try:
            session = requests.Session()
            spotify.do_login(session, username, password)
            spotify.delete_member(session, uuid)
        except ValueError as e:
            return {'errors': e.args}, 400
        return [], 204


@api.route('/family/<username>:<password>')
@api.doc(params={'password': 'Spotify account username'})
@api.doc(params={'username': 'Spotify account username'})
class FamilyPlan(Resource):
    """

    Resource with specific actions on a premium family plan.

    """
    @api.response(200, 'Success', response_family_plan)
    @api.response(400, 'Failed', response_error)
    def get(self, username, password):
        """Function to get information about a Spotify user account.

        Example of Request::

            Method: GET
            URL: /family/{username}:{password}

        :param username: Username of the Spotify account
        :param password: Password of the Spotify account
        :return: If the operation is correct: HTTP Code Status: 200 and the
         body of the answer in JSON format. If an error occurs: HTTP Code
         Status 400 and the body of response with data (JSON) about the error.

         Example of Successful Response::

            Http Code: 200 and JSON Content:
            {
              "can_invite": true,
              "invites": [
                {
                  "token": "string",
                  "first_name": "string",
                  "redeem_Link": "string",
                  "last_name": "string",
                  "email": "string"
                }
              ],
              "full_name": "string",
              "email": "string",
              "premium": true,
              "available_spots": 0,
              "username": "string",
              "country": "string",
              "members": [
                {
                  "email": "string",
                  "username": "string",
                  "full_name": "string",
                  "membershipUuid": "string"
                }
              ]
            }

         Example of Error Response::

             Http Code: 400 and JSON Content:
             {
                  "data": {
                    "http_code": "string",
                    "data": {},
                    "url": "string"
                  },
                  "message": "string",
                  "type": "http"
             }

        """
        try:
            session = requests.Session()
            spotify.do_login(session, username, password)
            account_data = spotify.get_account_profile(session)
        except ValueError as e:
            return {'errors': e.args}, 400
        if 'csrf' in account_data:
            account_data.pop('csrf', '')
        return account_data

    @api.response(201, 'Success', response_family_member)
    @api.response(400, 'Failed', response_error)
    @api.doc(body=create_member_resource_fields)
    @api.expect(create_member_resource_fields, validate=True)
    def post(self, username, password):
        """Function to add new member to a Spotify Premium Plan

        Example of Request::

            Method: POST
            URL: /family/{username}:{password}

        :param username: Username of the Spotify account
        :param password: Password of the Spotify account

            Example of Body Request::

                {
                    "password": "string",
                    "email": "string", #
                    "first_name": "string",
                    "address": {
                        "line2": "string",
                        "postalCode": "string",
                        "city": "string",
                        "partnerCheck": "",
                        "line1": "string"
                    },
                    "country": "string",
                    "last_name": "string"
                }

            .. note::
                All the data of the body of the request is from the new user
                member of the spotify premium plan.

        :return: If the operation is correct: HTTP Code Status: 201 and the
         body of the answer in JSON format. If an error occurs: HTTP Code
         Status 400 and the body of response with data (JSON) about the error.


         Example of Successful Response::

            Http Code: 201 and JSON Content:
            {
              "email": "string",
              "username": "string",
              "full_name": "string",
              "membershipUuid": "string" # Created UUID
            }

         Example of Error Response::

             Http Code: 400 and JSON Content:
             {
                  "data": {
                    "http_code": "string",
                    "data": {},
                    "url": "string"
                  },
                  "message": "string",
                  "type": "http"
             }

        """
        post_parser = reqparse.RequestParser()
        post_parser.add_argument('first_name', type=str, required=True,
                                 help='First name is required')
        post_parser.add_argument('last_name', type=str, required=True,
                                 help='Last name is required')
        post_parser.add_argument('email', type=str, required=True,
                                 help='Email is required')
        post_parser.add_argument('password', type=str, required=True,
                                 help='Password is required')
        post_parser.add_argument('country', type=str, required=False,
                                 help='Country')
        post_parser.add_argument("address", type=dict, required=True)

        address_parser = reqparse.RequestParser()
        address_parser.add_argument('line1', type=str, store_missing=False,
                                    location='address', required=True)
        address_parser.add_argument('line2', type=str, store_missing=False,
                                    location='address', required=True)
        address_parser.add_argument('postalCode', type=str,
                                    store_missing=False,
                                    location='address', required=True)
        address_parser.add_argument('city', type=str, store_missing=False,
                                    location='address', required=True)
        address_parser.add_argument('partnerCheck', type=str,
                                    store_missing=False,
                                    location='address', required=True)

        root_args = post_parser.parse_args()
        address_args = address_parser.parse_args(req=root_args)

        try:
            session_premium = requests.Session()
            spotify.do_login(session_premium, username, password)

            data_invitation = {'firstName': root_args['first_name'],
                               'lastName': root_args['last_name'],
                               'email': root_args['email']}
            token = spotify.create_invitation(session_premium, data_invitation)
            session_member = requests.Session()
            try:
                spotify.do_login(session_member, root_args['email'],
                                 root_args['password'])

            except ValueError:
                spotify.cancel_invitation(session_premium, token)
                return {
                           'errors': {
                               'message': 'Invalid credentials for '
                                          'the member user',
                               'type': 'auth',
                               'username': root_args['email']
                           }
                       }, 400

            if root_args['country']:
                spotify.update_profile(session_member, {
                    'profile[country]': root_args['country']
                })

            spotify.confirm_invitation(session_member, {
                'token': token,
                'firstName': root_args['first_name'],
                "lastName": root_args['last_name'],
                "address": {
                    "line1": address_args['line1'],
                    "line2": address_args['line2'],
                    "postalCode": address_args['postalCode'],
                    "city": address_args['city'],
                    "partnerCheck": address_args['partnerCheck']
                }
            })

            account_data = spotify.get_account_profile(session_premium)
            members = account_data['members']
            for member in members:
                if member['email'] == root_args['email']:
                    return member, 201
            return {
                       'errors': {
                           'message': 'Upgrade user',
                           'type': 'logic',
                           'username': username,
                       }
                   }, 400
        except ValueError as e:
            return {'errors': e.args}, 400


if __name__ == '__main__':
    app.run(debug=False, port=cfg.APP_PORT)
