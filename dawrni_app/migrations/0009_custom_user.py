# Generated by Django 4.2.6 on 2023-11-07 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dawrni_app', '0008_alter_client_user_alter_company_user_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Custom_user',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('image', models.ImageField(blank=True, null=True, upload_to='user_images/')),
                ('user_type', models.CharField(choices=[('company', 'Company'), ('user', 'User')], default='user', max_length=8)),
            ],
        ),
    ]
