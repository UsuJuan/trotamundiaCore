from django_mongoengine import document, fields
from django.utils import timezone
from django.contrib.contenttypes.models import ContentTypeManager
from django.db import models
from django.contrib.auth.hashers import check_password, make_password


class DateField(fields.DateTimeField):
    def to_python(self, value):
        return super(DateField, self).to_python(value).date()

class PermissionManager(models.Manager):
    def get_by_natural_key(self, codename, app_label, model):
        return self.get(
            codename=codename,
            content_type=ContentType.objects.get_by_natural_key(app_label, model)
        )

class ContentType(document.Document):
    name = fields.StringField(max_length=100)
    app_label = fields.StringField(max_length=100)
    model = fields.StringField(max_length=100, verbose_name=('python model class name'),
                               unique_with='app_label')
    objects = ContentTypeManager()

    class Meta:
        verbose_name = ('content type')
        verbose_name_plural = ('content types')
        # db_table = 'django_content_type'
        # ordering = ('name',)
        # unique_together = (('app_label', 'model'),)

    def __unicode__(self):
        return self.name

    def model_class(self):
        "Returns the Python model class for this type of content."
        from django.db import models
        return models.get_model(self.app_label, self.model)

    def get_object_for_this_type(self, **kwargs):
        """
        Returns an object of this type for the keyword arguments given.
        Basically, this is a proxy around this object_type's get_object() model
        method. The ObjectNotExist exception, if thrown, will not be caught,
        so code that calls this method should catch it.
        """
        return self.model_class()._default_manager.using(self._state.db).get(**kwargs)

class Permission(document.Document):
    """The permissions system provides a way to assign permissions to specific
    users and groups of users.

    The permission system is used by the Django admin site, but may also be
    useful in your own code. The Django admin site uses permissions as follows:

        - The "add" permission limits the user's ability to view the "add"
          form and add an object.
        - The "change" permission limits a user's ability to view the change
          list, view the "change" form and change an object.
        - The "delete" permission limits the ability to delete an object.

    Permissions are set globally per type of object, not per specific object
    instance. It is possible to say "Mary may change news stories," but it's
    not currently possible to say "Mary may change news stories, but only the
    ones she created herself" or "Mary may only change news stories that have
    a certain status or publication date."

    Three basic permissions -- add, change and delete -- are automatically
    created for each Django model.
    """
    name = fields.StringField(max_length=50, verbose_name=('username'))
    content_type = fields.ReferenceField(ContentType)
    codename = fields.StringField(max_length=100, verbose_name=('codename'))
        # FIXME: don't access field of the other class
        # unique_with=['content_type__app_label', 'content_type__model'])

    objects = PermissionManager()

    class Meta:
        verbose_name = ('permission')
        verbose_name_plural = ('permissions')
        # unique_together = (('content_type', 'codename'),)
        # ordering = ('content_type__app_label', 'content_type__model', 'codename')

    def __unicode__(self):
        return u"%s | %s | %s" % (
            unicode(self.content_type.app_label),
            unicode(self.content_type),
            unicode(self.name))

    def natural_key(self):
        return (self.codename,) + self.content_type.natural_key()
    natural_key.dependencies = ['contenttypes.contenttype']

class Provider(document.EmbeddedDocument):
    uid = fields.StringField()
    display_name = fields.StringField(blank=True)
    photo_url = fields.URLField(blank=True)
    email = fields.EmailField(blank=False)
    provider_id = fields.StringField(blank=False)

class User(document.Document):
    SEXO_HOMBRE = 'masculino'
    SEXO_MUJER = 'femenino'
    SEXOS = (
        (None, 'No definido'),
        (SEXO_HOMBRE, 'Masculino'),
        (SEXO_MUJER, 'Femenino')
    )

    """A User document that aims to mirror most of the API specified by Django
        at http://docs.djangoproject.com/en/dev/topics/auth/#users
        """
    username = fields.StringField(
        max_length=250, verbose_name=('username'),
        help_text=("Required. 250 characters or fewer. Letters, numbers and @/./+/-/_ characters"), required=False)
    first_name = fields.StringField(
        max_length=250, blank=True, verbose_name=('first name'),)
    last_name = fields.StringField(
        max_length=250, blank=True, verbose_name=('last name'))
    email = fields.EmailField(verbose_name=('e-mail address'), blank=False)
    password = fields.StringField(
        blank=True,
        max_length=128,
        verbose_name=('password'),
        help_text=(
            "Use '[algo]$[iterations]$[salt]$[hexdigest]' or use the <a href=\"password/\">change password form</a>."))
    is_staff = fields.BooleanField(
        default=False,
        verbose_name=('staff status'),
        help_text=("Designates whether the user can log into this admin site."))
    is_active = fields.BooleanField(
        default=True,
        verbose_name=('active'),
        help_text=(
            "Designates whether this user should be treated as active. Unselect this instead of deleting accounts."))
    is_superuser = fields.BooleanField(
        default=False,
        verbose_name=('superuser status'),
        help_text=("Designates that this user has all permissions without explicitly assigning them."))
    last_login = fields.DateTimeField(
        default=timezone.now,
        verbose_name=('last login'))
    date_joined = fields.DateTimeField(
        default=timezone.now,
        verbose_name=('date joined'))
    user_permissions = fields.ListField(
        fields.ReferenceField(Permission), verbose_name=('user permissions'),
        blank=True, help_text=('Permissions for the user.'))

    birthdate = DateField(blank=True)
    # image = LocalStorageFileField(upload_to='users/')
    web_url = fields.URLField(blank=True)
    facebook_page = fields.URLField(blank=True)
    youtube_channel = fields.URLField(blank=True)
    genere = fields.StringField(choices=SEXOS, required=False,blank=True)
    is_complete = fields.BooleanField(default=False)
    providers = fields.ListField(fields.EmbeddedDocumentField('Provider'), blank=True)
    photo_url = fields.URLField(blank=True)
    uid = fields.StringField(blank=False, required=True)
    display_name = fields.StringField(blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    meta = {
        'allow_inheritance': True,
        'indexes': [
            {
                'fields': ['username'],
                'unique': True,
                'sparse': True
            }
        ]
    }

    def __unicode__(self):
        return self.username

    def get_full_name(self):
        """Returns the users first and last names, separated by a space.
        """
        full_name = u'%s %s' % (self.first_name or '', self.last_name or '')
        return full_name.strip()

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def set_password(self, raw_password):
        """Sets the user's password - always use this rather than directly
        assigning to :attr:`~mongoengine.django.auth.User.password` as the
        password is hashed before storage.
        """
        self.password = make_password(raw_password)
        self.save()
        return self

    def check_password(self, raw_password):
        """Checks the user's password against a provided password - always use
        this rather than directly comparing to
        :attr:`~mongoengine.django.auth.User.password` as the password is
        hashed before storage.
        """
        return check_password(raw_password, self.password)

    @classmethod
    def create_user(cls, username, password, email=None):
        """Create (and save) a new user with the given username, password and
        email address.
        """
        now = timezone.now()

        # Normalize the address by lowercasing the domain part of the email
        # address.
        if email is not None:
            try:
                email_name, domain_part = email.strip().split('@', 1)
            except ValueError:
                pass
            else:
                email = '@'.join([email_name, domain_part.lower()])

        user = cls(username=username, email=email, date_joined=now)
        user.set_password(password)
        user.save()
        return user

    def get_group_permissions(self, obj=None):
        """
        Returns a list of permission strings that this user has through his/her
        groups. This method queries all available auth backends. If an object
        is passed in, only permissions matching this object are returned.
        """
        permissions = set()
        for backend in auth.get_backends():
            if hasattr(backend, "get_group_permissions"):
                permissions.update(backend.get_group_permissions(self, obj))
        return permissions

    def get_all_permissions(self, obj=None):
        return _user_get_all_permissions(self, obj)

    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general. If an object is
        provided, permissions for this specific object are checked.
        """

        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app label.
        Uses pretty much the same logic as has_perm, above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return _user_has_module_perms(self, app_label)

    def email_user(self, subject, message, from_email=None):
        "Sends an e-mail to this User."
        from django.core.mail import send_mail
        send_mail(subject, message, from_email, [self.email])