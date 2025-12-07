# gestao_app/serializers.py

from rest_framework import serializers
from .models import Evento

class EventoSerializer(serializers.ModelSerializer):
    # 'titulo' lê do campo 'nome'
    titulo = serializers.CharField(source='nome', read_only=True)
    
    # 'organizador' lê do campo 'organizador_responsavel'
    organizador = serializers.StringRelatedField(source='organizador_responsavel')
    
    # 'vagas' lê do campo 'quantidade_participantes'
    vagas = serializers.IntegerField(source='quantidade_participantes', read_only=True)

    # CORREÇÃO AQUI: Mudámos de DateTimeField para DateField
    # E removemos o %H:%M do formato, pois o banco só tem a data
    data_inicio = serializers.DateField(format="%d/%m/%Y")

    class Meta:
        model = Evento
        fields = ['id', 'titulo', 'data_inicio', 'local', 'organizador', 'vagas']

class InscricaoSerializer(serializers.Serializer):
    evento_id = serializers.IntegerField()