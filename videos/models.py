from django.db import models
from django.conf import settings
import os
import shutil
from django.dispatch import receiver
from django.db.models.signals import post_delete


def frame_upload_path(instance, filename):
    """
    Caminho: events/{user_id}/frames/{filename}
    """
    user_id = str(instance.user.id) if instance.user else 'default_user'
    return f'events/{user_id}/frames/{filename}'

def music_upload_path(instance, filename):
    """
    Caminho: events/{user_id}/music/{filename}
    """
    user_id = str(instance.user.id) if instance.user else 'default_user'
    return f'events/{user_id}/music/{filename}'

class Event(models.Model):
    """
    Espelha a classe Event.kt do Android.
    Armazena os dados do evento e suas configurações.
    """
    # NOVO: Vincular ao usuário
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    
    name = models.CharField(max_length=255, verbose_name="Nome do Evento")
    
    frame_url = models.CharField(max_length=500, null=True, blank=True, verbose_name="Caminho/URL da Moldura")
    music_url = models.CharField(max_length=500, null=True, blank=True, verbose_name="Caminho/URL da Música")
    
    # Configurações de Efeito e Tempo
    music_start_time_sec = models.IntegerField(default=0, verbose_name="Início da Música (s)")
    music_end_time_sec = models.IntegerField(default=0, verbose_name="Fim da Música (s)")
    effect_id = models.CharField(max_length=50, verbose_name="ID do Efeito")
    
    # Arquivos Binários (Novos)
    frame_file = models.ImageField(upload_to=frame_upload_path, null=True, blank=True, verbose_name="Arquivo da Moldura")
    music_file = models.FileField(upload_to=music_upload_path, null=True, blank=True, verbose_name="Arquivo da Música")
    
    # ALTERADO: De DateField para CharField (Android envia como string "dd/MM/yyyy")
    event_date = models.CharField(max_length=20, verbose_name="Data do Evento")
    is_finished = models.BooleanField(default=False, verbose_name="Finalizado")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (User: {self.user.email if self.user else 'No User'})"




def video_upload_path(instance, filename):
    """
    Define o caminho de upload: videos/{userId}/{eventId}/{filename}
    Exemplo: videos/123/456/1763739831951.mp4
    """
    user_id = str(instance.user.id) if instance.user else 'default_user'
    event_id = str(instance.event.id) if instance.event else 'default_event'
    
    # Adiciona 'videos/' no início para organizar melhor a pasta media
    return f'videos/{user_id}/{event_id}/{filename}'

class Video(models.Model):
    """
    Espelha a VideoUploadEntity.kt para receber os vídeos processados.
    """
    # Vincula o vídeo a um Evento e/ou Usuário
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='videos')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # O ID único gerado no Android (UUID)
    unique_id = models.CharField(max_length=100, unique=True)
    
    # O arquivo de vídeo final
    video_file = models.FileField(upload_to=video_upload_path)
    
    status = models.CharField(
        max_length=20, 
        default='PENDING',
        choices=[
            ('PENDING', 'Pendente'),
            ('PROCESSING', 'Processando'),
            ('COMPLETED', 'Concluído'),
            ('FAILED', 'Falhou')
        ]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video {self.unique_id} - {self.status}"

class SavedEffect(models.Model):
    """
    Espelha a classe EfeitoSalvo.kt do Android.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    json_config = models.TextField(verbose_name="JSON de Configuração")
    is_padrao = models.BooleanField(default=False)
    duracao_base = models.IntegerField(default=15, verbose_name="Duração Base (s)")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Efeito Salvo"
        verbose_name_plural = "Efeitos Salvos"

    def __str__(self):
        return f"{self.nome} (User: {self.user.email})"

# --- SIGNALS PARA LIMPEZA DE ARQUIVOS ---

@receiver(post_delete, sender=Video)
def auto_delete_video_file_on_delete(sender, instance, **kwargs):
    """
    Deleta o arquivo físico de vídeo quando o registro é deletado.
    """
    if instance.video_file:
        try:
            if os.path.isfile(instance.video_file.path):
                os.remove(instance.video_file.path)
        except Exception as e:
            print(f"Erro ao deletar arquivo de vídeo {instance.id}: {e}")

@receiver(post_delete, sender=Event)
def auto_delete_event_resources_on_delete(sender, instance, **kwargs):
    """
    1. Deleta arquivos de frame e música associados.
    2. Deleta a pasta inteira de vídeos deste evento (media/videos/userId/eventId).
    """
    # 1. Deleta Frame e Música
    for file_field in [instance.frame_file, instance.music_file]:
        if file_field:
            try:
                if os.path.isfile(file_field.path):
                    os.remove(file_field.path)
            except Exception as e:
                print(f"Erro ao deletar recurso do evento {instance.id}: {e}")

    # 2. Deleta Pasta de Vídeos do Evento (que contem os mp4 processados)
    try:
        # Usa user_id diretamente para evitar buscar usuário deletado
        user_id = str(instance.user_id) if instance.user_id else 'default_user'
        event_id = str(instance.id)
        
        # Caminho: media/videos/{userId}/{eventId}
        event_video_dir = os.path.join(settings.MEDIA_ROOT, 'videos', user_id, event_id)
        
        if os.path.exists(event_video_dir):
            shutil.rmtree(event_video_dir)
            print(f"Diretório de vídeos do evento {event_id} removido: {event_video_dir}")
            
    except Exception as e:
        print(f"Erro ao limpar diretório do evento {instance.id}: {e}")
