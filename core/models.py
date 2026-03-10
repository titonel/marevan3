from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import date


# 1. Usuário Completo (Idêntico ao banco já gerado)
class Usuario(AbstractUser):
    mudar_senha = models.BooleanField(default=False, verbose_name="Forçar Troca de Senha")
    email_verificado = models.BooleanField(default=False, verbose_name="Email Verificado")

    TIPO_PROFISSIONAL_CHOICES = [
        ('MED', 'Médico'),
        ('ENF', 'Enfermeiro'),
        ('FAR', 'Farmacêutico'),
        ('ADM', 'Administrativo'),
    ]

    TIPO_REGISTRO_CHOICES = [('CRM', 'CRM'), ('COREN', 'COREN'), ('CRF', 'CRF')]

    tipo_profissional = models.CharField(max_length=3, choices=TIPO_PROFISSIONAL_CHOICES, null=True, blank=True)
    tipo_registro = models.CharField(max_length=10, choices=TIPO_REGISTRO_CHOICES, null=True, blank=True)
    registro_profissional = models.CharField(max_length=20, null=True, blank=True)
    drt = models.CharField(max_length=20, null=True, blank=True, verbose_name="DRT / Matrícula")

    def __str__(self):
        return self.get_full_name() or self.username


# 2. Paciente (Mapeado com o banco legado)
class Paciente(models.Model):
    nome = models.CharField(max_length=100)
    cross = models.IntegerField(null=True, blank=True, unique=True)
    cpf = models.CharField(max_length=11, null=True, blank=True, unique=True)
    sexo = models.IntegerField(null=True, blank=True)
    data_nascimento = models.DateField()
    municipio = models.CharField(max_length=100, null=True, blank=True)
    indicacao = models.CharField(max_length=200, null=True, blank=True)
    medico = models.CharField(max_length=100, null=True, blank=True)
    meta = models.IntegerField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    data_insercao = models.DateTimeField(default=timezone.now)
    data_alta = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nome


# 3. Medição (Mapeado com o banco legado)
class Medicao(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='medicoes')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name="Profissional Responsável")

    valor_inr = models.FloatField()
    data_medicao = models.DateTimeField(default=timezone.now)
    intercorrencia = models.BooleanField(default=False)
    intercorrencia_txt = models.TextField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ['-data_medicao']