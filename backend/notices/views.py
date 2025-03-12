from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from .models import Notice, Event, EventRegistration
from .serializers import NoticeSerializer, EventSerializer, EventRegistrationSerializer
from users.models import User
from users.utils import log_user_activity
from .tasks import (
    send_notice_notification_async,
    send_event_notification_async,
    send_registration_confirmation_async
)

class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Notice.objects.filter(is_active=True)
        
        # Filter by notice type
        notice_type = self.request.query_params.get('notice_type')
        if notice_type:
            queryset = queryset.filter(notice_type=notice_type)
        
        # Filter by target audience
        target_audience = self.request.query_params.get('target_audience')
        if target_audience:
            queryset = queryset.filter(target_audience=target_audience)
        
        # Search by title or content
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            )
        
        return queryset.select_related('created_by').order_by('-created_at')

    def perform_create(self, serializer):
        notice = serializer.save(created_by=self.request.user)
        log_user_activity(
            self.request.user,
            'notice_create',
            self.request,
            {'notice_id': notice.id, 'title': notice.title}
        )
        # Send notification asynchronously
        send_notice_notification_async.delay(notice.id)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Event.objects.all()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Filter by registration status
        registration_required = self.request.query_params.get('registration_required')
        if registration_required is not None:
            queryset = queryset.filter(
                registration_required=registration_required.lower() == 'true'
            )
        
        # Filter upcoming events
        upcoming = self.request.query_params.get('upcoming')
        if upcoming and upcoming.lower() == 'true':
            queryset = queryset.filter(date__gte=timezone.now().date())
        
        # Search by title or venue
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(venue__icontains=search)
            )
        
        return queryset.select_related('organizer').order_by('date', 'time')

    def perform_create(self, serializer):
        event = serializer.save(organizer=self.request.user)
        log_user_activity(
            self.request.user,
            'event_create',
            self.request,
            {'event_id': event.id, 'title': event.title}
        )
        # Send notification asynchronously
        send_event_notification_async.delay(event.id)

    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        event = self.get_object()
        
        # Create registration using the serializer
        serializer = EventRegistrationSerializer(
            data={'event_id': event.id},
            context={'request': request}
        )
        
        if serializer.is_valid():
            registration = serializer.save()
            log_user_activity(
                request.user,
                'event_registration',
                request,
                {'event_id': event.id, 'title': event.title}
            )
            # Send registration confirmation asynchronously
            send_registration_confirmation_async.delay(registration.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel_registration(self, request, pk=None):
        event = self.get_object()
        try:
            registration = EventRegistration.objects.get(
                event=event,
                user=request.user
            )
            registration.delete()
            log_user_activity(
                request.user,
                'event_registration_cancel',
                request,
                {'event_id': event.id, 'title': event.title}
            )
            return Response({'message': 'Registration cancelled successfully'})
        except EventRegistration.DoesNotExist:
            return Response(
                {'error': 'You are not registered for this event'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def registrations(self, request, pk=None):
        event = self.get_object()
        registrations = EventRegistration.objects.filter(event=event)
        serializer = EventRegistrationSerializer(registrations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_attendance(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        event = self.get_object()
        user_id = request.data.get('user_id')
        attendance_status = request.data.get('attendance_status', True)

        registration = get_object_or_404(
            EventRegistration,
            event=event,
            user_id=user_id
        )

        registration.attendance_status = attendance_status
        registration.save()
        
        log_user_activity(
            request.user,
            'event_attendance_mark',
            request,
            {
                'event_id': event.id,
                'user_id': user_id,
                'attendance_status': attendance_status
            }
        )

        serializer = EventRegistrationSerializer(registration)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        event = self.get_object()
        total_registrations = event.eventregistration_set.count()
        present_count = event.eventregistration_set.filter(attendance_status=True).count()
        
        return Response({
            'total_registrations': total_registrations,
            'present_count': present_count,
            'absent_count': total_registrations - present_count,
            'attendance_percentage': (
                (present_count / total_registrations * 100)
                if total_registrations > 0 else 0
            )
        })

class EventRegistrationViewSet(viewsets.ModelViewSet):
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = EventRegistration.objects.all()
        
        # Regular users can only view their own registrations
        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)
        
        # Staff can filter registrations
        event_id = self.request.query_params.get('event_id')
        user_id = self.request.query_params.get('user_id')
        attendance_status = self.request.query_params.get('attendance_status')

        if event_id:
            queryset = queryset.filter(event_id=event_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if attendance_status is not None:
            queryset = queryset.filter(
                attendance_status=attendance_status.lower() == 'true'
            )
        
        return queryset.select_related('user', 'event') 