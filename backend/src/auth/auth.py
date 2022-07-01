"""Authentication file"""
import json
from functools import wraps
from urllib.request import urlopen

from flask import abort, request
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
AUTH0_DOMAIN = 'dev-3jfc9qzs.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'image'

## AuthError Exception

class AuthError(Exception):
    '''
    AuthError Exception
    A standardized way to communicate auth failure modes
    '''
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header


def get_token_auth_header():
    '''@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
    '''
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token


def check_permission(permission, payload):
    '''
    @TODO implement check_permissions(permission, payload) method
        @INPUTS
            permission: string permission (i.e. 'post:drink')
            payload: decoded jwt payload

        it should raise an AuthError if permissions are not included in the payload
            !!NOTE check your RBAC settings in Auth0
        it should raise an AuthError if the requested permission string is not in the
        payload permissions array
        return true otherwise
    '''
    if 'permissions' not in payload:
        abort(400)
    if permission not in payload['permissions']:
        abort(403)
    return True

def verify_decode_jwt(token):
    """Takes the token and verifies that it is valid, invalid or expired"""
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload

        except ExpiredSignatureError as ese:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401) from ese

        except JWTClaimsError as ese:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401) from ese
        except Exception as exc:
            raise AuthError ({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400) from exc
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

def requires_auth(permission=''):
    """Decorator for checking authentication for an endpoint"""
    def requires_auth_permission(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permission(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_permission
