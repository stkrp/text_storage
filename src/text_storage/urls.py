from django.conf.urls import url, include

from .views import TextListView


api_urlpatterns = [
    url(r'^texts/$', TextListView.as_view(), name='api.text_list'),
]

ui_urlpatterns = [

]


urlpatterns = [
    url(r'^api/', include(api_urlpatterns)),
    url(r'^', include(ui_urlpatterns)),
]
