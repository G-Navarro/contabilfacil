# Generated by Django 4.2 on 2023-11-05 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empbase', '0013_alocacao_emp_alter_holerite_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='diadetrabalho',
            name='folga',
            field=models.BooleanField(default=False),
        ),
    ]
