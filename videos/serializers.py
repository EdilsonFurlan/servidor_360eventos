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

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class SavedEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedEffect
        fields = ['id', 'user', 'nome', 'json_config', 'is_padrao', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']