# gestao_app/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid

class Usuario(AbstractUser):
    PERFIL_CHOICES = (
        ('ALUNO', 'Aluno'),
        ('PROFESSOR', 'Professor'),
        ('ORGANIZADOR', 'Organizador'),
    )
    telefone = models.CharField(max_length=15, blank=True, null=True, help_text="Telefone para contato")
    instituicao_ensino = models.CharField(max_length=100, blank=True, null=True, help_text="Instituição de ensino")
    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES, default='ALUNO')

    groups = models.ManyToManyField('auth.Group', related_name='usuario_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='usuario_set', blank=True)

    def __str__(self):
        return self.get_full_name() or self.username

class Evento(models.Model):
    TIPO_CHOICES = (
        ('SEMINARIO', 'Seminário'),
        ('PALESTRA', 'Palestra'),
        ('MINICURSO', 'Minicurso'),
        ('SEMANA_ACADEMICA', 'Semana Acadêmica'),
    )
    nome = models.CharField(max_length=200)
    tipo_evento = models.CharField(max_length=20, choices=TIPO_CHOICES)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    horario = models.TimeField(help_text="Horário de término do evento no último dia.")
    local = models.CharField(max_length=150)
    quantidade_participantes = models.PositiveIntegerField()
    
    organizador_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        limit_choices_to={'perfil__in': ['ORGANIZADOR', 'PROFESSOR']}
    )
    banner = models.ImageField(upload_to='banners/', blank=True, null=True, verbose_name="Banner do Evento")
    
    def clean(self):
        if self.data_inicio:
            if self.data_inicio < timezone.now().date():
                raise ValidationError({'data_inicio': 'A data de início não pode ser anterior à data atual.'})
        if self.data_inicio and self.data_fim:
            if self.data_fim < self.data_inicio:
                raise ValidationError({'data_fim': 'A data de término não pode ser anterior à data de início.'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def tem_vagas(self):
        return self.inscricao_set.count() < self.quantidade_participantes

    def __str__(self):
        return self.nome

class Inscricao(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    data_inscricao = models.DateTimeField(auto_now_add=True)
    certificado_liberado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('usuario', 'evento')

    def __str__(self):
        return f'{self.usuario} inscrito em {self.evento}'

class Certificado(models.Model):
    inscricao = models.OneToOneField(Inscricao, on_delete=models.CASCADE)
    codigo_validacao = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    data_emissao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Certificado para {self.inscricao.usuario} no evento {self.inscricao.evento}'

# --- NOVO: TABELA DE AUDITORIA ---
class AuditLog(models.Model):
    ACAO_CHOICES = (
        ('CRIACAO_USUARIO', 'Criação de Usuário'),
        ('LOGIN', 'Login no Sistema'),
        ('EVENTO_CRIAR', 'Cadastro de Evento'),
        ('EVENTO_EDITAR', 'Alteração de Evento'),
        ('EVENTO_EXCLUIR', 'Exclusão de Evento'),
        ('INSCRICAO', 'Inscrição em Evento'),
        ('CANCELAMENTO', 'Cancelamento de Inscrição'),
        ('CERTIFICADO_GERAR', 'Geração de Certificado'),
        ('API_CONSULTA', 'Consulta via API'),
    )
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    acao = models.CharField(max_length=50, choices=ACAO_CHOICES)
    detalhes = models.TextField(blank=True, null=True)
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.data_hora}] {self.usuario} - {self.acao}"