from rest_framework import serializers
from .models import Event, Video

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'frame_url', 'music_url', 
                  'music_start_time_sec', 'music_end_time_sec', 
                  'effect_id', 'event_date', 'is_finished',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'