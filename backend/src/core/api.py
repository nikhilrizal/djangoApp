import json
from datetime import datetime

import requests
from os import path

from django.db import transaction
from requests.auth import HTTPBasicAuth

from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema

from rest_framework.views import APIView, Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# import firebase_admin

# from firebase_admin import credentials
# from firebase_admin import auth

from .models import Profile, UserFile
from .serializers import ProfileSerializer, UserFileSerializer,LoginSerializer,SignUpSerializer, SendOTPSerializer, SendOTPSerializer, VerifyOTPSerializer, ForgotPasswordSerializer, VerifyForgotPasswordSerializer
from .utils import get_signed_url_from_aws, upload_file_to_s3, get_user_profile_completion, get_model_completion

# cred = credentials.Certificate(
#     path.join(settings.BASE_DIR, "creds", "firebase-admin.json")
# )
# firebase_admin.initialize_app(cred)


class LoginAPIView(APIView):
    
    @swagger_auto_schema(request_body=LoginSerializer)

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=400)

        user = authenticate(username=username.lower(), password=password)
        if not user:
            return Response({"error": "Invalid username or password"}, status=400)

        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)

        if not user.profile.phone:
            return Response(
                dict(
                    token=token.key,
                    message="Phone number not found for user",
                    phone_verified=False,
                ),
                status=200,
            )

        return Response(
            dict(token=token.key),
            status=200,
        )


class SignUpAPIView(APIView):
    @swagger_auto_schema(request_body=SignUpSerializer)
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        verify_password = request.data.get("verify_password")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")

        if not email:
            return Response({"error": "Email is required"}, status=400)

        if not password:
            return Response({"error": "Password is required"}, status=400)

        if not verify_password:
            return Response({"error": "Verify password is required"}, status=400)

        if not first_name:
            return Response({"error": "First name is required"}, status=400)

        if not last_name:
            return Response({"error": "Last name is required"}, status=400)

        if password != verify_password:
            return Response({"error": "Passwords do not match"}, status=400)

        if User.objects.filter(email=email.lower()).exists():
            return Response({"error": "Email is already in use"}, status=400)

        user = User.objects.create_user(
            email=email.lower(),
            username=email.lower(),
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.save()

        Profile.objects.create(user=user)
        token = Token.objects.create(user=user)

        return Response(
            dict(token=token.key),
            status=201,
        )


class SendOTPAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=SendOTPSerializer)
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")

        if not phone_number:
            return Response({"error": "Phone number is required"}, status=400)

        if not "+" in phone_number:
            return Response(
                {"error": "Phone number must include country code"}, status=400
            )

        base_url = f"https://verify.twilio.com/v2/Services/{settings.TWILIO_VERIFY_SID}"
        auth_credentials = HTTPBasicAuth(
            settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN
        )

        req = requests.post(
            f"{base_url}/Verifications",
            data={"To": phone_number, "Channel": "sms"},
            auth=auth_credentials,
        )
        if req.status_code != 201:
            return Response({"error": "Error in sending OTP"}, status=400)

        return Response({"message": "OTP sent successfully"}, status=200)


class VerifyOTPAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=VerifyOTPSerializer)
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")
        otp_code = request.data.get("otp_code")

        if not phone_number:
            return Response({"error": "Phone number is required"}, status=400)
        if not otp_code:
            return Response({"error": "OTP code is required"}, status=400)

        base_url = f"https://verify.twilio.com/v2/Services/{settings.TWILIO_VERIFY_SID}"
        auth_credentials = HTTPBasicAuth(
            settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN
        )

        response = requests.post(
            f"{base_url}/VerificationCheck",
            data={"To": phone_number, "Code": otp_code},
            auth=auth_credentials,
        )
        if response.status_code != 200:
            return Response({"error": "Error in OTP verification"}, status=400)

        res = response.json()
        if not res["valid"]:
            return Response({"error": "Invalid OTP code"}, status=400)

        user = request.user
        user.profile.phone = phone_number
        user.profile.save()

        return Response({"message": "Phone number verified successfully"}, status=200)


class ForgotPasswordAPIView(APIView):
    @swagger_auto_schema(request_body=ForgotPasswordSerializer)
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=400)

        user = User.objects.filter(email=email.lower()).first()
        if not user:
            return Response({"error": "User not found"}, status=400)

        if not user.profile:
            return Response({"error": "Profile not found for user"}, status=400)

        base_url = f"https://verify.twilio.com/v2/Services/{settings.TWILIO_VERIFY_SID}"
        auth_credentials = HTTPBasicAuth(
            settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN
        )

        req = requests.post(
            f"{base_url}/Verifications",
            data={"To": user.profile.phone, "Channel": "sms"},
            auth=auth_credentials,
        )
        if req.status_code != 201:
            return Response({"error": "Error in sending OTP"}, status=400)

        return Response({"message": "OTP sent for password reset"}, status=200)


class VerifyForgotPasswordAPIView(APIView):
    @swagger_auto_schema(request_body=VerifyForgotPasswordSerializer)
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        verify_password = request.data.get("verify_password")
        otp_code = request.data.get("otp_code")

        if not email:
            return Response({"error": "Email is required"}, status=400)
        if not password:
            return Response({"error": "Phone number is required"}, status=400)
        if not verify_password:
            return Response({"error": "OTP code is required"}, status=400)
        if not otp_code:
            return Response({"error": "OTP code is required"}, status=400)

        if password != verify_password:
            return Response({"error": "Passwords do not match"}, status=400)

        user = User.objects.filter(email=email.lower()).first()
        if not user:
            return Response({"error": "User not found"}, status=400)

        base_url = f"https://verify.twilio.com/v2/Services/{settings.TWILIO_VERIFY_SID}"
        auth_credentials = HTTPBasicAuth(
            settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN
        )

        response = requests.post(
            f"{base_url}/VerificationCheck",
            data={"To": user.profile.phone, "Code": otp_code},
            auth=auth_credentials,
        )

        if response.status_code != 200:
            return Response({"error": "Error in OTP verification"}, status=400)

        user.set_password(password)
        user.save()

        return Response({"message": "Password updated successfully"}, status=200)


class GoogleOAuthAPIView(APIView):
    @swagger_auto_schema(request_body=SignUpSerializer)
    def post(self, request, *args, **kwargs):
        token = request.data.get("token")  #
        if not token:
            return Response({"error": "Token is missing"}, status=400)

        try:
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token.get("uid")
        except Exception as e:
            return Response({"error": str(e)}, status=401)

        email = request.data.get("email")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        social_id = request.data.get("id")

        if not email:
            return Response({"error": "Email is required"}, status=400)

        if not first_name:
            return Response({"error": "First name is required"}, status=400)

        if not last_name:
            return Response({"error": "Last name is required"}, status=400)

        if not social_id:
            return Response({"error": "Social ID is required"}, status=400)

        user = User.objects.filter(email=email.lower()).first()
        if not user:
            user = User.objects.create_user(
                email=email.lower(),
                username=email.lower(),
                password="",
                first_name=first_name,
                last_name=last_name,
            )
            user.save()
            Profile.objects.create(user=user, google_id=social_id)
            token = Token.objects.create(user=user)
            return Response(
                dict(token=token.key),
                status=201,
            )
        else:
            return Response({"error": "User already exists"}, status=400)


class RetrieveFileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: UserFileSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        file_id = kwargs.get("file_id")
        if not file_id:
            return Response({"error": "File ID is required"}, status=400)

        try:
            file = UserFile.objects.get(id=file_id)
        except UserFile.DoesNotExist:
            return Response({"error": "File not found"}, status=404)
        file_key = f"{file.file_path_prefix}/{file.file_key}"
        signed_url = get_signed_url_from_aws(file_key)
        if not signed_url:
            return Response({"error": "Error in retrieving file"}, status=400)
        return Response({"url": signed_url}, status=200)


class UserProfileImageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: ProfileSerializer}
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        profile = request.FILES.get('profile')

        if not profile:
            return Response({"error": "Profile Image is required"}, status=400)

        profile_image_id = upload_file_to_s3(user, profile, "profile_iage", "profile", "accepted")

        user_profile, created = Profile.objects.get_or_create(user=user)
        user_profile.image_id = profile_image_id
        user_profile.save()

        return Response({"message": "Profile Image updated successfully"}, status=200)
