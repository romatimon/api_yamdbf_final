# Generated by Django 3.2 on 2023-11-02 06:33

import api.v1.validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[api.v1.validators.username_validator, django.core.validators.RegexValidator(message='Имя пользователя содержит недопустимый символ', regex='^[\\w.@+-]+$')], verbose_name='Имя пользователя'),
        ),
    ]