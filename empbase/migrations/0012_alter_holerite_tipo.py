# Generated by Django 4.1.7 on 2023-06-15 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('empbase', '0011_holerite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='holerite',
            name='tipo',
            field=models.CharField(choices=[('ADIANTAMENTO', 'Ad'), ('FOLHA MENSAL', 'Fm'), ('ADIANTAMENTO 13º', 'Ad13'), ('FOLHA MENSAL 13º', 'Fm13')], max_length=18),
        ),
    ]