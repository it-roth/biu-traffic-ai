from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_default_accounts(sender, **kwargs):
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Default admin account
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@beltei.edu.kh', 'admin123')
            print('[BIU Traffic AI] Seeded default admin superuser: admin / admin123')

        # Default officer account
        if not User.objects.filter(username='roth').exists():
            User.objects.create_superuser('roth', 'saroth@gmail.com', 'roth123')
            print('[BIU Traffic AI] Seeded default officer superuser: roth / roth123')
    except Exception as e:
        print(f'[BIU Traffic AI] Account seed skipped: {e}')


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        post_migrate.connect(create_default_accounts, sender=self)
