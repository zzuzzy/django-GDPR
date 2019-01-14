# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-19 15:17
from __future__ import unicode_literals

from django.apps import apps
from django.db import migrations
from django.db.models import Count

from tqdm import tqdm


def remove_duplicate_legal_reasons(apps, purpose_slug, source_object_content_type, source_object_id):
    LegalReason = apps.get_model('gdpr', 'LegalReason')
    duplicate_legal_reason_qs = LegalReason.objects.filter(
        purpose_slug=purpose_slug,
        source_object_content_type=source_object_content_type,
        source_object_id=source_object_id
    )

    if duplicate_legal_reason_qs.filter(is_active=True).count() > 0:
        duplicate_legal_reason_qs.filter(is_active=False).delete()

    latest_legal_reason = duplicate_legal_reason_qs.latest('expires_at')
    duplicate_legal_reason_qs.exclude(pk=latest_legal_reason.pk).delete()


def check_uniqueness_and_keep_latest_active_legal_reason(apps, schema_editor):
    LegalReason = apps.get_model('gdpr', 'LegalReason')
    check_qs = LegalReason.objects.values('purpose_slug', 'source_object_content_type', 'source_object_id').annotate(
        lr_count=Count('purpose_slug')).filter(lr_count__gt=1).order_by('-lr_count').distinct()

    for legal_reason in tqdm(check_qs.all()):
        remove_duplicate_legal_reasons(apps, legal_reason['purpose_slug'], legal_reason['source_object_content_type'],
                                       legal_reason['source_object_id']
        )


def remove_duplicate_legal_reasons_relatives(apps, legal_reason, object_content_type, object_id):
    LegalReasonRelatedObject = apps.get_model('gdpr', 'LegalReasonRelatedObject')
    duplicates_qs = LegalReasonRelatedObject.objects.filter(
        legal_reason=legal_reason,
        object_content_type=object_content_type,
        object_id=object_id
    )
    latest_legal_reason_related_object = duplicates_qs.latest('created_at')
    duplicates_qs.exclude(pk=latest_legal_reason_related_object.pk).delete()


def check_uniqueness_and_keep_latest_active_legal_reason_related_object(apps, schema_editor):
    LegalReasonRelatedObject = apps.get_model('gdpr', 'LegalReasonRelatedObject')
    check_qs = LegalReasonRelatedObject.objects.values('legal_reason', 'object_content_type', 'object_id').annotate(
        lrro_count=Count('legal_reason')).filter(lrro_count__gt=1).order_by('-lrro_count').distinct()

    for legal_reason_related_object in tqdm(check_qs.all()):
        remove_duplicate_legal_reasons_relatives(apps, legal_reason_related_object['legal_reason'],
                                                 legal_reason_related_object['object_content_type'],
                                                 legal_reason_related_object['object_id']
        )


class Migration(migrations.Migration):

    dependencies = [
        ('gdpr', '0002_auto_20180509_1518'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]
    operations = [
        migrations.AlterField(
            model_name='legalreason',
            name='purpose_slug',
            field=models.CharField(choices=[], db_index=True,
                                   max_length=100, verbose_name='purpose'),
        ),
        migrations.AlterField(
            model_name='legalreason',
            name='source_object_id',
            field=models.TextField(verbose_name='source object ID', db_index=True),
        ),
        migrations.AlterField(
            model_name='legalreasonrelatedobject',
            name='object_id',
            field=models.TextField(verbose_name='related object ID', db_index=True),
        ),
        migrations.RunPython(check_uniqueness_and_keep_latest_active_legal_reason),
        migrations.RunPython(check_uniqueness_and_keep_latest_active_legal_reason_related_object),
    ]
