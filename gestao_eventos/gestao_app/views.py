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

# Certifique-se que seus models e forms existem conforme importados
from .models import Evento, Inscricao, Usuario
from .forms import UserCreationForm, LoginForm, EventoForm

# --- Funções Auxiliares ---

def is_evento_finalizado(evento):
    """Verifica se a data de fim do evento já passou."""
    if not evento.data_fim:
        return False
    return evento.data_fim < timezone.now().date()

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
            user = form.save()
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('listar_eventos')
        else:
            messages.error(request, 'Ocorreram erros no formulário. Por favor, corrija-os.')
    else:
        form = UserCreationForm()
    return render(request, 'gestao_app/cadastro.html', {'form': form})

def login_usuario(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('listar_eventos')
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = LoginForm()
    return render(request, 'gestao_app/login.html', {'form': form})

@login_required
def logout_usuario(request):
    logout(request)
    return redirect('listar_eventos')

# --- Views de Inscrição (Usuário) ---

@login_required
def inscrever_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    if is_evento_finalizado(evento):
        messages.error(request, 'Não é possível se inscrever em eventos finalizados.')
        return redirect('listar_eventos')
        
    Inscricao.objects.get_or_create(usuario=request.user, evento=evento)
    messages.success(request, f'Inscrição no evento "{evento.nome}" realizada com sucesso!')
    return redirect('listar_eventos')

@login_required
def cancelar_inscricao(request, evento_id):
    """View adicionada: permite ao usuário sair do evento."""
    evento = get_object_or_404(Evento, id=evento_id)
    inscricao = get_object_or_404(Inscricao, usuario=request.user, evento=evento)
    
    if is_evento_finalizado(evento):
        messages.error(request, 'Não é possível cancelar inscrição de eventos já finalizados.')
    else:
        inscricao.delete()
        messages.success(request, f'Inscrição no evento "{evento.nome}" cancelada.')
        
    return redirect('listar_eventos')

@login_required
def minhas_inscricoes(request):
    inscricoes = Inscricao.objects.filter(usuario=request.user).select_related('evento')
    for inscricao in inscricoes:
        inscricao.evento_finalizado = is_evento_finalizado(inscricao.evento)
    contexto = { 'inscricoes': inscricoes }
    return render(request, 'gestao_app/minhas_inscricoes.html', contexto)

# --- Views do Organizador (Gestão de Eventos) ---

@login_required
def criar_evento(request):
    # ... verificações de permissão ...
    if request.method == 'POST':
        # ADICIONADO: request.FILES
        form = EventoForm(request.POST, request.FILES) 
        if form.is_valid():
            evento = form.save(commit=False)
            evento.organizador_responsavel = request.user
            evento.save()
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('meus_eventos')
    else:
        form = EventoForm()
    return render(request, 'gestao_app/criar_evento.html', {'form': form})

@login_required
def editar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    
    if evento.organizador_responsavel != request.user:
        messages.error(request, 'Você não tem permissão para editar este evento.')
        return redirect('listar_eventos')
        
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento atualizado com sucesso!')
            return redirect('meus_eventos')
    else:
        form = EventoForm(instance=evento)
    
    return render(request, 'gestao_app/criar_evento.html', {'form': form, 'titulo': 'Editar Evento'})

@login_required
def excluir_evento(request, evento_id):
    """View adicionada: permite excluir eventos."""
    evento = get_object_or_404(Evento, id=evento_id)
    
    if evento.organizador_responsavel != request.user:
        messages.error(request, 'Você não tem permissão para excluir este evento.')
    else:
        evento.delete()
        messages.success(request, 'Evento excluído com sucesso.')
        
    return redirect('meus_eventos')

@login_required
def meus_eventos(request):
    if getattr(request.user, 'perfil', '') != 'ORGANIZADOR':
        messages.error(request, 'Apenas organizadores podem acessar esta página.')
        return redirect('listar_eventos')
    
    eventos = Evento.objects.filter(organizador_responsavel=request.user).order_by('-data_inicio')
    for evento in eventos:
        evento.finalizado = is_evento_finalizado(evento)
    
    return render(request, 'gestao_app/meus_eventos.html', {'eventos': eventos})

@login_required
def gerenciar_evento(request, evento_id):
    """Gerencia a emissão de certificados."""
    evento = get_object_or_404(Evento, id=evento_id, organizador_responsavel=request.user)
    
    if not is_evento_finalizado(evento):
        messages.warning(request, 'Você só pode gerir certificados de eventos que já ocorreram.')
       

    if request.method == 'POST':
       
        Inscricao.objects.filter(evento=evento).update(certificado_liberado=False)
        
        # 2. Pegamos os IDs marcados no formulário
        inscricoes_a_liberar_ids = request.POST.getlist('inscricao_id')
        
        # 3. Atualizamos apenas os marcados para True
        if inscricoes_a_liberar_ids:
            Inscricao.objects.filter(id__in=inscricoes_a_liberar_ids, evento=evento).update(certificado_liberado=True)
        
        messages.success(request, 'Status dos certificados atualizado com sucesso!')
        return redirect('gerenciar_evento', evento_id=evento.id)

    inscricoes = Inscricao.objects.filter(evento=evento).select_related('usuario')
    return render(request, 'gestao_app/gerenciar_evento.html', {'evento': evento, 'inscricoes': inscricoes})

# --- Views de Certificado ---

@login_required
def detalhe_certificado(request, inscricao_id):
    inscricao = get_object_or_404(Inscricao, id=inscricao_id, usuario=request.user)
    if not inscricao.certificado_liberado:
        messages.error(request, 'O certificado para este evento ainda não foi liberado.')
        return redirect('minhas_inscricoes')
    return render(request, 'gestao_app/detalhe_certificado.html', {'inscricao': inscricao})

@login_required
def gerar_pdf_certificado(request, inscricao_id):
    inscricao = get_object_or_404(Inscricao, id=inscricao_id, usuario=request.user)
    
    if not inscricao.certificado_liberado:
        messages.error(request, 'O certificado não está disponível para download.')
        return redirect('minhas_inscricoes')
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Design do PDF
    p.setTitle(f"Certificado - {inscricao.evento.nome}")
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width / 2.0, height - 2 * inch, "Certificado de Participação")
    
    texto = p.beginText(1.5 * inch, height - 3.5 * inch)
    texto.setFont("Helvetica", 12)
    texto.textLine("Certificamos que")
    texto.moveCursor(0, 0.5 * inch)
    
    texto.setFont("Helvetica-Bold", 14)
    # Usa get_full_name se existir, senão usa o username
    nome_usuario = inscricao.usuario.get_full_name() or inscricao.usuario.username
    texto.textLine(f"{nome_usuario}")
    
    texto.moveCursor(0, 0.5 * inch)
    texto.setFont("Helvetica", 12)
    texto.textLine(f"participou no evento \"{inscricao.evento.nome}\",")
    
    data_formatada = inscricao.evento.data_inicio.strftime('%d/%m/%Y')
    texto.textLine(f"realizado em {data_formatada},")
    
    organizador_nome = inscricao.evento.organizador_responsavel.get_full_name() or "Organização"
    texto.textLine(f"organizado por {organizador_nome}.")
    
    p.drawText(texto)
    
    # Linha de assinatura
    p.line(3 * inch, 2.5 * inch, 5.5 * inch, 2.5 * inch)
    p.drawCentredString(4.25 * inch, 2.25 * inch, "Assinatura do Organizador")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"certificado_{inscricao.evento.id}_{inscricao.usuario.id}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response