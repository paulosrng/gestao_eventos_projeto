# gestao_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import io
from django.utils import timezone
from datetime import datetime
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from .models import Evento, Inscricao, Usuario, AuditLog
from .forms import UserCreationForm, LoginForm, EventoForm

# --- Funções Auxiliares ---

def is_evento_finalizado(evento):
    if not evento.data_fim:
        return False
    return evento.data_fim < timezone.now().date()

def registrar_log(usuario, acao, detalhes=""):
    """Salva uma ação na tabela de auditoria."""
    try:
        AuditLog.objects.create(
            usuario=usuario if usuario.is_authenticated else None,
            acao=acao,
            detalhes=detalhes
        )
    except Exception as e:
        print(f"Erro ao salvar log: {e}")

# --- Views Públicas e de Autenticação ---

def listar_eventos(request):
    eventos = Evento.objects.all().order_by('data_inicio')
    eventos_inscritos_ids = []
    if request.user.is_authenticated:
        eventos_inscritos_ids = Inscricao.objects.filter(usuario=request.user).values_list('evento_id', flat=True)
    
    contexto = {
        'eventos': eventos,
        'eventos_inscritos_ids': list(eventos_inscritos_ids)
    }
    return render(request, 'gestao_app/listar_eventos.html', contexto)

def cadastro_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False 
            user.save()

            # LOG
            registrar_log(user, 'CRIACAO_USUARIO', f"Novo cadastro: {user.username}")

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            link_ativacao = request.build_absolute_uri(f'/ativar/{uid}/{token}/')

            print("\n" + "="*60)
            print(" [SIMULAÇÃO DE EMAIL ENVIADO] ".center(60, "="))
            print(" De: sistema@sgea.com.br")
            print(f" Para: {user.email}")
            print("-" * 60)
            print(" Assunto: Confirmação de Cadastro - SGEA")
            print("-" * 60)
            print("")
            print("  🎓 SGEA  (Sistema de Gestão de Eventos Acadêmicos)")
            print("")
            print(f"  Olá, {user.first_name}!")
            print("")
            print("  Seja bem-vindo(a) ao sistema.")
            print("  Para ativar sua conta, clique no link abaixo:")
            print("")
            print(f"  {link_ativacao}")
            print("")
            print("="*60 + "\n")

            assunto = 'Confirmação de Cadastro - SGEA'
            try:
                html_message = render_to_string('gestao_app/email_confirmacao.html', {
                    'user': user,
                    'link': link_ativacao,
                })
                plain_message = strip_tags(html_message)
            except:
                html_message = None
                plain_message = f"Link: {link_ativacao}"
            
            send_mail(assunto, plain_message, settings.EMAIL_HOST_USER, [user.email], html_message=html_message)

            return redirect('cadastro_sucesso')
        else:
            messages.error(request, 'Ocorreram erros no formulário.')
    else:
        form = UserCreationForm()
    return render(request, 'gestao_app/cadastro.html', {'form': form})

def cadastro_sucesso(request):
    return render(request, 'gestao_app/aguardando_confirmacao.html')

def ativar_conta(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Sua conta foi ativada com sucesso! Faça login.')
        return redirect('login')
    else:
        messages.error(request, 'O link de ativação é inválido ou expirou.')
        return redirect('login')

def login_usuario(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                # LOG
                registrar_log(user, 'LOGIN', "Usuário realizou login")
                return redirect('listar_eventos')
            else:
                usuario_existe = Usuario.objects.filter(username=username).first()
                if usuario_existe and not usuario_existe.is_active:
                    messages.error(request, 'Sua conta ainda não foi ativada. Verifique o link no terminal.')
                else:
                    messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = LoginForm()
    return render(request, 'gestao_app/login.html', {'form': form})

@login_required
def logout_usuario(request):
    logout(request)
    return redirect('listar_eventos')

# --- Views de Inscrição (ALUNO E PROFESSOR) ---

@login_required
def inscrever_evento(request, evento_id):
    if request.user.perfil == 'ORGANIZADOR':
        messages.error(request, 'Organizadores não podem se inscrever em eventos.')
        return redirect('listar_eventos')

    evento = get_object_or_404(Evento, id=evento_id)
    
    if is_evento_finalizado(evento):
        messages.error(request, 'Não é possível se inscrever em eventos finalizados.')
        return redirect('listar_eventos')
    
    if not evento.tem_vagas():
        messages.error(request, 'Vagas esgotadas para este evento.')
        return redirect('listar_eventos')

    if Inscricao.objects.filter(usuario=request.user, evento=evento).exists():
        messages.warning(request, 'Você já está inscrito neste evento.')
        return redirect('listar_eventos')
        
    Inscricao.objects.create(usuario=request.user, evento=evento)
    
    # LOG
    registrar_log(request.user, 'INSCRICAO', f"Inscreveu-se no evento: {evento.nome}")
    
    messages.success(request, f'Inscrição no evento "{evento.nome}" realizada com sucesso!')
    return redirect('listar_eventos')

@login_required
def cancelar_inscricao(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    inscricao = get_object_or_404(Inscricao, usuario=request.user, evento=evento)
    
    if is_evento_finalizado(evento):
        messages.error(request, 'Não é possível cancelar inscrição de eventos já finalizados.')
    else:
        # LOG
        registrar_log(request.user, 'CANCELAMENTO', f"Cancelou inscrição no evento: {evento.nome}")
        inscricao.delete()
        messages.success(request, f'Inscrição no evento "{evento.nome}" cancelada.')
        
    return redirect('listar_eventos')

@login_required
def minhas_inscricoes(request):
    inscricoes = Inscricao.objects.filter(usuario=request.user).select_related('evento')
    for inscricao in inscricoes:
        inscricao.evento_finalizado = is_evento_finalizado(inscricao.evento)
    return render(request, 'gestao_app/minhas_inscricoes.html', {'inscricoes': inscricoes})

# --- Views do ORGANIZADOR (Gestão de Eventos) ---

@login_required
def criar_evento(request):
    if request.user.perfil != 'ORGANIZADOR':
        messages.error(request, 'Acesso negado. Apenas organizadores podem criar eventos.')
        return redirect('listar_eventos')

    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES) 
        if form.is_valid():
            try:
                evento = form.save()
                # LOG
                registrar_log(request.user, 'EVENTO_CRIAR', f"Criou o evento: {evento.nome}")
                messages.success(request, 'Evento criado com sucesso!')
                return redirect('meus_eventos')
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = EventoForm()
    return render(request, 'gestao_app/criar_evento.html', {'form': form})

@login_required
def editar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    
    if request.user.perfil != 'ORGANIZADOR':
        messages.error(request, 'Você não tem permissão para editar este evento.')
        return redirect('listar_eventos')
        
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            try:
                form.save()
                # LOG
                registrar_log(request.user, 'EVENTO_EDITAR', f"Editou o evento: {evento.nome}")
                messages.success(request, 'Evento atualizado com sucesso!')
                return redirect('meus_eventos')
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = EventoForm(instance=evento)
    
    return render(request, 'gestao_app/criar_evento.html', {'form': form, 'titulo': 'Editar Evento'})

@login_required
def excluir_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    
    if request.user.perfil != 'ORGANIZADOR':
        messages.error(request, 'Você não tem permissão para excluir este evento.')
    else:
        nome_evento = evento.nome
        try:
            evento.delete()
            # LOG
            registrar_log(request.user, 'EVENTO_EXCLUIR', f"Excluiu o evento: {nome_evento}")
            messages.success(request, 'Evento excluído com sucesso.')
        except Exception as e:
            messages.error(request, 'Não foi possível excluir. Existem inscrições vinculadas.')
        
    return redirect('meus_eventos')

@login_required
def meus_eventos(request):
    if request.user.perfil != 'ORGANIZADOR':
        messages.error(request, 'Apenas organizadores podem acessar o painel de gestão.')
        return redirect('listar_eventos')
    
    eventos = Evento.objects.all().order_by('-data_inicio')
    for evento in eventos:
        evento.finalizado = is_evento_finalizado(evento)
    
    return render(request, 'gestao_app/meus_eventos.html', {'eventos': eventos})

@login_required
def gerenciar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    
    if request.user.perfil != 'ORGANIZADOR':
        return redirect('listar_eventos')

    if not is_evento_finalizado(evento):
        messages.warning(request, 'Você só pode gerir presenças de eventos que já ocorreram.')

    if request.method == 'POST':
        Inscricao.objects.filter(evento=evento).update(certificado_liberado=False)
        inscricoes_a_liberar_ids = request.POST.getlist('inscricao_id')
        
        if inscricoes_a_liberar_ids:
            Inscricao.objects.filter(id__in=inscricoes_a_liberar_ids, evento=evento).update(certificado_liberado=True)
        
        messages.success(request, 'Lista de presença atualizada!')
        return redirect('gerenciar_evento', evento_id=evento.id)

    inscricoes = Inscricao.objects.filter(evento=evento).select_related('usuario')
    return render(request, 'gestao_app/gerenciar_evento.html', {'evento': evento, 'inscricoes': inscricoes})

@login_required
def cadastrar_participante(request):
    if request.user.perfil != 'ORGANIZADOR':
        messages.error(request, 'Acesso negado.')
        return redirect('listar_eventos')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True 
            user.save()
            
            # LOG
            registrar_log(request.user, 'CRIACAO_USUARIO', f"Cadastrou manualmente: {user.username}")
            
            messages.success(request, f'Participante {user.username} cadastrado com sucesso!')
            return redirect('meus_eventos')
    else:
        form = UserCreationForm()
    
    return render(request, 'gestao_app/cadastro_interno.html', {'form': form})

# --- Views de Certificado ---

@login_required
def detalhe_certificado(request, inscricao_id):
    inscricao = get_object_or_404(Inscricao, id=inscricao_id, usuario=request.user)
    
    if not inscricao.certificado_liberado:
        messages.error(request, 'Sua presença não foi confirmada neste evento.')
        return redirect('minhas_inscricoes')
        
    if not is_evento_finalizado(inscricao.evento):
        messages.warning(request, 'O certificado só estará disponível após o término do evento.')
        return redirect('minhas_inscricoes')

    # LOG
    registrar_log(request.user, 'CERTIFICADO_GERAR', f"Visualizou certificado: {inscricao.evento.nome}")

    return render(request, 'gestao_app/detalhe_certificado.html', {'inscricao': inscricao})

@login_required
def gerar_pdf_certificado(request, inscricao_id):
    inscricao = get_object_or_404(Inscricao, id=inscricao_id, usuario=request.user)
    
    if not inscricao.certificado_liberado or not is_evento_finalizado(inscricao.evento):
        messages.error(request, 'Certificado indisponível no momento.')
        return redirect('minhas_inscricoes')
    
    # LOG
    registrar_log(request.user, 'CERTIFICADO_GERAR', f"Baixou PDF: {inscricao.evento.nome}")

    buffer = io.BytesIO()
    from reportlab.lib.pagesizes import landscape
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)
    
    p.setStrokeColorRGB(0.2, 0.4, 0.8)
    p.setLineWidth(5)
    p.rect(30, 30, width-60, height-60)
    
    p.setFont("Helvetica-Bold", 36)
    p.drawCentredString(width / 2.0, height - 120, "CERTIFICADO DE PARTICIPAÇÃO")
    
    p.setFont("Helvetica", 16)
    p.drawCentredString(width / 2.0, height - 180, "Certificamos que")
    
    p.setFont("Helvetica-Bold", 28)
    nome_usuario = inscricao.usuario.get_full_name() or inscricao.usuario.username
    p.drawCentredString(width / 2.0, height - 230, nome_usuario.upper())
    
    p.setFont("Helvetica", 16)
    p.drawCentredString(width / 2.0, height - 280, f"Participou com êxito do evento:")
    
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2.0, height - 310, f"\"{inscricao.evento.nome}\"")
    
    p.setFont("Helvetica", 14)
    data_fmt = inscricao.evento.data_inicio.strftime('%d/%m/%Y')
    p.drawCentredString(width / 2.0, height - 350, f"Realizado em {data_fmt}")
    
    p.setLineWidth(1)
    p.setStrokeColorRGB(0, 0, 0)
    p.line(width/2 - 150, 100, width/2 + 150, 100)
    
    p.setFont("Helvetica-Oblique", 12)
    organizador = inscricao.evento.organizador_responsavel.get_full_name() or "Coordenação SGEA"
    p.drawCentredString(width / 2.0, 80, f"{organizador}")
    p.drawCentredString(width / 2.0, 65, "Responsável Técnico / Organizador")
    
    p.setFont("Helvetica", 9)
    p.setFillColorRGB(0.5, 0.5, 0.5)
    p.drawString(40, 40, f"Autenticação: REF-{inscricao.id}-{inscricao.evento.id}")

    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"certificado_{inscricao.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

# --- RELATÓRIO DE AUDITORIA (NOVO) ---
@login_required
def relatorio_auditoria(request):
    if request.user.perfil != 'ORGANIZADOR':
        messages.error(request, 'Acesso negado.')
        return redirect('listar_eventos')
    
    logs = AuditLog.objects.all().order_by('-data_hora')
    
    # Filtros
    data_filtro = request.GET.get('data')
    usuario_filtro = request.GET.get('usuario')
    
    if data_filtro:
        logs = logs.filter(data_hora__date=data_filtro)
    
    if usuario_filtro:
        logs = logs.filter(usuario__username__icontains=usuario_filtro)

    return render(request, 'gestao_app/relatorio_auditoria.html', {
        'logs': logs,
        'data_filtro': data_filtro,
        'usuario_filtro': usuario_filtro
    })