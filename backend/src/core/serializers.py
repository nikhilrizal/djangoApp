from django.contrib.auth.models import User

from rest_framework import serializers

from .models import (
    UserFile,
    Profile,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class UserFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFile
        fields = [
            "id",
            "file_key",
            "url",
            "document_type",
            "file_path_prefix",
            "file_path",
            "status",
        ]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    image = UserFileSerializer()

    class Meta:
        model = Profile
        fields = ["id", "user", "phone", "image"]

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    verify_password = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)

class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    otp_code = serializers.CharField(required=True)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class VerifyForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    verify_password = serializers.CharField(required=True)
    otp_code = serializers.CharField(required=True)

class GoogleOAuthSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    id = serializers.CharField(required=True)  # Assuming this is some form of ID

class UserProfileImageSerializer(serializers.Serializer):
    profile = serializers.ImageField(required=True)