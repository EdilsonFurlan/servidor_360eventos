from rest_framework import serializers
from .models import Event, Video, SavedEffect

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'user', 'name', 'frame_url', 'music_url', 
                  'music_start_time_sec', 'music_end_time_sec', 
                  'effect_id', 'event_date', 'is_finished',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        request = self.context.get('request')

        # Se tiver arquivo real, sobrescreve a URL antiga (que pode ser local path)
        if instance.frame_file:
            try:
                file_url = instance.frame_file.url
                if request:
                    file_url = request.build_absolute_uri(file_url)
                representation['frame_url'] = file_url
            except Exception:
                pass

        if instance.music_file:
            try:
                file_url = instance.music_file.url
                if request:
                    file_url = request.build_absolute_uri(file_url)
                representation['music_url'] = file_url
            except Exception:
                pass

        # Garante que event_date nunca seja null para não quebrar o Android
        if not representation.get('event_date'):
            import datetime
            representation['event_date'] = datetime.datetime.now().strftime("%d/%m/%Y")
        return representation

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class SavedEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedEffect
        fields = ['id', 'user', 'nome', 'json_config', 'is_padrao', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']