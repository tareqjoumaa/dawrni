# Generated by Django 4.2.6 on 2023-11-14 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dawrni_app', '0023_alter_category_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
