from django.conf import settings
from django.db import models
from .totp import generate_base32_secret


class TwoFactorProfile(models.Model):
    """
    Two-Factor Authentication Profile storing per-user dynamic TOTP secret keys.
    Compatible with Google Authenticator, Microsoft Authenticator, and RFC 6238.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='two_factor_profile'
    )
    secret_key = models.CharField(max_length=64, default=generate_base32_secret)
    is_enabled = models.BooleanField(default=True)
    last_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"2FA for {self.user.username} (enabled={self.is_enabled})"

    @property
    def otpauth_url(self):
        return f"otpauth://totp/BIU%20Traffic%20AI:{self.user.username}?secret={self.secret_key}&issuer=BIU%20Traffic%20AI"
