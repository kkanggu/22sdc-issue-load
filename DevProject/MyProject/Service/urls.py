"""
root app에서 라우팅된 request의 엔드포인트에 따라 라우팅될 view가 정의된 파일
"""
from django.urls import path

from .views import Kword_save, req_app


urlpatterns = [
    path("modeling/", Kword_save),
    path("need/", req_app),
]
