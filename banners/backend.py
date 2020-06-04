from django.utils import timezone
from django.db import transaction

from banners.constants import BannersPublicationState
from banners.models import Publication, Banner


@transaction.atomic
def publish(publisher):
    now = timezone.now()

    live_publication = Publication.objects.\
        select_for_update().\
        get_live_publication()

    if live_publication is not None:
        live_publication.state = BannersPublicationState.STATE_DEACTIVATED.value
        live_publication.save()

    new_publication = Publication.objects.create(
        state=BannersPublicationState.STATE_LIVE.value,
        published_by=publisher,
        published_at=now,
    )

    # making banners snapshots to display
    num_re_published, num_newly_published = Banner.objects.\
        publishable_banners().\
        republish_snapshots(new_publication)

    # marking as published
    Banner.objects.publishable_banners().\
        update(
            update_time=now,
            published_at=now,
    )

    return num_re_published, num_newly_published
