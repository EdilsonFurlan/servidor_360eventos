from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Event, Video, SavedEffect
from .serializers import EventSerializer, VideoSerializer, SavedEffectSerializer
from django.db import transaction

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_download(request):
    """
    Retorna todos os dados do usuário para o app Android.
    """
    user = request.user
    
    events = Event.objects.filter(user=user)
    videos = Video.objects.filter(user=user)
    effects = SavedEffect.objects.filter(user=user) | SavedEffect.objects.filter(is_padrao=True)

    return Response({
        'events': EventSerializer(events, many=True).data,
        'videos': VideoSerializer(videos, many=True).data,
        'effects': SavedEffectSerializer(effects, many=True).data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_upload(request):
    """
    Recebe dados do app Android para atualizar o servidor.
    Espera um JSON com listas de 'events' e 'videos' (e opcionalmente 'effects').
    """
    user = request.user
    data = request.data
    
    events_data = data.get('events', [])
    # videos_data = data.get('videos', []) # Video upload usually handled separately, but metadata might be here
    
    try:
        with transaction.atomic():
            # Processar Eventos
            for event_json in events_data:
                server_id = event_json.get('serverId') # O app manda 'serverId' se já existir
                
                # Se tiver serverId, tenta atualizar. Se nao, cria novo.
                if server_id:
                    try:
                        event = Event.objects.get(id=server_id, user=user)
                        serializer = EventSerializer(event, data=event_json, partial=True)
                        if serializer.is_valid():
                            serializer.save()
                    except Event.DoesNotExist:
                        # Se o ID nao existe (talvez deletado?), cria como novo ou ignora?
                        # Melhor criar como novo se for crucial, ou ignorar. 
                        # Vamos assumir criação se não achar, ou logar erro.
                        pass 
                else:
                    # Criação
                    serializer = EventSerializer(data=event_json)
                    if serializer.is_valid():
                        serializer.save(user=user)
            
            # TODO: Processar outros tipos se necessário (Videos metadata, Effects)
            
        return Response({'message': 'Sync upload success'}, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=400)
