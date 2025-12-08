from django.db import models
from django.conf import settings


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
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Efeito Salvo"
        verbose_name_plural = "Efeitos Salvos"

    def __str__(self):
        return f"{self.nome} (User: {self.user.email})"
