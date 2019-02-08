from dateutil.relativedelta import relativedelta

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from chamber.models import SmartModel

from .purposes.default import purposes_map


class LegalReasonManager(models.Manager):

    def create_consent(self, purpose_slug, source_object, issued_at=None, tag=None, related_objects=None):
        """
        Create (or update, if it exist) a LegalReason with purpose slug for concrete object instance

        Args:
            purpose_slug: String of Legal Reason purpose
            source_object: Source object this Legal Reason is related to
            issued_at: When the Legal Reason consent was given
            tag: String that the developer can add to the created consent and use it to mark his business processes
            related_objects: Objects this Legal Reason relates to (ie. order, registrations etc.)

        Returns:
            Legal Reason: LegalReason object
        """
        purpose = purposes_map[purpose_slug]
        issued_at = issued_at or timezone.now()

        legal_reason, created = LegalReason.objects.get_or_create(
            source_object_content_type=ContentType.objects.get_for_model(source_object.__class__),
            source_object_id=str(source_object.pk),
            purpose_slug=purpose_slug,
            defaults={
                'issued_at': issued_at,
                'expires_at': issued_at + purpose.expiration_timedelta,
                'tag': tag,
                'is_active': True
                }
            )

        if not created:
            legal_reason.change_and_save(expires_at=timezone.now() + purpose.expiration_timedelta, tag=tag,
                                         is_active=True
            )

        for related_object in related_objects or ():
            legal_reason.related_objects.update_or_create(
                object_content_type=ContentType.objects.get_for_model(related_object.__class__),
                object_id=related_object.pk
            )

        return legal_reason

    def deactivate_consent(self, purpose_slug, source_object):
        """
        Deactivate/Remove consent (Leagal reason) for source_object, purpose_slug combination

        Args:
            purpose_slug: Purpose slug to deactivate consent for
            source_object: Source object to deactivate consent for
        """
        LegalReason.objects.filter_source_instance_active_non_expired(source_object).filter(
            purpose_slug=purpose_slug).update(is_active=False)

    def exists_valid_consent(self, purpose_slug, source_object):
        """
        Returns True if source_object has valid (ie. active and non-expired) consent (Legal Reason)

        Args:
            purpose_slug: Purpose_slug to check consent for
            source_object: Source object to check consent for
        """
        return LegalReason.objects.filter_source_instance_active_non_expired(
            source_object).filter(purpose_slug=purpose_slug).exists()


class LegalReasonQuerySet(models.QuerySet):

    def filter_expired_retaining_data_in_last_days(self, days=None):
        """
        Filters all Legal Reason that retain data and that expired in last days

        Args:
            days: Number of days in the past. If not provided, all Legal Reasons retaining data which expired in the
            past will be returned.
        """
        purpose_slugs_retaining_data = [slug for slug, cls in purpose_register.items() if cls.is_retaining_data]

        filter_keys = {
            'expires_at__lt': timezone.now(),
        } if days is None else {
            'expires_at__gt': timezone.now() - relativedelta(days=days),
            'expires_at__lt': timezone.now()
        }

        return self.filter(purpose_slug__in=purpose_slugs_retaining_data, **filter_keys)

    def filter_non_expired(self):
        return self.filter(expires_at__gte=timezone.now())

    def filter_active_and_non_expired(self):
        return self.filter(is_active=True).filter_non_expired()

    def filter_source_instance(self, source_object):
        return self.filter(source_object_content_type=ContentType.objects.get_for_model(source_object.__class__),
                           source_object_id=str(source_object.pk))

    def filter_source_instance_active_non_expired(self, source_object):
        return self.filter_source_instance(source_object).filter_active_and_non_expired()


class LegalReason(SmartModel):

    objects = LegalReasonManager.from_queryset(LegalReasonQuerySet)()

    issued_at = models.DateTimeField(
        verbose_name=_('issued at'),
        null=False,
        blank=False,
    )
    expires_at = models.DateTimeField(
        verbose_name=_('expires at'),
        null=False,
        blank=False,
        db_index=True
    )
    tag = models.CharField(
        verbose_name=_('tag'),
        null=True,
        blank=True,
        max_length=100
    )
    is_active = models.BooleanField(
        verbose_name=_('is active'),
        default=True
    )
    purpose_slug = models.CharField(
        verbose_name=_('purpose'),
        null=False,
        blank=False,
        choices=(
            (purpose_slug, purpose_class.name)
            for purpose_slug, purpose_class in purposes_map.items()
        ),
        max_length=100
    )
    source_object_content_type = models.ForeignKey(
        ContentType,
        verbose_name=_('source object content type'),
        null=False,
        blank=False
    )
    source_object_id = models.TextField(
        verbose_name=_('source object ID'),
        null=False, blank=False
    )
    source_object = GenericForeignKey(
        'source_object_content_type', 'source_object_id'
    )

    @property
    def purpose(self):
        return purposes_map.get(self.purpose_slug, None)

    def __str__(self):
        return '{purpose_slug}'.format(purpose_slug=self.get_purpose_slug_display())

    class Meta:
        verbose_name = _('legal reason')
        verbose_name_plural = _('legal reasons')
        ordering = ('-created_at',)
        unique_together = ('purpose_slug', 'source_object_content_type', 'source_object_id')


class LegalReasonRelatedObject(SmartModel):

    legal_reason = models.ForeignKey(
        LegalReason,
        verbose_name=_('legal reason'),
        null=False,
        blank=False,
        related_name='related_objects'
    )
    object_content_type = models.ForeignKey(
        ContentType,
        verbose_name=_('related object content type'),
        null=False,
        blank=False
    )
    object_id = models.TextField(
        verbose_name=_('related object ID'),
        null=False,
        blank=False
    )
    object = GenericForeignKey(
        'object_content_type', 'object_id'
    )

    def __str__(self):
        return '{legal_reason} {object}'.format(legal_reason=self.legal_reason, object=self.object)

    class Meta:
        verbose_name = _('legal reason related object')
        verbose_name_plural = _('legal reasons related objects')
        ordering = ('-created_at',)
        unique_together = ('legal_reason', 'object_content_type', 'object_id')


class AnonymizedData(SmartModel):

    field = models.CharField(
        verbose_name=_('anonymized field name'),
        max_length=250,
        null=False,
        blank=False
    )
    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_('related object content type'),
        null=False,
        blank=False
    )
    object_id = models.TextField(
        verbose_name=_('related object ID'),
        null=False,
        blank=False
    )
    object = GenericForeignKey(
        'content_type', 'object_id'
    )
    is_active = models.BooleanField(
        verbose_name=_('is active'),
        default=True
    )
    expired_reason = models.ForeignKey(
        LegalReason,
        verbose_name=_('expired reason'),
        null=True,
        blank=True
    )

    def __str__(self):
        return '{field} {object}'.format(field=self.field, object=self.object)

    class Meta:
        verbose_name = _('anonymized data')
        verbose_name_plural = _('anonymized data')
        ordering = ('-created_at',)
