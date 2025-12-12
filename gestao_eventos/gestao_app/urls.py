from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views      # Views do site (HTML)
from . import api_views  # Views da API

urlpatterns = [
    # --- ROTAS DO SITE (HTML) ---
    path('cadastro/sucesso/', views.cadastro_sucesso, name='cadastro_sucesso'),
    path('ativar/<uidb64>/<token>/', views.ativar_conta, name='ativar_conta'),
    path('', views.listar_eventos, name='listar_eventos'),
    path('cadastro/', views.cadastro_usuario, name='cadastrar_usuario'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('cadastrar-participante/', views.cadastrar_participante, name='cadastrar_participante'),
    path('auditoria/', views.relatorio_auditoria, name='relatorio_auditoria'),
    
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

    # --- ROTAS DA API ---
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/eventos/', api_views.listar_eventos_api, name='api_listar_eventos'),
    path('api/inscrever/', api_views.inscrever_evento_api, name='api_inscrever'),
]