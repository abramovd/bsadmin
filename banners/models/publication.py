from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.manager import BaseManager

from banners.constants import BannersPublicationState
from helpers.models import BaseModel


class PublicationQuerySet(models.QuerySet):

    def get_live_publication(self):
        try:
            obj = self.get(state=BannersPublicationState.STATE_LIVE.value)
        except Publication.DoesNotExist:
            obj = None
        return obj


class Publication(BaseModel):
    state = models.CharField(
        choices=(
            (
                BannersPublicationState.STATE_DEACTIVATED.value,
                'Deactivated'
            ),
            (
                BannersPublicationState.STATE_LIVE.value,
                'Live (published)'
            ),
        ),
        max_length=128,
    )
    published_at = models.DateTimeField()
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    objects = BaseManager.from_queryset(PublicationQuerySet)()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['state'],
                condition=Q(
                    state=BannersPublicationState.STATE_LIVE.value,
                ),
                name='unique_live_publication',
            )
        ]
        ordering = ('-create_time',)
