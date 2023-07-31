from django.db import models
from usuarios.models import Usuario
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

class Base(models.Model):
    criado = models.DateField(auto_now_add=True)
    atualizado = models.DateField(auto_now=True)
    ativa = models.BooleanField(default=True)
    usuario = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, null=True, blank=True)


class Contribuintes(Base):
    nome = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.nome}'

class Escritorio(Base):
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
    cod = models.IntegerField(primary_key=True)
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
    exonera_folha = models.BooleanField(default=False)
    escr = models.ForeignKey(Escritorio, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.cod} - {self.apelido}'


class Turno(Base):
    entrada = models.CharField(max_length=5, default='08:00')
    intervalo = models.CharField(max_length=5, default='12:00')
    fimintervalo = models.CharField(max_length=5, default='13:00')
    saida = models.CharField(max_length=5, default='17:00')
    entradafs = models.CharField(max_length=5, default='08:00')
    intervalofs = models.CharField(max_length=5, blank=True, null=True)
    fimintervalofs = models.CharField(max_length=5, blank=True, null=True)
    saidafs = models.CharField(max_length=5, default='12:00')


class Funcionario(Base):
    cod = models.IntegerField()
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14)
    pis = models.CharField(max_length=14)
    admissao = models.DateField()
    salario = models.FloatField(blank=True, null=True)
    cargo = models.CharField(max_length=30)
    cbo = models.CharField(max_length=8)
    rg = models.CharField(max_length=15, blank=True, null=True)
    rgemiss = models.DateField(max_length=5, blank=True, null=True)
    rgorgao = models.CharField(max_length=5, blank=True, null=True)
    ctps = models.CharField(max_length=10)
    ctpsserie = models.CharField(max_length=5)
    ctpsdata = models.DateField(blank=True, null=True)
    ctpsuf = models.CharField(max_length=2)
    jornada = models.ForeignKey(Turno, on_delete=models.DO_NOTHING, default=7352)
    logradouro = models.CharField(max_length=100)
    num = models.CharField(max_length=10)
    bairro = models.CharField(max_length=50)
    cidade = models.CharField(max_length=70)
    uf = models.CharField(max_length=2)
    cep = models.IntegerField()
    datanasc = models.DateField()
    cidadenasc = models.CharField(max_length=100)
    ufnasc = models.CharField(max_length=2)
    genero = models.CharField(max_length=15)
    pai = models.CharField(max_length=100, blank=True, null=True)
    mae = models.CharField(max_length=100)
    demissao = models.DateField(blank=True, null=True)
    demitido = models.BooleanField()
    emp = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.cod} - {self.nome}'


class Obras(Base):
    emp = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING)
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


class Rubrica(models.Model):
    name = models.CharField(max_length=100)
    cod = models.IntegerField(unique=True)

    def __str__(self):
        return self.name


class Lancamento(models.Model):
    rub = models.ForeignKey(Rubrica, on_delete=models.CASCADE)
    func = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    comp = models.CharField(max_length=7)  # Format: 'YYYY-MM' (e.g., '2023-07')


class DiadeTrabalho(Base):
    func = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    entrou = models.BooleanField(default=False)
    inicioem = models.DateField()
    entrada = models.DateTimeField()
    intervalo = models.DateTimeField()
    fimintervalo = models.DateTimeField()
    saida = models.DateTimeField()
    encerrado = models.BooleanField(default=False)


class Ferias(Base):
    func = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    aviso = models.DateField(blank=True, null=True)
    inicio = models.DateField()
    final = models.DateField()


class Rescisao(Base):
    PTRA = '1'
    PIND = '2'
    DIND = '3'
    DTRA = '4'
    TEXP = '5'
    TEXPANT = '6'
    TEXPANTEMP = '7'
    JUST = '8'

    TIPOS = [
        (PTRA, 'Pedido Trabalhado'),
        (PIND, 'Pedido Indenizado'),
        (DIND, 'Dispensa Indenizada'),
        (DTRA, 'Dispensa Trabalhada'),
        (TEXP, 'Término Experiência'),
        (TEXPANT, 'Término Antecipado'),
        (TEXPANTEMP, 'Término Antecipado Empregado'),
        (JUST, 'Justa Causa'),
    ]

    func = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=2, choices=TIPOS)
    aviso = models.DateField(blank=True, null=True)
    inicio = models.DateField()
    final = models.DateField()


class Notas(Base):
    numero = models.IntegerField()
    canc = models.IntegerField()
    comp = models.DateField()
    valor = models.FloatField()
    inss = models.FloatField()
    iss = models.FloatField()
    tomador = models.ForeignKey(Obras, on_delete=models.DO_NOTHING)
    emp = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING)


class Alocacao(Base):
    emp = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING)
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


class TemAcesso(models.Model):
    escr = models.ManyToManyField(Escritorio)
    emp = models.ManyToManyField(Empresa)
    user = models.OneToOneField(Usuario, on_delete=models.DO_NOTHING)
    atualizado = models.DateField(auto_now=True)


class Imposto(Base):
    emp = models.ForeignKey(Empresa, on_delete=models.DO_NOTHING)
    nome = models.CharField(max_length=80)
    valor = models.FloatField()
    comp = models.DateField()
    vcto = models.DateField(null=True, blank=True)
    enviado = models.BooleanField(default=False)
    pago = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.emp} - {self.nome} - {self.valor} - {self.comp}'

class Pagamento(Base):
    func = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    pago = models.BooleanField(default=False)


class Holerite(Base):
    class Tipo(models.TextChoices):
        AD = 'ADIANTAMENTO'
        FM = 'FOLHA MENSAL'
        AD13 = 'ADIANTAMENTO 13º'
        FM13 = 'FOLHA MENSAL 13º'

    emp = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=18, choices=Tipo.choices)
    comp = models.DateField()
    enviado = models.BooleanField(default=False)
    funcs = models.ManyToManyField(Pagamento)