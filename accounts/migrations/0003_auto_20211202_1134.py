# Generated by Django 3.1.7 on 2021-12-02 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userotp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]
