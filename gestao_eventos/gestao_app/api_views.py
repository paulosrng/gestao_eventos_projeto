# gestao_app/api_views.py

from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from django.shortcuts import get_object_or_404

# Importando os modelos e serializers corretos
from .models import Evento, Inscricao
from .serializers import EventoSerializer, InscricaoSerializer

# --- Classes de Limite (Throttling) ---
class ConsultaEventosThrottle(ScopedRateThrottle):
    scope = 'consulta_eventos'

class InscricaoThrottle(ScopedRateThrottle):
    scope = 'inscricao_participante'

# --- Views da API ---

# 3.1 Consulta de Eventos
@api_view(['GET'])
@throttle_classes([ConsultaEventosThrottle])
@permission_classes([IsAuthenticated])
def listar_eventos_api(request):
    """
    Retorna a lista de eventos disponíveis.
    """
    eventos = Evento.objects.all()
    serializer = EventoSerializer(eventos, many=True)
    return Response(serializer.data)

# 3.2 Inscrição de Participantes
@api_view(['POST'])
@throttle_classes([InscricaoThrottle])
@permission_classes([IsAuthenticated])
def inscrever_evento_api(request):
    """
    Permite que o utilizador autenticado se inscreva num evento.
    """
    serializer = InscricaoSerializer(data=request.data)
    
    if serializer.is_valid():
        evento_id = serializer.validated_data['evento_id']
        evento = get_object_or_404(Evento, id=evento_id)
        
        # 1. Regra de Negócio: Verificar vagas
        # Agora funciona porque adicionamos o método no models.py
        if not evento.tem_vagas():
            return Response(
                {'erro': 'Vagas esgotadas para este evento.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Regra de Negócio: Não permitir inscrição duplicada
        # Verificamos na tabela Inscricao se esse par (usuario, evento) já existe
        if Inscricao.objects.filter(usuario=request.user, evento=evento).exists():
             return Response(
                 {'erro': 'Você já está inscrito neste evento.'}, 
                 status=status.HTTP_400_BAD_REQUEST
             )

        # 3. Realizar a inscrição
        # Criamos o objeto na tabela intermediária explicitamente
        Inscricao.objects.create(usuario=request.user, evento=evento)

        return Response(
            {'mensagem': 'Inscrição realizada com sucesso!'}, 
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)