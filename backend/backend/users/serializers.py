from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, Student, Faculty, Course, Enrollment, Attendance

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        
        if user.user_type != data['user_type']:
            raise serializers.ValidationError(f"User is not registered as {data['user_type']}")
        
        return {
            'user': user,
            'user_type': data['user_type']
        }

class StudentSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    student_id = serializers.CharField()
    department = serializers.CharField()
    semester = serializers.IntegerField()
    admission_date = serializers.DateField()

    class Meta:
        model = User
        fields = ('username', 'password', 'confirm_password', 'email', 'first_name', 
                 'last_name', 'phone_number', 'date_of_birth', 'student_id', 
                 'department', 'semester', 'admission_date')

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        student_data = {
            'student_id': validated_data.pop('student_id'),
            'department': validated_data.pop('department'),
            'semester': validated_data.pop('semester'),
            'admission_date': validated_data.pop('admission_date')
        }
        
        validated_data['user_type'] = 'student'
        user = User.objects.create_user(**validated_data)
        Student.objects.create(user=user, **student_data)
        return user

class FacultySignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    faculty_id = serializers.CharField()
    department = serializers.CharField()
    designation = serializers.CharField()
    joining_date = serializers.DateField()

    class Meta:
        model = User
        fields = ('username', 'password', 'confirm_password', 'email', 'first_name', 
                 'last_name', 'phone_number', 'date_of_birth', 'faculty_id', 
                 'department', 'designation', 'joining_date')

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        faculty_data = {
            'faculty_id': validated_data.pop('faculty_id'),
            'department': validated_data.pop('department'),
            'designation': validated_data.pop('designation'),
            'joining_date': validated_data.pop('joining_date')
        }
        
        validated_data['user_type'] = 'faculty'
        user = User.objects.create_user(**validated_data)
        Faculty.objects.create(user=user, **faculty_data)
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords do not match")
        try:
            validate_password(data['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        return data

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture')

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

# Existing serializers remain unchanged 