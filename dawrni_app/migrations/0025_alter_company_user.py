# Generated by Django 4.2.6 on 2023-11-14 13:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dawrni_app', '0024_alter_category_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dawrni_app.custom_user'),
        ),
    ]
