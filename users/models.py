from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from simple_history.models import HistoricalRecords
from phonenumber_field.modelfields import PhoneNumberField

from internals.models import School, University

from .templatetags.users import device, location


SEX_CHOICES = [
    ('male', _('Male')),
    ('female', _('Female'))
]


class Parent(models.Model):
    class Meta:
        verbose_name = _('Parent')
        verbose_name_plural = _('Parents')

    sex = models.CharField(max_length=128, choices=SEX_CHOICES)
    last_name = models.CharField(max_length=128, verbose_name=_('Last Name'))
    first_name = models.CharField(max_length=128, verbose_name=_('First Name'))
    middle_name = models.CharField(max_length=128, null=True, blank=True, verbose_name=_('Middle Name'))
    job = models.CharField(max_length=128, verbose_name=_('Job'))
    phone_number = PhoneNumberField(verbose_name=_('Parent Phone Number'))

    def __str__(self):
        return f"{self.get_full_name()}, {self.job}, {self.phone_number}"

    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"


class User(AbstractUser):
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    GROUP_CHOICES = [
        ('junior', _('Junior')),
        ('middle', _('Middle')),
        ('senior', _('Senior')),
    ]

    def get_photo_upload_path(instance, filename):
        ext = filename.split('.')[-1]
        dt = timezone.now()
        filename = f"{dt.year}-{dt.month:02d}-{dt.day:02d}-{dt.hour:02d}-{dt.minute:02d}-{dt.second:02d}.{ext}"
        return f"profiles/{instance.id}/{filename}"

    sex = models.CharField(max_length=128, choices=SEX_CHOICES, verbose_name=_('Sex'))
    middle_name = models.CharField(max_length=128, null=True, blank=True, verbose_name=_('Middle Name'))
    phone_number = PhoneNumberField(verbose_name=_('Phone Number'))
    group = models.CharField(default='junior', max_length=20, choices=GROUP_CHOICES, verbose_name=_('Group'))
    birthday = models.DateField(default=timezone.now, verbose_name=_('Birthday'))

    parents = models.ManyToManyField(Parent)

    school = models.ForeignKey(School, null=True, on_delete=models.SET_NULL, verbose_name=_('School'))
    photo = models.ImageField(upload_to=get_photo_upload_path, null=True, blank=True, verbose_name=_('Profile Photo'))
    klass = models.PositiveIntegerField(null=True, blank=True,
                                        choices=[(i, str(i)) for i in range(1, 12)], verbose_name=_('Class'))
    symbol = models.CharField(max_length=1, null=True, blank=True, verbose_name=_('Class Symbol'))

    history = HistoricalRecords()

    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    def __str__(self):
        return f"{self.get_full_name()} (ID: {self.id}, {self.phone_number})"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, parent_link=True, verbose_name=_('User'))
    telegram_id = models.IntegerField()

    def __str__(self):
        return self.user.get_full_name()


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, parent_link=True, verbose_name=_('User'))
    university = models.ForeignKey(University, null=True, on_delete=models.SET_NULL, verbose_name=_('University'))
    admission_year = models.PositiveIntegerField(verbose_name=_('Admission Year'))


class SessionManager(models.Manager):
    use_in_migrations = True

    def encode(self, session_dict):
        """
        Returns the given session dictionary serialized and encoded as a string.
        """
        return SessionStore().encode(session_dict)

    def save(self, session_key, session_dict, expire_date):
        s = self.model(session_key, self.encode(session_dict), expire_date)
        if session_dict:
            s.save()
        else:
            s.delete()  # Clear sessions with no data.
        return s


class Session(models.Model):
    """
    Session objects containing user session information.

    Django provides full support for anonymous sessions. The session
    framework lets you store and retrieve arbitrary data on a
    per-site-visitor basis. It stores data on the server side and
    abstracts the sending and receiving of cookies. Cookies contain a
    session ID -- not the data itself.

    Additionally this session object providers the following properties:
    ``user``, ``user_agent`` and ``ip``.
    """
    class Meta:
        verbose_name = _('session')
        verbose_name_plural = _('sessions')

    session_key = models.CharField(_('session key'), max_length=40, primary_key=True)
    session_data = models.TextField(_('session data'))
    expire_date = models.DateTimeField(_('expiry date'), db_index=True)

    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    user_agent = models.CharField(null=True, blank=True, max_length=200)
    last_activity = models.DateTimeField(auto_now=True)
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP')

    objects = SessionManager()

    def __str__(self):
        return f"Session {self.session_key} (User: {self.user}, Location: {location(self.ip)}, Device: {device(self.user_agent)}, Expires: {self.expire_date})"

    def get_decoded(self):
        return SessionStore(None, None).decode(self.session_data)


# At bottom to avoid circular import
from .backends.db import SessionStore  # noqa: E402 isort:skip
