# Generated by Django 4.2.6 on 2023-11-24 16:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dawrni_app', '0032_favorite_client_favorites'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Appointment Date')),
                ('time', models.TimeField(verbose_name='Appointment Time')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled')], default='pending', max_length=20)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dawrni_app.client')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dawrni_app.company')),
            ],
        ),
    ]
