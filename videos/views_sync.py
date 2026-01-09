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
        'events': EventSerializer(events, many=True, context={'request': request}).data,
        'videos': VideoSerializer(videos, many=True, context={'request': request}).data,
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
            
            # Processar Efeitos
            if 'effects' in data:
                effects_data = data.get('effects', [])
                print(f"SyncUpload: Recebido {len(effects_data)} efeitos.")
                
                received_names = []

                for effect_json in effects_data:
                    nome_efeito = effect_json.get('nome')
                    if nome_efeito:
                        received_names.append(nome_efeito)
                        try:
                            # Tenta buscar efeito existente pelo nome para atualizar
                            effect = SavedEffect.objects.get(user=user, nome=nome_efeito)
                            serializer = SavedEffectSerializer(effect, data=effect_json, partial=True)
                            if serializer.is_valid():
                                serializer.save()
                            else:
                                print(f"Erro update '{nome_efeito}': {serializer.errors}")
                        except SavedEffect.DoesNotExist:
                            # Cria novo
                            serializer = SavedEffectSerializer(data=effect_json)
                            if serializer.is_valid():
                                serializer.save(user=user)
                            else:
                                print(f"Erro create '{nome_efeito}': {serializer.errors}")
                        except SavedEffect.MultipleObjectsReturned:
                             # Caso raro de duplicidade: atualiza o primeiro
                            effect = SavedEffect.objects.filter(user=user, nome=nome_efeito).first()
                            serializer = SavedEffectSerializer(effect, data=effect_json, partial=True)
                            if serializer.is_valid():
                                serializer.save()

                # --- DELETE LOGIC (Diferencial) ---
                # Remove apenas os que não vieram na lista (ou seja, foram deletados no app)
                # Se a lista recebida for vazia (ex: deletou o ultimo), received_names é vazio
                # exclude(nome__in=[]) não exclui nada do queryset, ou seja, seleciona TODOS para deletar.
                # Isso está correto: se o app diz "não tenho efeitos", o server deleta os dele.
                to_delete = SavedEffect.objects.filter(user=user).exclude(nome__in=received_names)
                deleted_count, _ = to_delete.delete()
                if deleted_count > 0:
                    print(f"SyncUpload: Deletados {deleted_count} efeitos ausentes na lista de envio.")
            else:
                print("SyncUpload: Sem chave 'effects'.")
            
        return Response({'message': 'Sync upload success'}, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=400)
