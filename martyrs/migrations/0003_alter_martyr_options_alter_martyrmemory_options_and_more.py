# Generated by Django 5.2 on 2025-06-22 07:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_persona'),
        ('martyrs', '0002_martyrmemory'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='martyr',
            options={'ordering': ['last_name', 'first_name'], 'verbose_name': 'شهید', 'verbose_name_plural': 'شهدا'},
        ),
        migrations.AlterModelOptions(
            name='martyrmemory',
            options={'ordering': ['-created_at'], 'verbose_name': 'خاطره شهید', 'verbose_name_plural': 'خاطرات شهدا'},
        ),
        migrations.AddField(
            model_name='martyrmemory',
            name='persona',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.persona', verbose_name='شخصیت ارسال\u200cکننده'),
        ),
        migrations.AlterField(
            model_name='martyr',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='تاریخ تولد'),
        ),
        migrations.AlterField(
            model_name='martyr',
            name='birth_place',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='محل تولد'),
        ),
        migrations.AlterField(
            model_name='martyr',
            name='father_name',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='نام پدر'),
        ),
        migrations.AlterField(
            model_name='martyr',
            name='first_name',
            field=models.CharField(max_length=50, verbose_name='نام'),
        ),
        migrations.AlterField(
            model_name='martyr',
            name='grave_place',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='محل دفن'),
        ),
        migrations.AlterField(
            model_name='martyr',
            name='last_name',
            field=models.CharField(max_length=50, verbose_name='نام خانوادگی'),
        ),
        migrations.AlterField(
            model_name='martyr',
            name='last_operation',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='آخرین عملیات'),
        ),
        migrations.AlterField(
            model_name='martyr',
            name='martyr_date',
            field=models.DateField(blank=True, null=True, verbose_name='تاریخ شهادت'),
        ),
        migrations.AlterField(
            model_name='martyr',
            name='martyr_place',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='محل شهادت'),
        ),
        migrations.AlterField(
            model_name='martyr',
            name='martyr_region',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='منطقه شهادت'),
        ),
        migrations.AlterField(
            model_name='martyr',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='martyrs/photos/', verbose_name='عکس شهید'),
        ),
        migrations.AlterField(
            model_name='martyrmemory',
            name='audio',
            field=models.FileField(blank=True, null=True, upload_to='memories/audio/', verbose_name='فایل صوتی'),
        ),
        migrations.AlterField(
            model_name='martyrmemory',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت'),
        ),
        migrations.AlterField(
            model_name='martyrmemory',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='memories/images/', verbose_name='تصویر'),
        ),
        migrations.AlterField(
            model_name='martyrmemory',
            name='martyr',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memories', to='martyrs.martyr', verbose_name='شهید مربوطه'),
        ),
        migrations.AlterField(
            model_name='martyrmemory',
            name='text',
            field=models.TextField(blank=True, null=True, verbose_name='دل\u200cنوشته'),
        ),
        migrations.AlterField(
            model_name='martyrmemory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='کاربر ارسال\u200cکننده'),
        ),
    ]
