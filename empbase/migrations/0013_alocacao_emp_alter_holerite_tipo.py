# Generated by Django 4.2 on 2023-10-30 00:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('empbase', '0012_diadetrabalho_retificar'),
    ]

    operations = [
        migrations.AddField(
            model_name='alocacao',
            name='emp',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.empresa'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='holerite',
            name='tipo',
            field=models.CharField(choices=[('ADIANTAMENTO', 'Ad'), ('FOLHA MENSAL', 'Fm'), ('ADIANTAMENTO 13º', 'Ad13'), ('PAGAMENTO 13º', 'Fm13')], max_length=18),
        ),
    ]