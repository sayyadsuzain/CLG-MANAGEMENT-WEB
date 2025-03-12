from rest_framework import serializers
from .models import Notice, Event, EventRegistration
from users.serializers import UserSerializer
from django.utils import timezone

class NoticeSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(
        source='created_by',
        write_only=True,
        queryset=User.objects.all()
    )

    class Meta:
        model = Notice
        fields = ('id', 'title', 'content', 'notice_type', 'created_by', 'created_by_id',
                'created_at', 'updated_at', 'attachment', 'is_active', 'target_audience')
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, data):
        if data.get('notice_type') == 'event' and not data.get('content'):
            raise serializers.ValidationError({
                'content': 'Content is required for event notices.'
            })
        return data

class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    organizer_id = serializers.PrimaryKeyRelatedField(
        source='organizer',
        write_only=True,
        queryset=User.objects.all()
    )
    registration_count = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()
    can_register = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'date', 'time',
            'venue', 'organizer', 'organizer_id', 'created_at',
            'image', 'registration_required', 'registration_deadline',
            'registration_count', 'is_registered', 'can_register'
        )
        read_only_fields = ('created_at',)

    def get_registration_count(self, obj):
        return obj.eventregistration_set.count()

    def get_is_registered(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.eventregistration_set.filter(user=request.user).exists()
        return False

    def get_can_register(self, obj):
        if not obj.registration_required:
            return False
        if obj.registration_deadline and obj.registration_deadline < timezone.now():
            return False
        if obj.date < timezone.now().date():
            return False
        return True

    def validate(self, data):
        # Validate registration deadline is before event date
        if data.get('registration_required') and data.get('registration_deadline'):
            event_datetime = timezone.datetime.combine(
                data['date'],
                data['time'],
                tzinfo=timezone.get_current_timezone()
            )
            if data['registration_deadline'] >= event_datetime:
                raise serializers.ValidationError({
                    'registration_deadline': 'Registration deadline must be before event date and time.'
                })
        return data

class EventRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        source='event',
        write_only=True,
        queryset=Event.objects.all()
    )

    class Meta:
        model = EventRegistration
        fields = (
            'id', 'event', 'event_id', 'user',
            'registration_date', 'attendance_status'
        )
        read_only_fields = ('registration_date', 'attendance_status')

    def validate_event_id(self, event):
        user = self.context['request'].user

        # Check if registration is required
        if not event.registration_required:
            raise serializers.ValidationError(
                "This event does not require registration."
            )

        # Check if registration deadline has passed
        if event.registration_deadline and event.registration_deadline < timezone.now():
            raise serializers.ValidationError(
                "Registration deadline has passed."
            )

        # Check if event date has passed
        if event.date < timezone.now().date():
            raise serializers.ValidationError(
                "Cannot register for past events."
            )

        # Check if user is already registered
        if EventRegistration.objects.filter(event=event, user=user).exists():
            raise serializers.ValidationError(
                "You are already registered for this event."
            )

        return event

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data) 