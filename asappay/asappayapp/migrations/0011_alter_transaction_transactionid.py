# Generated by Django 5.2 on 2025-05-17 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asappayapp', '0010_alter_accountsc_accountid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transactionid',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
