# Generated by Django 2.2.14 on 2020-10-02 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_remove_item_prescription'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='prescription',
            field=models.BooleanField(default=False),
        ),
    ]
