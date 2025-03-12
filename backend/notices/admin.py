from django.contrib import admin
from .models import Notice, Event, EventRegistration

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'notice_type', 'target_audience', 'created_by', 'created_at', 'is_active')
    list_filter = ('notice_type', 'target_audience', 'is_active', 'created_at')
    search_fields = ('title', 'content', 'created_by__email')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'venue', 'organizer', 'registration_required', 'get_registration_count')
    list_filter = ('date', 'registration_required', 'created_at')
    search_fields = ('title', 'description', 'venue', 'organizer__email')
    ordering = ('-date', '-time')
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('organizer')
    
    def get_registration_count(self, obj):
        return obj.eventregistration_set.count()
    get_registration_count.short_description = 'Registrations'

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'registration_date', 'attendance_status')
    list_filter = ('registration_date', 'attendance_status', 'event__date')
    search_fields = ('event__title', 'user__email')
    ordering = ('-registration_date',)
    date_hierarchy = 'registration_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('event', 'user') 