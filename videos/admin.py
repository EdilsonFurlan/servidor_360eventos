from django.contrib import admin
from .models import Event, Video

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'event_date', 'is_finished', 'created_at')
    search_fields = ('name', 'user__username')
    list_filter = ('is_finished', 'event_date')

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('unique_id', 'event', 'user', 'status', 'created_at')
    search_fields = ('unique_id', 'event__name', 'user__username')
    list_filter = ('status', 'created_at')
