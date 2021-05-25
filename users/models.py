from django.db import models

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator

from django.utils import timezone

from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail

import uuid


#ここ( https://github.com/django/django/blob/master/django/contrib/auth/models.py#L321 )から流用
class CustomUser(AbstractBaseUser, PermissionsMixin):

    username_validator  = UnicodeUsernameValidator()

    id          = models.UUIDField( default=uuid.uuid4, primary_key=True, editable=False )
    username    = models.CharField(
                    _('username'),
                    max_length=150,
                    unique=True,
                    help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
                    validators=[username_validator],
                    error_messages={
                        'unique': _("A user with that username already exists."),
                    },
                )

    handle_name = models.CharField(verbose_name="Handle_name", max_length=150)
    email       = models.EmailField(_('email address'))  #blank=True消去

    is_staff    = models.BooleanField(
                    _('staff status'),
                    default=False,
                    help_text=_('Designates whether the user can log into this admin site.'),
                )

    is_active   = models.BooleanField(
                    _('active'),
                    default=True,
                    help_text=_(
                        'Designates whether this user should be treated as active. '
                        'Unselect this instead of deleting accounts.'
                    ),
                )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    #usericon    = models.ImageField(verbose_name="ユーザーアイコン", upload_to="tube/usericon/", null=True)
    usericon    = models.ImageField(verbose_name="ユーザーアイコン", upload_to="tube/usericon/",blank=True, null=True)

    objects     = UserManager()

    EMAIL_FIELD     = 'email'
    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['email','handle_name']  #ハンドルネーム追加

    class Meta:
        verbose_name        = _('user')
        verbose_name_plural = _('users')
        #abstract            = True

    def clean(self):
        super().clean()
        self.email  = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_full_name(self):
        return self.handle_name

    def get_short_name(self):
        return self.handle_name
