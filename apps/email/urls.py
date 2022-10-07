from django.urls import include, path
from rest_framework import routers
from apps.email.views import *
from django.conf.urls import url
# email_view = EmailViewSet()
# router = routers.DefaultRouter()
# router.register(r'email', EmailViewSet())
#
# urlpatterns = router.urls

urlpatterns = [
    url(r'^get_chart', get_line_chart_data, name="get_data"),
    url(r'^update_tbl', updateNewEmails, name="update_data"),
]
# urlpatterns += router.urls