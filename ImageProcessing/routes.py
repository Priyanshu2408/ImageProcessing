from django.urls import re_path
from ImageProcessing.Views.ImageProcessingView import *

urlpatterns = [
    re_path(r'^health/check/v(?P<version_id>\d+)/', HealthCheckView.as_view()),
    # re_path(r'^details/v(?P<version_id>\d+)/$', .as_view()),
]