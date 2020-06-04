from django.conf.urls import url

from banners.api.views import LiveBannersView

urlpatterns = [
    url(r'^live/$', LiveBannersView.as_view(), name='')
]

