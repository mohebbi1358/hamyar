# Generated by Django 5.2 on 2025-06-12 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_gender'),
        ('news', '0004_alter_category_name_alter_category_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='allowed_categories',
            field=models.ManyToManyField(blank=True, related_name='allowed_users', to='news.category', verbose_name='دسته\u200cبندی\u200cهای مجاز برای ارسال خبر'),
        ),
    ]
