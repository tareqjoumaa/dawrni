# Generated by Django 4.2.6 on 2023-11-14 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dawrni_app', '0025_alter_company_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='custom_user',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
