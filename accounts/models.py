import logging
import random

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from .querysets import UserOtpQueryMixin, UserOtpQuerySet
from helpers.oauth_token import UserAccessToken

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class UserOtpManager(models.Manager, UserOtpQueryMixin):
    """ custom UserOtp manager """

    def get_queryset(self):
        return UserOtpQuerySet(self.model, using=self._db)

# Create your models here.


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(_('name'), max_length=255, blank=True)
    last_name = models.CharField(max_length=255, default="", blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    avatar = models.ImageField(blank=True, null=True, upload_to="avatars")
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    friends = models.ManyToManyField('self', blank=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('name',)

    def __str__(self):
        return "{} {}".format(self.name, self.last_name)

    def clean(self):
        super(User, self).clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return "{} {}".format(self.name, self.last_name)

    def get_short_name(self):
        return self.name

    def send_verification_email(self, request):
        subject = _('Verify your Email address')
        from_email = settings.DEFAULT_FROM_EMAIL
        to = self.email
        otp_code = random.randint(11111, 99999)
        data = {
            'user': self,
            'otp': otp_code,
        }
        try:
            user_otp = UserOtp.objects.filter(user=self)
            user_otp.delete()
            user_otp = UserOtp.objects.create(**data)
        except UserOtp.DoesNotExist:
            user_otp = UserOtp.objects.create(**data)
        otp = user_otp.get_otp()
        ctx = {
            'email': to,
            'otp_code': otp,
        }
        text_content = render_to_string('otp.txt', ctx)
        html_content = render_to_string('otp.html', ctx)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()

    def get_user_access_token(self, revoke=False):
        token_application_name = settings.APPLICATION_NAME
        user_access_token = UserAccessToken(self, self, token_application_name)
        if revoke:
            user_access_token.revoke_oauth_tokens()
            return
        else:
            access_token = user_access_token.create_oauth_token()
            access_token = access_token.token
            self.last_login = timezone.now()
            self.save()
            return access_token


class UserOtp(models.Model):
    """ model for user otp"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    otp = models.CharField(
        max_length=5
    )
    created_on = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True)

    objects = UserOtpManager()

    def __str__(self):
        return "{0}-{1}".format(self.user.email, self.otp)

    def get_user(self):
        return self.user

    def get_otp(self):
        return self.otp

    def get_created_time(self):
        return self.created_on


class FriendRequests(models.Model):
    REQUEST_STATUS = (
        ('sent', _('sent')),
        ('accepted', _('accepted')),
        ('rejected', _('rejected'))
    )
    source = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="request_by",
        null=True,
        blank=True
    )
    target = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="request_to",
        null=True,
        blank=True
    )
    requested_date = models.DateField(
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=50,
        choices=REQUEST_STATUS,
        null=True,
        blank=True,
        default='sent'
    )

    class Meta:
        verbose_name_plural = _(u"Friend Requests")

