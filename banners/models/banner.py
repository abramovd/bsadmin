import uuid
import base64
import json

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.conf import settings
from django.db.models.manager import BaseManager
from django.core.serializers.json import DjangoJSONEncoder

from banners.models.publication import Publication
from banners.models.slot import Slot
from helpers.fields import ChoiceArrayField
from helpers.models import BaseModel


SUPPORTED_LANGUAGES = settings.BSADMIN_SETTINGS['SUPPORTED_LANGUAGES']
SUPPORTED_COUNTRIES = settings.BSADMIN_SETTINGS['SUPPORTED_COUNTRIES']


class BaseBanner(BaseModel):
    priority = models.SmallIntegerField(default=10)
    countries = ChoiceArrayField(
        models.CharField(
            max_length=2,
            choices=(
                (country, country)
                for country in SUPPORTED_COUNTRIES
            )
        ),
        blank=True, default=list,
        help_text='Leave empty to support all countries',
    )

    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    dismissible = models.BooleanField(default=True)
    stopped = models.BooleanField(default=False)

    body = models.TextField()

    languages = ChoiceArrayField(
        models.CharField(
            max_length=3,
            choices=(
                (lang, lang)
                for lang in SUPPORTED_LANGUAGES
            )
        ),
        blank=True, default=list,
    )
    hash_base64 = models.TextField(unique=True, max_length=256)

    def to_copy(self):
        raise NotImplementedError

    def get_hash(self):
        return base64.b64encode(
            json.dumps(
                self.to_copy(),
                cls=DjangoJSONEncoder,
            ).encode()
        )

    def save(self, *args, **kwargs):
        self.hash_base64 = self.get_hash()
        super(BaseBanner, self).save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ('-create_time', )

    def dump(self):
        return {
            'priority': self.priority,
            'countries': self.countries,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'dismissible': self.dismissible,
            'stopped': self.stopped,
            'body': self.body,
            'languages': self.languages,
        }


class BannerQuerySet(models.QuerySet):

    def delete(self):
        return self.update(active=False)

    def duplicate(self):
        new_banners = []
        for banner in self.all():
            banner.pk = None
            banner.published_at = None
            banner.name = banner.name[:80] + f' (copy {uuid.uuid4()})'
            banner.hash_base64 = banner.get_hash()
            new_banners.append(banner)
        return self.bulk_create(new_banners)

    def publishable_banners(self):
        return self.filter(slot__hidden=False)

    def not_publishable_banners(self):
        return self.exclude(slot__hidden=False)

    def republish_snapshots(self, to_publication):
        to_republish = BannerSnapshot.objects.filter(
            original_banner__in=self.all(),
            original_banner__hash_base64=models.F('hash_base64')
        )
        num_republished = to_republish.update(
            publication=to_publication,
        )
        to_publication.snapshots_log.add(
            *to_republish.values_list('id', flat=True)
        )
        to_publish = self.exclude(
            snapshots__hash_base64=models.F('hash_base64')
        )

        snapshots_to_create = []
        for banner in to_publish:
            snapshot = BannerSnapshot(
                original_banner=banner,
                publication=to_publication,
                **banner.to_copy()
            )
            snapshot.hash_base64 = snapshot.get_hash()
            snapshots_to_create.append(snapshot)

        BannerSnapshot.objects.bulk_create(snapshots_to_create)

        to_publication.snapshots_log.add(
            *to_publish.values_list('id', flat=True)
        )
        return num_republished, len(snapshots_to_create)


class ActiveBannerManager(BaseManager.from_queryset(BannerQuerySet)):
    def get_queryset(self):
        qs = super(ActiveBannerManager, self).get_queryset()
        qs = qs.filter(active=True)
        return qs


class Banner(BaseBanner):
    name = models.CharField(unique=True, max_length=256)
    slot = models.ForeignKey(
        Slot, on_delete=models.PROTECT,
    )

    segments = ChoiceArrayField(
        models.CharField(
            max_length=256,
        ),
        blank=True,
        default=list,
    )
    published_at = models.DateTimeField(blank=True, null=True)

    active = models.BooleanField(default=True)

    objects = ActiveBannerManager()

    def to_copy(self):
        dump = super(Banner, self).dump()
        dump.update(
            {
                'name': self.name,
                'slot': self.slot.to_dict(),
                'segments': self.segments,
            }
        )
        return dump

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.active = False
        self.save()


class BannerSnapshot(BaseBanner):
    name = models.CharField(max_length=256)
    slot = JSONField()
    segments = JSONField()

    original_banner = models.ForeignKey(
        Banner,
        on_delete=models.CASCADE,
        related_name='snapshots',
    )
    publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='banners',
    )
    publications_log = models.ManyToManyField(
        Publication, blank=True,
        related_name='snapshots_log',
    )

    def to_copy(self):
        dump = super(BannerSnapshot, self).dump()
        dump.update(
            {
                'name': self.name,
                'slot': self.slot,
                'segments': self.segments,
            }
        )
        return dump
