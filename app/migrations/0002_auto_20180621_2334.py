# Generated by Django 2.0.6 on 2018-06-21 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nonce',
            name='id',
        ),
        migrations.AlterField(
            model_name='nonce',
            name='nonce',
            field=models.CharField(default='', max_length=135, primary_key=True, serialize=False),
        ),
    ]