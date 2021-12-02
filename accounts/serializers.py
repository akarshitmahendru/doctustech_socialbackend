import re
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers, exceptions
import django.contrib.auth.password_validation as validators
from accounts.models import User, UserOtp
from helpers.serializer_fields import CustomEmailSerializerField


class RegistrationSerializer(serializers.ModelSerializer):
    """
    serializer for registering new user
    """
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        style={'input_type': 'password'},
        validators=[validators.validate_password]
    )
    name = serializers.CharField(required=True, allow_null=False)
    last_name = serializers.CharField(required=False, allow_null=True)
    email = CustomEmailSerializerField()
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError('Password doesnt matches')
        return attrs

    def validate_email(self, email):
        if User.objects.filter(email=email):
            raise serializers.ValidationError("User with this email already exists")
        return email

    def validate_name(self, first_name):
        if not bool(first_name.strip()):
            raise serializers.ValidationError("First Name is mandatory")
        try:
            assert not re.search("\d", first_name)
        except AssertionError:
            raise serializers.ValidationError("First Name cannot contain numbers")
        return first_name

    def validate_last_name(self, last_name):
        if last_name is None:
            return last_name
        try:
            assert not re.search("\d", last_name)
        except AssertionError:
            raise serializers.ValidationError("Last Name cannot contain numbers")
        return last_name

    class Meta:
        model = User
        fields = ('email', 'name', 'last_name', 'password', 'confirm_password')


class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=255)
    email = CustomEmailSerializerField()

    def validate(self, data):
        otp = data['otp']
        try:
            user = User.objects.get(email=data['email'])
            self.user_otp = UserOtp.objects.get_user_otp_by_otp_and_user(
                otp, user)
        except UserOtp.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP. Please enter valid OTP.")
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No account is founded with this email id")
        created = self.user_otp.created_on
        current_datetime = timezone.now()
        last = (current_datetime - created).seconds
        if last > settings.SESSION_IDLE_TIMEOUT:
            raise exceptions.ValidationError("Invalid OTP. Please enter valid OTP.")
        return data


class UserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name", "last_name", "email")
