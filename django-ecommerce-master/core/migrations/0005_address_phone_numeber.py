# Generated by Django 2.2.14 on 2020-09-27 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20200927_1943'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='phone_numeber',
            field=models.CharField(default='1111111111', max_length=10),
            preserve_default=False,
        ),
    ]