# Generated by Django 3.1.7 on 2021-12-02 13:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20211202_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendrequests',
            name='requested_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]