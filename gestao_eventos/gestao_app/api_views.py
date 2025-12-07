# gestao_app/api_views.py

from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from django.shortcuts import get_object_or_404

from .models import Evento, Inscricao, AuditLog # Importamos AuditLog
from .serializers import EventoSerializer, InscricaoSerializer

class ConsultaEventosThrottle(ScopedRateThrottle):
    scope = 'consulta_eventos'

class InscricaoThrottle(ScopedRateThrottle):
    scope = 'inscricao_participante'

# Helper para logar na API
def registrar_log_api(usuario, acao, detalhes):
    try:
        AuditLog.objects.create(usuario=usuario, acao=acao, detalhes=detalhes)
    except:
        pass

@api_view(['GET'])
@throttle_classes([ConsultaEventosThrottle])
@permission_classes([IsAuthenticated])
def listar_eventos_api(request):
    # LOG: Consulta
    registrar_log_api(request.user, 'API_CONSULTA', "Consultou lista de eventos via API")
    
    eventos = Evento.objects.all()
    serializer = EventoSerializer(eventos, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@throttle_classes([InscricaoThrottle])
@permission_classes([IsAuthenticated])
def inscrever_evento_api(request):
    serializer = InscricaoSerializer(data=request.data)
    
    if serializer.is_valid():
        evento_id = serializer.validated_data['evento_id']
        evento = get_object_or_404(Evento, id=evento_id)
        
        if not evento.tem_vagas():
            return Response({'erro': 'Vagas esgotadas.'}, status=status.HTTP_400_BAD_REQUEST)

        if Inscricao.objects.filter(usuario=request.user, evento=evento).exists():
             return Response({'erro': 'Já inscrito.'}, status=status.HTTP_400_BAD_REQUEST)

        Inscricao.objects.create(usuario=request.user, evento=evento)
        
        # LOG: Inscrição
        registrar_log_api(request.user, 'INSCRICAO', f"Inscrição via API no evento: {evento.nome}")

        return Response({'mensagem': 'Inscrição realizada!'}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)