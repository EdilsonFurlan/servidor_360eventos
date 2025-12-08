from rest_framework import viewsets, parsers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # OPCIONAL
from django.core.files.storage import default_storage
from .models import Event, Video
from .serializers import EventSerializer, VideoSerializer
import uuid
from rest_framework import status
from django.contrib.auth import get_user_model



class EventViewSet(viewsets.ModelViewSet):
    # CORRIGIDO: Adicionar queryset como atributo da classe
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    # OPCIONAL: Descomentar se quiser exigir autenticação
    # permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # OPCIONAL: Filtrar por usuário se tiver autenticação
        # if self.request.user.is_authenticated:
        #     return Event.objects.filter(user=self.request.user)
        return Event.objects.all()
    
    def perform_create(self, serializer):
        # OPCIONAL: Associar ao usuário logado
        # if self.request.user.is_authenticated:
        #     serializer.save(user=self.request.user)
        # else:
        serializer.save()




class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    @action(detail=False, methods=['post'], url_path='upload/(?P<event_name>[^/.]+)')
    def upload_video(self, request, event_name=None):
        """
        Endpoint para upload de vídeo processado
        POST /videos/videos/upload/{event_name}/
        
        Salva em: media/videos/{userId}/{eventId}/{timestamp}.mp4
        """
        
        video_file = request.FILES.get('video')
        user_id = request.data.get('userId')
        
        if not video_file:
            return Response({'error': 'Arquivo não fornecido'}, status=400)
        
        # 1. Busca o Evento pelo nome
        event = Event.objects.filter(name=event_name).first()
        if not event:
            return Response({'error': f'Evento "{event_name}" não encontrado'}, status=404)

        # 2. Busca o Usuário (opcional)
        User = get_user_model()
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass  # Mantém user como None se não encontrar

        try:
            # 3. Cria registro no banco
            # O upload_video_path será chamado automaticamente ao salvar
            video = Video.objects.create(
                event=event,
                user=user,
                unique_id=str(uuid.uuid4()),  # Gera ID único para o registro
                video_file=video_file,  # Django salva em: videos/{userId}/{eventId}/{filename}
                status='UPLOADED'
            )
            
            # 4. Retorna URL completa do arquivo
            file_url = request.build_absolute_uri(video.video_file.url)
            
            return Response({
                'message': 'Upload realizado com sucesso!',
                'id': video.id,
                'url': file_url,
                'status': 'UPLOADED',
                'path': video.video_file.name  # Caminho relativo: videos/123/456/1763739831951.mp4
            }, status=201)
            
        except Exception as e:
            import traceback
            traceback.print_exc()  # Log completo no console
            return Response({'error': str(e)}, status=500)