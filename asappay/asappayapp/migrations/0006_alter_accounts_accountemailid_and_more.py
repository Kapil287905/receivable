# Generated by Django 5.2 on 2025-05-17 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asappayapp', '0005_alter_accounts_accountgst_alter_accounts_accountpan_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounts',
            name='accountemailid',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='accounts',
            name='accountgst',
            field=models.CharField(default='N/A', max_length=15),
        ),
        migrations.AlterField(
            model_name='accounts',
            name='accountpan',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='accounts',
            name='address',
            field=models.CharField(default='N/A', max_length=255),
        ),
        migrations.AlterField(
            model_name='accounts',
            name='pincode',
            field=models.CharField(default='000000', max_length=10),
        ),
    ]
