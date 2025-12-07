# gestao_app/api_views.py

from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle # <--- Importação importante
from django.shortcuts import get_object_or_404
from .models import Evento
from .serializers import EventoSerializer, InscricaoSerializer

# --- Classes de Limite (Throttling) ---
# Estas classes ligam as views às regras '20/day' e '50/day' do settings.py

class ConsultaEventosThrottle(ScopedRateThrottle):
    scope = 'consulta_eventos'

class InscricaoThrottle(ScopedRateThrottle):
    scope = 'inscricao_participante'

# --- Views da API ---

# 3.1 Consulta de Eventos
@api_view(['GET'])
@throttle_classes([ConsultaEventosThrottle]) # Agora usamos a classe correta
def listar_eventos_api(request):
    """
    Retorna a lista de eventos disponíveis.
    """
    eventos = Evento.objects.all()
    serializer = EventoSerializer(eventos, many=True)
    return Response(serializer.data)

# 3.2 Inscrição de Participantes
@api_view(['POST'])
@throttle_classes([InscricaoThrottle]) # Agora usamos a classe correta
def inscrever_evento_api(request):
    """
    Permite que o utilizador autenticado se inscreva num evento.
    """
    # Verifica se o utilizador está autenticado (caso o permission_classes global falhe)
    if not request.user.is_authenticated:
        return Response({'erro': 'Autenticação necessária.'}, status=status.HTTP_401_UNAUTHORIZED)

    serializer = InscricaoSerializer(data=request.data)
    if serializer.is_valid():
        evento_id = serializer.validated_data['evento_id']
        evento = get_object_or_404(Evento, id=evento_id)
        
        # Regra de Negócio: Verificar vagas
        if not evento.tem_vagas():
            return Response({'erro': 'Vagas esgotadas para este evento.'}, status=status.HTTP_400_BAD_REQUEST)

        # Regra de Negócio: Não permitir inscrição duplicada
        # (Assumindo que você tem o related_name='eventos_participante' ou similar no User)
        # Se não tiver certeza, podemos usar evento.inscricoes.filter(usuario=request.user).exists()
        # Vou usar uma verificação genérica aqui. Se der erro, me avise sobre o seu modelo de Inscrição.
        if evento.participantes.filter(id=request.user.id).exists():
             return Response({'erro': 'Você já está inscrito neste evento.'}, status=status.HTTP_400_BAD_REQUEST)

        evento.participantes.add(request.user)
        return Response({'mensagem': 'Inscrição realizada com sucesso!'}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)