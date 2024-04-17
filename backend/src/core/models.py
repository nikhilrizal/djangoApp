from django.db import models

from django.contrib.auth.models import User

class DocumentStatus(models.TextChoices):
    NOT_SUBMITTED = "not_submitted", "Not Submitted"
    IN_REVIEW = "in_review", "In Review"
    ACCEPTED = "accepted", "Accepted"
    DECLINED = "declined", "Declined"


class UserFile(models.Model):
    class Meta:
        verbose_name_plural = "User Files"

    # relational fields
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    status = models.CharField(
        max_length=100, choices=DocumentStatus.choices, default=DocumentStatus.IN_REVIEW
    )
    # fields
    file_key = models.CharField(max_length=200, blank=True, null=True)
    file_path_prefix = models.CharField(max_length=200, blank=True, null=True)
    file_path = models.CharField(max_length=200, blank=True, null=True)
    url = models.URLField()
    document_type = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.url


class Profile(models.Model):
    class Meta:
        verbose_name_plural = "User Profiles"

    # relational fields
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    image = models.ForeignKey(
        UserFile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="profile_image",
    )

    # social logins
    google_id = models.CharField(max_length=200, blank=True, null=True)

    # fields
    phone = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.email

    def is_social_auth(self):
        return self.google_id is not None
