# Generated by Django 4.1.7 on 2023-06-22 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empbase', '0015_pagamento_alter_holerite_funcs'),
    ]

    operations = [
        migrations.AddField(
            model_name='imposto',
            name='pago',
            field=models.BooleanField(default=False),
        ),
    ]
