from datetime import datetime, timedelta
from django.db import models
from usuarios.models import Usuario
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

class Base(models.Model):
    criado = models.DateField(auto_now_add=True, null=True, blank=True)
    atualizado = models.DateField(auto_now=True, null=True, blank=True)
    ativa = models.BooleanField(default=True, null=True, blank=True)
    usuario = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return f'{self.criado} - {self.atualizado} - {self.ativa}'


class Tramites(Base):
    emp = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    nome = models.CharField(max_length=100)
    finalizado = models.BooleanField(default=False)
    datafinalizado = models.DateField(null=True, blank=True)
    observacao = models.TextField(null=True, blank=True)


class Competencia(models.Model):
    emp = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    nome = models.CharField(max_length=100)
    comp = models.DateField()
    finalizada = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.emp.cod} - {self.nome} - {self.comp}'
    
    class Meta:
        ordering = ['emp', 'comp']


class Contribuintes(Base):
    nome = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.nome}'

class Escritorio(models.Model):
    cnpj = models.CharField(max_length=30, unique=True, null=True, blank=True)
    inscest = models.CharField(max_length=30, blank=True, null=True)
    inscmun = models.CharField(max_length=30, blank=True, null=True)
    inscjunta = models.CharField(max_length=30, blank=True, null=True)
    apelido = models.CharField(max_length=100)
    nome = models.CharField(max_length=100)
    rsocial = models.CharField(max_length=100)
    natjuridica = models.CharField(max_length=100, null=True, blank=True)
    inicio = models.DateField(null=True, blank=True)
    tipoend = models.CharField(max_length=30, null=True, blank=True)
    endereco = models.CharField(max_length=150, null=True, blank=True)
    num = models.CharField(max_length=30, null=True, blank=True)
    bairro = models.CharField(max_length=100, null=True, blank=True)
    municipio = models.CharField(max_length=100, null=True, blank=True)
    uf = models.CharField(max_length=10, null=True, blank=True)
    pais = models.CharField(max_length=50, null=True, blank=True)
    cep = models.CharField(max_length=10, null=True, blank=True)
    cnae = models.CharField(max_length=15, null=True, blank=True)
    capital = models.FloatField(null=True, blank=True)
    email = models.CharField(max_length=100)
    usuarios = models.ManyToManyField(Usuario)

    def __str__(self):
        return f'{self.id} - {self.apelido}'


class Empresa(Base):
    cod = models.IntegerField()
    cnpj = models.CharField(max_length=30, unique=True)
    inscest = models.CharField(max_length=30, blank=True, null=True)
    inscmun = models.CharField(max_length=30, blank=True, null=True)
    inscjunta = models.CharField(max_length=30, blank=True, null=True)
    apelido = models.CharField(max_length=100)
    nome = models.CharField(max_length=100)
    rsocial = models.CharField(max_length=100)
    natjuridica = models.CharField(max_length=100)
    inicio = models.DateField()
    tipoend = models.CharField(max_length=30)
    endereco = models.CharField(max_length=150)
    num = models.CharField(max_length=30)
    bairro = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    uf = models.CharField(max_length=10)
    pais = models.CharField(max_length=50)
    cep = models.CharField(max_length=10)
    cnae = models.CharField(max_length=15)
    capital = models.FloatField()
    email = models.CharField(max_length=100)
    responsavel = models.ForeignKey(Contribuintes, blank=True, null=True, on_delete=models.DO_NOTHING)
    situacao = models.CharField(max_length=20, default='Ativa')
    formaenvio = models.CharField(max_length=5, default='2')
    paga_vr = models.BooleanField(default=False)
    exonera_folha = models.BooleanField(default=False)
    escr = models.ForeignKey(Escritorio, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.cod} - {self.apelido}'

    class Meta:
        ordering = ['escr', 'cod']

class Turno(Base):
    emp = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    semana = models.IntegerField(default=8)
    intervalosemana = models.IntegerField(default=1)
    fsemana = models.IntegerField(default=4)
    intervalofsemana = models.IntegerField(default=0)
    entrada = models.CharField(max_length=5, default='08:00')
    intervalo = models.CharField(max_length=5, default='12:00')
    fimintervalo = models.CharField(max_length=5, default='13:00')
    saida = models.CharField(max_length=5, default='17:00')
    entradafs = models.CharField(max_length=5, default='08:00')
    intervalofs = models.CharField(max_length=5, blank=True, null=True)
    fimintervalofs = models.CharField(max_length=5, blank=True, null=True)
    saidafs = models.CharField(max_length=5, default='12:00')
    diafolga = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return f'{self.entrada} - {self.intervalo} - {self.fimintervalo} - {self.saida}'

class ValeTransporte(Base):
    emp = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING, null=True, blank=True)
    nome = models.CharField(max_length=100, default='Hortolândia')
    valor = models.FloatField(default= 5.25)

    def __str__(self):
        return f'{self.nome} - {str(self.valor)}'


class Funcionario(Base):
    emp = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    cod = models.IntegerField()
    matesocial = models.IntegerField(blank=True, null=True)
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14)
    pis = models.CharField(max_length=14)
    admissao = models.DateField()
    salario = models.FloatField(blank=True, null=True)
    cargo = models.CharField(max_length=30)
    cbo = models.CharField(max_length=8, default=None)
    rg = models.CharField(max_length=15, blank=True, null=True)
    rgemiss = models.DateField(max_length=5, blank=True, null=True)
    rgorgao = models.CharField(max_length=5, blank=True, null=True)
    ctps = models.CharField(max_length=10, default=None)
    ctpsserie = models.CharField(max_length=5, default=None)
    ctpsdata = models.DateField(blank=True, null=True)
    ctpsuf = models.CharField(max_length=2, default=None)
    jornada = models.ForeignKey(Turno, on_delete=models.DO_NOTHING, default=7352)
    logradouro = models.CharField(max_length=100, default=None)
    num = models.CharField(max_length=10, default=None)
    bairro = models.CharField(max_length=50, default=None)
    cidade = models.CharField(max_length=70, default=None)
    uf = models.CharField(max_length=2, default=None)
    cep = models.IntegerField(default=None)
    datanasc = models.DateField(default=None)
    cidadenasc = models.CharField(max_length=100, default=None)
    ufnasc = models.CharField(max_length=2, default=None)
    genero = models.CharField(max_length=15, default=None)
    pai = models.CharField(max_length=100, blank=True, null=True)
    mae = models.CharField(max_length=100, default=None)
    vt = models.ForeignKey(ValeTransporte, on_delete=models.DO_NOTHING, null=True, blank=True)
    demissao = models.DateField(blank=True, null=True, default=None)
    demitido = models.BooleanField(default=False)
    funcacesso = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return f'{self.emp.cod} - {self.cod} - {self.nome}'

    class Meta:
        ordering = ['emp', 'cod']


class PeriodoAquisitivo(Base):
    def datamaxima_calc(self, periodofim):
        if periodofim.day == 29 and periodofim.month == 2:
            periodofim = periodofim.replace(day=28)
        trintadias = periodofim.replace(year=periodofim.year + 1) - timedelta(days=30)
        datamaxima = trintadias
        while datamaxima.weekday() > 2:
            datamaxima -= timedelta(days=1)
        return datamaxima
    
    emp = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    func = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    periodoinicio = models.DateField(blank=True, null=True)
    periodofim = models.DateField(blank=True, null=True)
    diasdedireito = models.IntegerField(default=30)
    datamaxima = models.DateField(blank=True, null=True)
    def __str__(self):
        return f'{self.func.nome} - {self.periodoinicio} - {self.periodofim}'


class Ferias(Base):
    periodo_aquisitivo = models.ForeignKey(PeriodoAquisitivo, on_delete=models.CASCADE, blank=True, null=True)
    aviso = models.DateField(blank=True, null=True)
    inicio = models.DateField(blank=True, null=True)
    final = models.DateField(blank=True, null=True)
    tramite = models.ManyToManyField(Tramites)

    def __str__(self):
        return f'{self.aviso} - {self.inicio}'


class Rescisao(Base):
    class Tipo(models.TextChoices):
        PED = 'Pedido de Demissão'
        DSJ = 'Demissão Sem Justa Causa'
        DCJ = 'Demissão Com Justa Causa'
        TERM =  'Término de Experiência'
        TERANT = 'Término de Experiência Antecipado'

    emp = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    func = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    tiporescisao = models.CharField(max_length=40, choices=Tipo.choices, blank=True, null=True)
    tipoaviso = models.CharField(max_length=30, blank=True, null=True)
    reducao = models.DateField(blank=True, null=True)
    aviso = models.DateField(blank=True, null=True)
    final = models.DateField()
    tramite = models.ManyToManyField(Tramites)

    def __str__(self):
        return f'{self.func.cod} - {self.tiporescisao} - {self.final}'


class Pagamento(Base):
    func = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    pago = models.BooleanField(default=False)
    valor = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'{self.func.cod} - {self.valor}'

class Holerite(Base):
    class Tipo(models.TextChoices):
        AD = 'ADIANTAMENTO'
        FM = 'FOLHA MENSAL'
        AD13 = 'ADIANTAMENTO 13º'
        FM13 = 'PAGAMENTO 13º'

    emp = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    tipo = models.CharField(max_length=18, choices=Tipo.choices)
    comp = models.DateField()
    enviado = models.BooleanField(default=False)
    funcs = models.ManyToManyField(Pagamento)

    def __str__(self):
        return f'{self.emp} - {self.comp} - {self.tipo}'

class Obras(Base):
    emp = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    cod = models.IntegerField(null=True, blank=True)
    cnpj = models.CharField(max_length=30, null=True, blank=True)
    cno = models.CharField(max_length=30, null=True, blank=True)
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=150)
    num = models.CharField(max_length=30)
    bairro = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100)
    uf = models.CharField(max_length=10)
    cep = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f'{self.cod} - {self.nome}'


class DiaDeTrabalho(Base):
    func = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    inicioem = models.DateField(null=True, blank=True)
    entrou = models.BooleanField(default=False)
    encerrado = models.BooleanField(default=False)
    entrada = models.DateTimeField(null=True, blank=True)
    intervalo = models.DateTimeField(null=True, blank=True)
    fimintervalo = models.DateTimeField(null=True, blank=True)
    saida = models.DateTimeField(null=True, blank=True)
    horastrabalhadas = models.IntegerField(default=0)
    folga = models.BooleanField(default=False) 
    retificar = models.BooleanField(default=False)
    observacao = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.func.cod} - {self.func.nome} | {self.inicioem}'


class Rubrica(models.Model):
    emp = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=100)
    cod = models.IntegerField()

    def __str__(self):
        return self.name


class Lancamento(Base):
    rub = models.ForeignKey(Rubrica, on_delete=models.CASCADE)
    func = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    valor = models.FloatField(default=0)
    comp = models.DateField()
    diatrabalhado = models.ForeignKey(DiaDeTrabalho, on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return f'{self.rub.name} | {self.valor} | {self.comp}'


class Notas(Base):
    emp = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    numero = models.IntegerField()
    canc = models.IntegerField()
    comp = models.DateField()
    valor = models.FloatField()
    inss = models.FloatField()
    iss = models.FloatField()
    tomador = models.ForeignKey(Obras, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.tomador} | {self.comp}'


class Alocacao(Base):
    emp = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    nota = models.OneToOneField(Notas, on_delete=models.DO_NOTHING, null=True, blank=True)
    obra = models.ForeignKey(Obras, on_delete=models.DO_NOTHING)
    func = models.ManyToManyField(Funcionario)
    comp = models.DateField()

    def __str__(self):
        return f'{self.obra} | {self.comp}'


class UltimoAcesso(models.Model):
    escr = models.ForeignKey(Escritorio, on_delete=models.DO_NOTHING)
    emp = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING)
    user = models.OneToOneField(Usuario, on_delete=models.DO_NOTHING)
    comp = models.DateField()
    atualizado = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.emp} - {self.user} - {self.comp}'

    class Meta:
        ordering = ['emp', 'comp']

class TemAcesso(models.Model):
    escr = models.ManyToManyField(Escritorio)
    emp = models.ManyToManyField(Empresa)
    user = models.OneToOneField(Usuario, on_delete=models.DO_NOTHING)
    atualizado = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.user}'

    class Meta:
        ordering = ['user']


class Rel_Arquivos(Base):
    nome = models.CharField(max_length=80)
    arquivo = models.FileField(upload_to='arquivos/', null=True, blank=True)


class TiposGuia(Base):
    nome = models.CharField(max_length=80)
    ident_titular = models.CharField(max_length=80)
    ident_titular_regex = models.CharField(max_length=100, null=True, blank=True)
    ident_tipo_guia = models.CharField(max_length=80)
    ident_cod_guia = models.CharField(max_length=80)
    forma_pagamento = models.CharField(max_length=20, null=True, blank=True)
    comp_regex = models.CharField(max_length=100, default='(Janeiro|Fevereiro|Março|Abril|Maio|Junho|Julho|Agosto|Setembro|Outubro|Novembro|Dezembro)/\d{4}')

    def __str__(self):
        return self.nome


class Imposto(Base):
    emp = models.ForeignKey('Empresa', on_delete=models.DO_NOTHING)
    nome = models.CharField(max_length=250, null=True, blank=True)
    tipoguia = models.ForeignKey(TiposGuia, on_delete=models.DO_NOTHING, null=True, blank=True)
    valor = models.FloatField()
    comp = models.DateField()
    vcto = models.DateField(null=True, blank=True)
    identificador = models.CharField(max_length=30, null=True, blank=True)
    barcode = models.CharField(max_length=80, null=True, blank=True)
    pix = models.CharField(max_length=250, null=True, blank=True)
    enviado = models.BooleanField(default=False)
    pago = models.BooleanField(default=False)
    guia = models.FileField(upload_to='arquivos/', null=True, blank=True)
    arquivos = models.ForeignKey(Rel_Arquivos, on_delete=models.DO_NOTHING, null=True, blank=True)




'''from datetime import datetime
from empbase.models import Empresa, Contribuintes, Escritorio

escr = Escritorio.objects.get(nome='Escritório Exemplo')
def create_empresa(cod, cnpj, inscest, inscmun, inscjunta, apelido, nome, rsocial, natjuridica, inicio, tipoend, endereco, num, bairro, municipio, uf, pais, cep, cnae, capital, email, situacao, formaenvio, paga_vr, exonera_folha, escr):
    return Empresa.objects.create(
        cod=cod,
        cnpj=cnpj,
        inscest=inscest,
        inscmun=inscmun,
        inscjunta=inscjunta,
        apelido=apelido,
        nome=nome,
        rsocial=rsocial,
        natjuridica=natjuridica,
        inicio=inicio,
        tipoend=tipoend,
        endereco=endereco,
        num=num,
        bairro=bairro,
        municipio=municipio,
        uf=uf,
        pais=pais,
        cep=cep,
        cnae=cnae,
        capital=capital,
        email=email,
        situacao=situacao,
        formaenvio=formaenvio,
        paga_vr=paga_vr,
        exonera_folha=exonera_folha,
        escr=escr
    )

# Example usage:
contribuinte_example = Contribuintes.objects.first()  # replace with your actual logic to get a Contribuintes object
escritorio_example = Escritorio.objects.first()  # replace with your actual logic to get an Escritorio object

create_empresa(
    cod=192,
    cnpj="12345678000259",
    inscest="123456789",
    inscmun="123456789",
    inscjunta="123456789",
    apelido="Peter Pão Inc.",
    nome="Nome Empresa 1",
    rsocial="Razão Social 1",
    natjuridica="Ltda",
    inicio=datetime.now(),
    tipoend="Rua",
    endereco="Endereço da Empresa 1",
    num="123",
    bairro="Bairro Empresa 1",
    municipio="Cidade Empresa 1",
    uf="SP",
    pais="Brasil",
    cep="12345678",
    cnae="9876543",
    capital=100000.00,
    email="empresa1@example.com",
    situacao="Ativa",
    formaenvio="2",
    paga_vr=False,
    exonera_folha=False,
    escr=escr
)
'''
