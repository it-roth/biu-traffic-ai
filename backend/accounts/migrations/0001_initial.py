from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import accounts.totp


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TwoFactorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('secret_key', models.CharField(default=accounts.totp.generate_base32_secret, max_length=64)),
                ('is_enabled', models.BooleanField(default=True)),
                ('last_verified_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='two_factor_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
