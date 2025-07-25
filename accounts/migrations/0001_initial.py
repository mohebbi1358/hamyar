# Generated by Django 5.2 on 2025-05-02 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('phone', models.CharField(max_length=11, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('national_code', models.CharField(blank=True, max_length=10)),
                ('image', models.ImageField(blank=True, null=True, upload_to='profiles/')),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_profile_completed', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, related_name='accounts_user_set', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='accounts_user_permissions_set', to='auth.permission')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
