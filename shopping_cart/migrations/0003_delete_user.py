# Generated by Django 2.2 on 2020-05-26 11:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('authtoken', '0002_auto_20160226_1747'),
        ('shopping_cart', '0002_auto_20200526_1552'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]
