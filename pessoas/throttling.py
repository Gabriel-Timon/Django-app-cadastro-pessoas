from datetime import timedelta
import secrets

from django.conf import settings
from django.core.signing import salted_hmac
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import SignupThrottle


SIGNUP_ATTEMPT_LIMIT = 5
SIGNUP_WINDOW = timedelta(hours=1)


def _client_key(request) -> str:
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if settings.IS_VERCEL and forwarded_for:
        client_address = forwarded_for.split(',', 1)[0].strip()
    else:
        client_address = request.META.get('REMOTE_ADDR', 'unknown')
    return salted_hmac('signup-throttle-v1', client_address).hexdigest()


@transaction.atomic
def consume_signup_attempt(request) -> tuple[bool, int]:
    now = timezone.now()
    key_hash = _client_key(request)
    created = False
    try:
        throttle = SignupThrottle.objects.select_for_update().get(key_hash=key_hash)
    except SignupThrottle.DoesNotExist:
        try:
            # O savepoint permite recuperar com lock caso outro worker crie a chave.
            with transaction.atomic():
                SignupThrottle.objects.create(
                    key_hash=key_hash,
                    window_started_at=now,
                    attempts=1,
                )
            created = True
        except IntegrityError:
            throttle = SignupThrottle.objects.select_for_update().get(key_hash=key_hash)

    if created:
        # Amostragem evita uma varredura de limpeza a cada novo endereço de origem.
        if secrets.randbelow(100) == 0:
            SignupThrottle.objects.filter(updated_at__lt=now - timedelta(days=7)).delete()
        return True, 0

    if throttle.window_started_at <= now - SIGNUP_WINDOW:
        throttle.window_started_at = now
        throttle.attempts = 0

    if throttle.attempts >= SIGNUP_ATTEMPT_LIMIT:
        retry_at = throttle.window_started_at + SIGNUP_WINDOW
        return False, max(1, int((retry_at - now).total_seconds()))

    throttle.attempts += 1
    throttle.save(update_fields=['window_started_at', 'attempts', 'updated_at'])

    return True, 0
