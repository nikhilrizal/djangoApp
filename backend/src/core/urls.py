from django.urls import path

from django.conf import settings

from . import api

urlpatterns = [
    path("login/", api.LoginAPIView.as_view(), name="login"),
    path("sign-up/", api.SignUpAPIView.as_view(), name="sign-up"),
    path("send-otp/", api.SendOTPAPIView.as_view(), name="send-otp"),
    path("verify-otp/", api.VerifyOTPAPIView.as_view(), name="verify-otp"),
    path(
        "forgot-password/", api.ForgotPasswordAPIView.as_view(), name="forgot-password"
    ),
    path(
        "reset-password/",
        api.VerifyForgotPasswordAPIView.as_view(),
        name="reset-password",
    ),
    # social auth
    path("google-auth/", api.GoogleOAuthAPIView.as_view(), name="google-auth"),   
    
    # user profile
    # path("profile/", api.UserAccountProfileAPIView.as_view(), name="get-profile"),
    path(
        "profile/image/",
        api.UserProfileImageAPIView.as_view(),
        name="profile-image-upload",
    ),
    # file retrieval
    path(
        "file/<str:file_id>/", api.RetrieveFileAPIView.as_view(), name="file-retrieve"
    ),
]
