# Generated by Django 4.1.7 on 2023-06-16 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empbase', '0013_empresa_situacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='holerite',
            name='funcs',
            field=models.ManyToManyField(to='empbase.funcionario'),
        ),
    ]
