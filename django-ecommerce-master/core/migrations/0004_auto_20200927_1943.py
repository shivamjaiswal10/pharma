# Generated by Django 2.2.14 on 2020-09-27 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='available_quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='item',
            name='discount_percentage',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='do_we_sell',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='item',
            name='manufacturer',
            field=models.CharField(default='Dabur', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='one_click_purchasing',
            field=models.BooleanField(default=False),
        ),
    ]
