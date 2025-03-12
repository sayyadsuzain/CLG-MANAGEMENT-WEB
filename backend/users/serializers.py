from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import User, Student, Faculty, Course, Enrollment, Attendance, UserActivity, Log

class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile_url = serializers.SerializerMethodField()
    role_details = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'full_name',
                 'user_type', 'phone_number', 'profile_picture', 'profile_url',
                 'date_of_birth', 'is_active', 'last_login', 'role_details',
                 'date_joined', 'email_verified')
        read_only_fields = ('email_verified', 'last_login', 'date_joined')

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_profile_url(self, obj):
        if obj.profile_picture:
            return self.context['request'].build_absolute_uri(obj.profile_picture.url)
        return None

    def get_role_details(self, obj):
        if obj.user_type == 'student':
            try:
                student = obj.student
                return {
                    'student_id': student.student_id,
                    'department': student.department,
                    'semester': student.semester,
                    'admission_date': student.admission_date
                }
            except Student.DoesNotExist:
                return None
        elif obj.user_type == 'faculty':
            try:
                faculty = obj.faculty
                return {
                    'faculty_id': faculty.faculty_id,
                    'department': faculty.department,
                    'designation': faculty.designation,
                    'joining_date': faculty.joining_date
                }
            except Faculty.DoesNotExist:
                return None
        return None

class UserUpdateSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'profile_picture',
                 'date_of_birth', 'current_password', 'new_password', 'confirm_password')

    def validate(self, data):
        if 'new_password' in data or 'confirm_password' in data or 'current_password' in data:
            if not all(key in data for key in ['current_password', 'new_password', 'confirm_password']):
                raise serializers.ValidationError({
                    'password': 'All password fields are required for password change.'
                })
            
            if not self.instance.check_password(data['current_password']):
                raise serializers.ValidationError({
                    'current_password': 'Current password is incorrect.'
                })
            
            if data['new_password'] != data['confirm_password']:
                raise serializers.ValidationError({
                    'confirm_password': 'Passwords do not match.'
                })
            
            try:
                validate_password(data['new_password'], self.instance)
            except ValidationError as e:
                raise serializers.ValidationError({
                    'new_password': list(e.messages)
                })
        
        return data

    def update(self, instance, validated_data):
        if 'new_password' in validated_data:
            instance.set_password(validated_data['new_password'])
            validated_data.pop('new_password')
            validated_data.pop('current_password')
            validated_data.pop('confirm_password')
        
        return super().update(instance, validated_data)

class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('is_active', 'user_type', 'is_staff', 'is_superuser')

    def validate(self, data):
        # Prevent self-deactivation
        if self.instance == self.context['request'].user and 'is_active' in data:
            if not data['is_active']:
                raise serializers.ValidationError({
                    'is_active': "You cannot deactivate your own account."
                })
        
        # Prevent removal of last superuser
        if self.instance.is_superuser and 'is_superuser' in data:
            if not data['is_superuser'] and User.objects.filter(is_superuser=True).count() <= 1:
                raise serializers.ValidationError({
                    'is_superuser': "Cannot remove the last superuser."
                })
        
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'user_type',
                 'phone_number', 'profile_picture', 'date_of_birth')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = ('id', 'user', 'student_id', 'department', 'semester', 'admission_date')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        student = Student.objects.create(user=user, **validated_data)
        return student

class FacultySerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Faculty
        fields = ('id', 'user', 'faculty_id', 'department', 'designation', 'joining_date')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        faculty = Faculty.objects.create(user=user, **validated_data)
        return faculty

class CourseSerializer(serializers.ModelSerializer):
    faculty = FacultySerializer(read_only=True)
    faculty_id = serializers.PrimaryKeyRelatedField(
        queryset=Faculty.objects.all(),
        source='faculty',
        write_only=True
    )

    class Meta:
        model = Course
        fields = ('id', 'course_code', 'title', 'description', 'faculty', 'faculty_id')

class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ('id', 'student', 'course', 'enrollment_date', 'grade')

class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = ('id', 'student', 'course', 'date', 'is_present')

class UserActivitySerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    performed_by = UserDetailSerializer(read_only=True)

    class Meta:
        model = UserActivity
        fields = (
            'id', 'user', 'activity_type', 'ip_address', 'user_agent',
            'device_type', 'location', 'extra_data', 'created_at',
            'performed_by'
        )
        read_only_fields = fields

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        print(f"Validating login data for email: {data.get('email')}")
        email = data.get('email')
        password = data.get('password')

        if not email:
            raise serializers.ValidationError({
                'email': 'Email is required.'
            })
        
        if not password:
            raise serializers.ValidationError({
                'password': 'Password is required.'
            })

        try:
            # Check if user exists and is active
            user = User.objects.get(email=email)
            print(f"Found user: {user.email}, active: {user.is_active}, verified: {user.email_verified}")
            
            if not user.is_active:
                raise serializers.ValidationError({
                    'email': 'This account has been deactivated.'
                })
            
            if not user.email_verified:
                raise serializers.ValidationError({
                    'email': 'Please verify your email address first.'
                })
            
            # Check if account is locked
            if user.account_locked_until and user.account_locked_until > timezone.now():
                time_remaining = user.account_locked_until - timezone.now()
                minutes_remaining = int(time_remaining.total_seconds() / 60)
                raise serializers.ValidationError({
                    'error': f'Account is locked. Please try again in {minutes_remaining} minutes.'
                })
            
            # Attempt authentication
            authenticated_user = authenticate(email=email, password=password)
            if not authenticated_user:
                # Increment failed login attempts
                user.increment_failed_login()
                attempts_remaining = 5 - user.failed_login_attempts
                
                if attempts_remaining > 0:
                    raise serializers.ValidationError({
                        'password': f'Invalid password. {attempts_remaining} attempts remaining.'
                    })
                else:
                    raise serializers.ValidationError({
                        'error': 'Account locked due to too many failed attempts.'
                    })
            
            # Reset failed login attempts on successful authentication
            user.reset_login_attempts()
            data['user'] = authenticated_user
            return data
            
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'No account found with this email address.'
            })
        except Exception as e:
            print(f"Error in login validation: {str(e)}")
            raise serializers.ValidationError({
                'error': 'An error occurred during login. Please try again.'
            })

class LogSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Log
        fields = (
            'id', 'timestamp', 'level', 'logger_name', 'file_path',
            'function_name', 'line_number', 'message', 'exception',
            'stack_trace', 'user', 'ip_address', 'request_method',
            'request_path', 'request_body', 'response_status',
            'execution_time'
        )
        read_only_fields = fields 