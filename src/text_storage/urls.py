from django.conf.urls import url, include

from .views import TextListAPIView, TextListView


api_urlpatterns = [
    url(r'^texts/$', TextListAPIView.as_view(), name='api.text_list'),
]

ui_urlpatterns = [
    url(r'^texts/$', TextListView.as_view(), name='ui.text_list'),
]


urlpatterns = [
    url(r'^api/', include(api_urlpatterns)),
    url(r'^', include(ui_urlpatterns)),
]
