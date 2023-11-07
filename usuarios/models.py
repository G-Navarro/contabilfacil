from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UsuarioManager(BaseUserManager):
    def create_user(self, email, fone, usuario, nome, snome, password, **other_fields):
        if not None:
            email = self.normalize_email(email)
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_active', True)
        user = self.model(email=email, fone=fone, usuario=usuario, nome=nome, snome=snome, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, fone, usuario, nome, snome, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, fone, usuario, nome, snome, password, **other_fields)
    
    #SUPERVISOR ESCRITORIO
    def create_supervisor(self, email, fone, usuario, nome, snome, password, **other_fields):
        other_fields.setdefault('eh_supervisor', True)
        return self.create_user(email, fone, usuario, nome, snome, password, **other_fields)

    #GERENTE É O RESPONSAVEL POR UMA OU MAIS EMPRESAS
    def create_gerente(self, email, fone, usuario, nome, snome, password, **other_fields):
        other_fields.setdefault('eh_gerente', True)
        return self.create_user(email, fone, usuario, nome, snome, password, **other_fields)    
    
    #AUXILIAR DO GERENTE DE ALGUMA EMPRESA
    def create_auxiliar(self, email, fone, usuario, nome, snome, password, **other_fields):
        other_fields.setdefault('eh_auxiliar', True)
        return self.create_user(email, fone, usuario, nome, snome, password, **other_fields)
    
    #PERMITE FUNCIONARIO MARCAR PONTO
    def create_funcionario(self, usuario, nome, snome, password, email=None, fone=None, **other_fields):
        other_fields.setdefault('eh_funcionario', True)
        return self.create_user(email, fone, usuario, nome, snome, password, **other_fields)



class Usuario(AbstractBaseUser, PermissionsMixin):
    usuario = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=50)
    snome = models.CharField(max_length=50)
    email = models.EmailField(_('email address'), null=True, blank=True)
    fone = models.IntegerField(null=True, blank=True)
    eh_supervisor = models.BooleanField(default=False)
    eh_gerente = models.BooleanField(default=False)
    eh_auxiliar = models.BooleanField(default=False)
    eh_funcionario = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'usuario'
    REQUIRED_FIELDS = ['nome', 'snome', 'email', 'fone']

    def __str__(self):
        return self.usuario
