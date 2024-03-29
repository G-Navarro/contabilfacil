# Generated by Django 4.2 on 2023-10-25 14:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Base',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado', models.DateField(auto_now_add=True, null=True)),
                ('atualizado', models.DateField(auto_now=True, null=True)),
                ('ativa', models.BooleanField(blank=True, default=True, null=True)),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Escritorio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cnpj', models.CharField(blank=True, max_length=30, null=True, unique=True)),
                ('inscest', models.CharField(blank=True, max_length=30, null=True)),
                ('inscmun', models.CharField(blank=True, max_length=30, null=True)),
                ('inscjunta', models.CharField(blank=True, max_length=30, null=True)),
                ('apelido', models.CharField(max_length=100)),
                ('nome', models.CharField(max_length=100)),
                ('rsocial', models.CharField(max_length=100)),
                ('natjuridica', models.CharField(blank=True, max_length=100, null=True)),
                ('inicio', models.DateField(blank=True, null=True)),
                ('tipoend', models.CharField(blank=True, max_length=30, null=True)),
                ('endereco', models.CharField(blank=True, max_length=150, null=True)),
                ('num', models.CharField(blank=True, max_length=30, null=True)),
                ('bairro', models.CharField(blank=True, max_length=100, null=True)),
                ('municipio', models.CharField(blank=True, max_length=100, null=True)),
                ('uf', models.CharField(blank=True, max_length=10, null=True)),
                ('pais', models.CharField(blank=True, max_length=50, null=True)),
                ('cep', models.CharField(blank=True, max_length=10, null=True)),
                ('cnae', models.CharField(blank=True, max_length=15, null=True)),
                ('capital', models.FloatField(blank=True, null=True)),
                ('email', models.CharField(max_length=100)),
                ('usuarios', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Contribuintes',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('nome', models.CharField(max_length=200)),
            ],
            bases=('empbase.base',),
        ),
        migrations.CreateModel(
            name='DiaDeTrabalho',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('inicioem', models.DateField(blank=True, null=True)),
                ('entrou', models.BooleanField(default=False)),
                ('encerrado', models.BooleanField(default=False)),
                ('entrada', models.DateTimeField(blank=True, null=True)),
                ('intervalo', models.DateTimeField(blank=True, null=True)),
                ('fimintervalo', models.DateTimeField(blank=True, null=True)),
                ('saida', models.DateTimeField(blank=True, null=True)),
                ('observacao', models.TextField(blank=True, null=True)),
            ],
            bases=('empbase.base',),
        ),
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('cod', models.IntegerField(unique=True)),
                ('cnpj', models.CharField(max_length=30, unique=True)),
                ('inscest', models.CharField(blank=True, max_length=30, null=True)),
                ('inscmun', models.CharField(blank=True, max_length=30, null=True)),
                ('inscjunta', models.CharField(blank=True, max_length=30, null=True)),
                ('apelido', models.CharField(max_length=100)),
                ('nome', models.CharField(max_length=100)),
                ('rsocial', models.CharField(max_length=100)),
                ('natjuridica', models.CharField(max_length=100)),
                ('inicio', models.DateField()),
                ('tipoend', models.CharField(max_length=30)),
                ('endereco', models.CharField(max_length=150)),
                ('num', models.CharField(max_length=30)),
                ('bairro', models.CharField(max_length=100)),
                ('municipio', models.CharField(max_length=100)),
                ('uf', models.CharField(max_length=10)),
                ('pais', models.CharField(max_length=50)),
                ('cep', models.CharField(max_length=10)),
                ('cnae', models.CharField(max_length=15)),
                ('capital', models.FloatField()),
                ('email', models.CharField(max_length=100)),
                ('situacao', models.CharField(default='Ativa', max_length=20)),
                ('formaenvio', models.CharField(default='2', max_length=5)),
                ('exonera_folha', models.BooleanField(default=False)),
                ('escr', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.escritorio')),
                ('responsavel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.contribuintes')),
            ],
            bases=('empbase.base',),
        ),
        migrations.CreateModel(
            name='Funcionario',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('cod', models.IntegerField()),
                ('nome', models.CharField(max_length=150)),
                ('cpf', models.CharField(max_length=14)),
                ('pis', models.CharField(max_length=14)),
                ('admissao', models.DateField()),
                ('salario', models.FloatField(blank=True, null=True)),
                ('cargo', models.CharField(max_length=30)),
                ('cbo', models.CharField(default=None, max_length=8)),
                ('rg', models.CharField(blank=True, max_length=15, null=True)),
                ('rgemiss', models.DateField(blank=True, max_length=5, null=True)),
                ('rgorgao', models.CharField(blank=True, max_length=5, null=True)),
                ('ctps', models.CharField(default=None, max_length=10)),
                ('ctpsserie', models.CharField(default=None, max_length=5)),
                ('ctpsdata', models.DateField(blank=True, null=True)),
                ('ctpsuf', models.CharField(default=None, max_length=2)),
                ('logradouro', models.CharField(default=None, max_length=100)),
                ('num', models.CharField(default=None, max_length=10)),
                ('bairro', models.CharField(default=None, max_length=50)),
                ('cidade', models.CharField(default=None, max_length=70)),
                ('uf', models.CharField(default=None, max_length=2)),
                ('cep', models.IntegerField(default=None)),
                ('datanasc', models.DateField(default=None)),
                ('cidadenasc', models.CharField(default=None, max_length=100)),
                ('ufnasc', models.CharField(default=None, max_length=2)),
                ('genero', models.CharField(default=None, max_length=15)),
                ('pai', models.CharField(blank=True, max_length=100, null=True)),
                ('mae', models.CharField(default=None, max_length=100)),
                ('demissao', models.DateField(blank=True, default=None, null=True)),
                ('demitido', models.BooleanField(default=False)),
                ('emp', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.empresa')),
                ('funcacesso', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            bases=('empbase.base',),
        ),
        migrations.CreateModel(
            name='Tramites',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('nome', models.CharField(max_length=100)),
                ('finalizado', models.BooleanField(default=False)),
                ('datafinalizado', models.DateField(blank=True, null=True)),
                ('observacao', models.TextField(blank=True, null=True)),
            ],
            bases=('empbase.base',),
        ),
        migrations.CreateModel(
            name='UltimoAcesso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comp', models.DateField()),
                ('atualizado', models.DateField(auto_now=True)),
                ('escr', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.escritorio')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('emp', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.empresa')),
            ],
        ),
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('semana', models.IntegerField(default=8)),
                ('intervalosemana', models.IntegerField(default=1)),
                ('fsemana', models.IntegerField(default=4)),
                ('intervalofsemana', models.IntegerField(default=0)),
                ('entrada', models.CharField(default='08:00', max_length=5)),
                ('intervalo', models.CharField(default='12:00', max_length=5)),
                ('fimintervalo', models.CharField(default='13:00', max_length=5)),
                ('saida', models.CharField(default='17:00', max_length=5)),
                ('entradafs', models.CharField(default='08:00', max_length=5)),
                ('intervalofs', models.CharField(blank=True, max_length=5, null=True)),
                ('fimintervalofs', models.CharField(blank=True, max_length=5, null=True)),
                ('saidafs', models.CharField(default='12:00', max_length=5)),
                ('emp', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.empresa')),
            ],
            bases=('empbase.base',),
        ),
        migrations.CreateModel(
            name='TemAcesso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atualizado', models.DateField(auto_now=True)),
                ('escr', models.ManyToManyField(to='empbase.escritorio')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('emp', models.ManyToManyField(to='empbase.empresa')),
            ],
        ),
        migrations.CreateModel(
            name='Rubrica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('cod', models.IntegerField(unique=True)),
                ('emp', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.empresa')),
            ],
        ),
        migrations.CreateModel(
            name='Rescisao',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('tiporescisao', models.CharField(blank=True, choices=[('Pedido de Demissão', 'Ped'), ('Demissão Sem Justa Causa', 'Dsj'), ('Demissão Com Justa Causa', 'Dcj'), ('Término de Experiência', 'Term'), ('Término de Experiência Antecipado', 'Terant')], max_length=40, null=True)),
                ('tipoaviso', models.CharField(blank=True, max_length=30, null=True)),
                ('reducao', models.DateField(blank=True, null=True)),
                ('aviso', models.DateField(blank=True, null=True)),
                ('final', models.DateField()),
                ('emp', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.empresa')),
                ('func', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='empbase.funcionario')),
                ('tramite', models.ManyToManyField(to='empbase.tramites')),
            ],
            bases=('empbase.base',),
        ),
        migrations.CreateModel(
            name='PeriodoAquisitivo',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('periodoinicio', models.DateField(blank=True, null=True)),
                ('periodofim', models.DateField(blank=True, null=True)),
                ('diasdedireito', models.IntegerField(default=30)),
                ('datamaxima', models.DateField(blank=True, null=True)),
                ('emp', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.empresa')),
                ('func', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='empbase.funcionario')),
            ],
            bases=('empbase.base',),
        ),
        migrations.CreateModel(
            name='Pagamento',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('pago', models.BooleanField(default=False)),
                ('func', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='empbase.funcionario')),
            ],
            bases=('empbase.base',),
        ),
        migrations.CreateModel(
            name='Obras',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('cod', models.IntegerField(blank=True, null=True)),
                ('cnpj', models.CharField(blank=True, max_length=30, null=True)),
                ('cno', models.CharField(blank=True, max_length=30, null=True)),
                ('nome', models.CharField(max_length=100)),
                ('endereco', models.CharField(max_length=150)),
                ('num', models.CharField(max_length=30)),
                ('bairro', models.CharField(max_length=100)),
                ('municipio', models.CharField(max_length=100)),
                ('uf', models.CharField(max_length=10)),
                ('cep', models.CharField(blank=True, max_length=10, null=True)),
                ('emp', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.empresa')),
            ],
            bases=('empbase.base',),
        ),
        migrations.CreateModel(
            name='Notas',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('numero', models.IntegerField()),
                ('canc', models.IntegerField()),
                ('comp', models.DateField()),
                ('valor', models.FloatField()),
                ('inss', models.FloatField()),
                ('iss', models.FloatField()),
                ('emp', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.empresa')),
                ('tomador', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.obras')),
            ],
            bases=('empbase.base',),
        ),
        migrations.CreateModel(
            name='Lancamento',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('valor', models.FloatField(default=0)),
                ('comp', models.DateField()),
                ('diatrabalhado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.diadetrabalho')),
                ('func', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='empbase.funcionario')),
                ('rub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='empbase.rubrica')),
            ],
            bases=('empbase.base',),
        ),
        migrations.CreateModel(
            name='Imposto',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('nome', models.CharField(max_length=80)),
                ('valor', models.FloatField()),
                ('comp', models.DateField()),
                ('vcto', models.DateField(blank=True, null=True)),
                ('enviado', models.BooleanField(default=False)),
                ('pago', models.BooleanField(default=False)),
                ('emp', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.empresa')),
            ],
            bases=('empbase.base',),
        ),
        migrations.CreateModel(
            name='Holerite',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('tipo', models.CharField(choices=[('ADIANTAMENTO', 'Ad'), ('FOLHA MENSAL', 'Fm'), ('ADIANTAMENTO 13º', 'Ad13'), ('FOLHA MENSAL 13º', 'Fm13')], max_length=18)),
                ('comp', models.DateField()),
                ('enviado', models.BooleanField(default=False)),
                ('funcs', models.ManyToManyField(to='empbase.pagamento')),
            ],
            bases=('empbase.base',),
        ),
        migrations.AddField(
            model_name='funcionario',
            name='jornada',
            field=models.ForeignKey(default=7352, on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.turno'),
        ),
        migrations.CreateModel(
            name='Ferias',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('aviso', models.DateField(blank=True, null=True)),
                ('inicio', models.DateField(blank=True, null=True)),
                ('final', models.DateField(blank=True, null=True)),
                ('periodo_aquisitivo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='empbase.periodoaquisitivo')),
                ('tramite', models.ManyToManyField(to='empbase.tramites')),
            ],
            bases=('empbase.base',),
        ),
        migrations.AddField(
            model_name='diadetrabalho',
            name='func',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='empbase.funcionario'),
        ),
        migrations.CreateModel(
            name='Alocacao',
            fields=[
                ('base_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='empbase.base')),
                ('comp', models.DateField()),
                ('func', models.ManyToManyField(to='empbase.funcionario')),
                ('nota', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.notas')),
                ('obra', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='empbase.obras')),
            ],
            bases=('empbase.base',),
        ),
    ]
