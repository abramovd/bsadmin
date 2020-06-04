from rest_framework import serializers


class PageSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()


class SlotSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    page = PageSerializer()


class BannerSnapshotModelSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    priority = serializers.IntegerField()
    countries = serializers.ListField()
    languages = serializers.ListField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    dismissible = serializers.BooleanField()
    stopped = serializers.BooleanField()

    body = serializers.CharField()

    slot = SlotSerializer()
    segments = serializers.ListField()


class BannerPublicationSerializer(serializers.Serializer):
    id = serializers.CharField()
    published_at = serializers.DateTimeField()
    banners = BannerSnapshotModelSerializer(many=True)
