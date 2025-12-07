from django.urls import path
from . import views
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token # Importação para o Token
from . import views      # Suas views normais do site
from . import api_views  # As novas views da API

urlpatterns = [
    path('', views.listar_eventos, name='listar_eventos'),
    path('cadastro/', views.cadastro_usuario, name='cadastrar_usuario'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),

    path('minhas-inscricoes/', views.minhas_inscricoes, name='minhas_inscricoes'),
    path('evento/<int:evento_id>/inscrever/', views.inscrever_evento, name='inscrever_evento'),
    
    path('evento/<int:evento_id>/cancelar/', views.cancelar_inscricao, name='cancelar_inscricao'),

    path('meus-eventos/', views.meus_eventos, name='meus_eventos'),
    path('evento/criar/', views.criar_evento, name='criar_evento'),
    path('evento/editar/<int:evento_id>/', views.editar_evento, name='editar_evento'),
    
    path('evento/excluir/<int:evento_id>/', views.excluir_evento, name='excluir_evento'),
    
    path('evento/<int:evento_id>/gerenciar/', views.gerenciar_evento, name='gerenciar_evento'),

    path('certificado/<int:inscricao_id>/', views.detalhe_certificado, name='detalhe_certificado'),
    path('certificado/<int:inscricao_id>/gerar-pdf/', views.gerar_pdf_certificado, name='gerar_pdf_certificado'),

    # --- NOVAS ROTAS DA API (Adicionadas) ---
    # Endpoint para pegar o Token (Login da API)
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    
    # Endpoints da API (Consultar e Inscrever)
    path('api/eventos/', api_views.listar_eventos_api, name='api_listar_eventos'),
    path('api/inscrever/', api_views.inscrever_evento_api, name='api_inscrever'),

]