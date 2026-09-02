from django.conf import settings


class SecurityHeadersMiddleware:
    """Adiciona políticas de navegador e impede cache de páginas com dados pessoais."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers.setdefault(
            'Content-Security-Policy',
            "; ".join(
                [
                    "default-src 'self'",
                    "base-uri 'self'",
                    "connect-src 'self'",
                    "font-src 'self' https://cdn.jsdelivr.net data:",
                    "form-action 'self'",
                    "frame-ancestors 'none'",
                    "img-src 'self' data:",
                    "object-src 'none'",
                    "script-src 'self' https://cdn.jsdelivr.net",
                    "style-src 'self' https://cdn.jsdelivr.net",
                ]
            ),
        )
        response.headers.setdefault(
            'Permissions-Policy',
            'camera=(), geolocation=(), microphone=(), payment=(), usb=()',
        )
        response.headers.setdefault('X-Robots-Tag', 'noindex, nofollow')

        if getattr(request, 'user', None) and request.user.is_authenticated:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response.headers['Pragma'] = 'no-cache'

        if not settings.DEBUG:
            response.headers.setdefault('Cross-Origin-Opener-Policy', 'same-origin')

        return response
