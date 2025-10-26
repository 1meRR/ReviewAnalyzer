from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, exceptions

User = get_user_model()


def _b64encode(data: bytes) -> str: return base64.urlsafe_b64encode(data).decode().rstrip('=')

def _sign(message: bytes) -> str: return _b64encode(hmac.new(settings.SECRET_KEY.encode(), message, hashlib.sha256).digest())

def encode(payload: dict, lifetime: timedelta | None = None) -> str:
    now = datetime.now(timezone.utc)
    exp = now + (lifetime or timedelta(hours=6))
    data = payload | {'iat': int(now.timestamp()), 'exp': int(exp.timestamp())}
    header = _b64encode(json.dumps({'alg': 'HS256', 'typ': 'JWT'}, separators=(',', ':')).encode())
    body = _b64encode(json.dumps(data, separators=(',', ':')).encode())
    return f'{header}.{body}.{_sign(f"{header}.{body}".encode())}'

def decode(token: str) -> dict:
    try:
        header, body, signature = token.split('.')
    except ValueError as exc:  # pragma: no cover
        raise exceptions.AuthenticationFailed(_('Invalid token')) from exc
    if not hmac.compare_digest(signature, _sign(f'{header}.{body}'.encode())):
        raise exceptions.AuthenticationFailed(_('Invalid signature'))
    data = json.loads(base64.urlsafe_b64decode(body + '=' * (-len(body) % 4)))
    if datetime.fromtimestamp(data.get('exp', 0), timezone.utc) < datetime.now(timezone.utc):
        raise exceptions.AuthenticationFailed(_('Token expired'))
    return data


class JWTAuthentication(authentication.BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request):
        raw = authentication.get_authorization_header(request).decode()
        if not raw:
            return None
        try:
            prefix, token = raw.split(' ', 1)
        except ValueError:
            raise exceptions.AuthenticationFailed(_('Invalid header'))
        if prefix != self.keyword:
            return None
        payload = decode(token)
        try:
            user = User.objects.get(id=payload.get('user_id'))
        except User.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed(_('User not found')) from exc
        return user, token

    def authenticate_header(self, request) -> str:  # pragma: no cover
        return self.keyword
