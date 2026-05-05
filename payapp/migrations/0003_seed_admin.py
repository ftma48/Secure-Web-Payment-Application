from django.db import migrations

def seed_admin(apps, schema_editor):
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin1').exists():
        User.objects.create_superuser(
            username='admin1',
            password='admin1',
            email='admin1@webapps.com'
        )

def reverse_seed(apps, schema_editor):
    from django.contrib.auth.models import User
    User.objects.filter(username='admin1').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('payapp', '0002_notification'),
    ]

    operations = [
        migrations.RunPython(seed_admin, reverse_seed),
    ]
