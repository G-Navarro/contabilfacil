# Generated by Django 4.2 on 2023-10-25 16:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('empbase', '0002_turno_diafolga'),
    ]

    operations = [
        migrations.AddField(
            model_name='tramites',
            name='emp',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.empresa'),
            preserve_default=False,
        ),
    ]
