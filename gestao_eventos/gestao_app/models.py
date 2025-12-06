from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid

class Usuario(AbstractUser):
    """
    Modelo de usuário customizado que herda de AbstractUser.
    Adiciona campos como telefone, instituição e perfil.
    """
    PERFIL_CHOICES = (
        ('ALUNO', 'Aluno'),
        ('PROFESSOR', 'Professor'),
        ('ORGANIZADOR', 'Organizador'),
    )
    telefone = models.CharField(max_length=15, blank=True, null=True, help_text="Telefone para contato")
    instituicao_ensino = models.CharField(max_length=100, blank=True, null=True, help_text="Instituição de ensino do usuário (obrigatório para Alunos e Professores)")
    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES, default='ALUNO')

    # Mantém os related_name para resolver o conflito com o auth.User padrão do Django.
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_set',
        blank=True,
    )

    def __str__(self):
        return self.get_full_name() or self.username

class Evento(models.Model):
    """
    Modelo para armazenar informações sobre os eventos acadêmicos.
    """
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
    # Revertido para usar PROTECT, que é mais seguro para não apagar eventos se o organizador for removido.
    organizador_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        limit_choices_to={'perfil': 'ORGANIZADOR'}
    )
    banner = models.ImageField(upload_to='banners/', blank=True, null=True, verbose_name="Banner do Evento")
    
    def __str__(self):
        return self.nome

class Inscricao(models.Model):
    """
    Modelo para vincular um usuário a um evento (inscrição).
    """
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    data_inscricao = models.DateTimeField(auto_now_add=True)
    # Campo essencial para a nova funcionalidade de liberação manual.
    certificado_liberado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('usuario', 'evento')

    def __str__(self):
        return f'{self.usuario} inscrito em {self.evento}'

class Certificado(models.Model):
    """
    Modelo para gerar e armazenar os certificados dos participantes.
    """
    inscricao = models.OneToOneField(Inscricao, on_delete=models.CASCADE)
    # Revertido para usar UUIDField, que é uma ótima escolha para códigos de validação.
    codigo_validacao = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    data_emissao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Certificado para {self.inscricao.usuario} no evento {self.inscricao.evento}'


