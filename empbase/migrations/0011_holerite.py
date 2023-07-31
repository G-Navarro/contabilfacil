# Generated by Django 4.1.7 on 2023-06-15 14:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('empbase', '0010_empresa_escr'),
    ]

    operations = [
        migrations.CreateModel(
            name='Holerite',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('tipo', models.CharField(choices=[('AD', 'ADIANTAMENTO'), ('FM', 'FOLHA MENSAL'), ('AD13', 'ADIANTAMENTO 13º'), ('FM13', 'FOLHA MENSAL 13º')], max_length=4)),
                ('comp', models.DateField()),
                ('enviado', models.BooleanField(default=False)),
                ('emp', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.empresa')),
            ],
            bases=('empbase.base',),
        ),
    ]