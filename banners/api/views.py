from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from .serializers import BannerPublicationSerializer
from banners.models import Publication


def get_paginated_response(paginator, data):
    result = {
        'count': paginator.count,
        'next': paginator.get_next_link(),
        'previous': paginator.get_previous_link(),
    }
    result.update(data)
    return Response(result)


class LiveBannersView(APIView):

    def get(self, request):
        live_publication = Publication.objects.get_live_publication()
        if live_publication is None:
            return Response({})

        banners = live_publication.banners.all()

        paginator = LimitOffsetPagination()
        banners_page = paginator.paginate_queryset(
            banners, request,
        )
        if banners_page is not None:
            banners = banners_page

        serializer = BannerPublicationSerializer(
            {
                'id': live_publication.id,
                'published_at': live_publication.published_at,
                'banners': banners,
            }
        )

        return get_paginated_response(paginator, serializer.data)
