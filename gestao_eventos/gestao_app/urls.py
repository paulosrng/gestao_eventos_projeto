from django.urls import path
from . import views

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
]