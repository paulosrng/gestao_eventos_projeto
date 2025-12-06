from django.core.management.base import BaseCommand
from gestao_app.models import Usuario

class Command(BaseCommand):
    help = 'Cria os dados iniciais (Seeding) conforme requisitos do projeto'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando carga de dados...'))

        # Lista de usuários conforme o pedido
        # Formato: (Nome, Email/Login, Senha, Perfil)
        dados_usuarios = [
            (
                'Usuário Organizador', 
                'organizador@sgea.com', 
                'Admin@123', 
                'ORGANIZADOR'
            ),
            (
                'Usuário Aluno', 
                'aluno@sgea.com', 
                'Aluno@123', 
                'PARTICIPANTE'
            ),
            (
                'Usuário Professor', 
                'professor@sgea.com', 
                'Professor@123', 
                'PARTICIPANTE'
            ),
        ]

        for nome, email, senha, perfil in dados_usuarios:
            if not Usuario.objects.filter(email=email).exists():
                usuario = Usuario.objects.create_user(
                    username=email, 
                    email=email,
                    password=senha,
                    first_name=nome.split()[0],
                    last_name=' '.join(nome.split()[1:])
                )
                
                # Define o perfil
                usuario.perfil = perfil
                
                # Se for organizador, dá permissão total (Admin do Django)
                if perfil == 'ORGANIZADOR':
                    usuario.is_staff = True
                    usuario.is_superuser = True
                
                usuario.save()
                
                self.stdout.write(self.style.SUCCESS(f'[OK] Criado: {email} ({perfil})'))
            else:
                self.stdout.write(self.style.WARNING(f'[!] Já existe: {email}'))

        self.stdout.write(self.style.SUCCESS('-' * 30))
        self.stdout.write(self.style.SUCCESS('Carga inicial concluída com sucesso!'))