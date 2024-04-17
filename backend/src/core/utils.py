import uuid

import boto3

from django.conf import settings

from .models import UserFile, Profile


def get_signed_url_from_aws(key):
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        signed_url = s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": bucket_name, "Key": key}, ExpiresIn=3600
        )  # URL expires in 1 hour (3600 seconds)

        return signed_url
    except Exception as e:
        print(e)
        return None


def upload_file_to_s3(
    user, file, document_type=None, folder_path_prefix=None, status=None
):
    if not file:
        return None

    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    bucket = settings.AWS_STORAGE_BUCKET_NAME
    unique_filename = str(uuid.uuid4()) + "." + file.name.split(".")[-1]
    file_path_prefix = (
        f"uploads/{user.id}/{folder_path_prefix}"
        if folder_path_prefix
        else f"uploads/{user.id}"
    )
    path_key = f"{file_path_prefix}/{unique_filename}"

    try:
        with file.open("rb") as f:
            s3.upload_fileobj(f, bucket, path_key)
        url = f"https://{bucket}.s3.amazonaws.com/{path_key}"
        
        uploaded_file = UserFile.objects.create(
            user=user,
            file_path=path_key,
            url=url,
            file_key=unique_filename,
            document_type=document_type,
            file_path_prefix=file_path_prefix,
            status=status,
        )
        uploaded_file.save()
        return uploaded_file.id
    except Exception as e:
        print(e)
        return None


def get_user_profile_completion(user):
    profile = Profile.objects.filter(user=user).first()
    if not profile:
        return 0, None

    fields_count = len(Profile._meta.fields) - 1
    filled_fields_count = sum(
        1
        for field in Profile._meta.fields
        if getattr(profile, field.name, None) is not None
    )
    completion_level = filled_fields_count / fields_count * 100
    return completion_level, profile


def get_model_completion(user, model):
    instance = model.objects.filter(user=user).first()
    if not instance:
        instance = model.objects.create(user=user)

    fields_count = len([field for field in model._meta.fields if field.name != "user"])
    filled_fields_count = sum(
        1
        for field in model._meta.fields
        if field.name != "user" and getattr(instance, field.name, None)
    )
    if fields_count == 0 or filled_fields_count == 0:
        return 0, instance

    completion_level = filled_fields_count / fields_count * 100
    return completion_level, instance
