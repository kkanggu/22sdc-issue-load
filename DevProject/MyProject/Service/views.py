"""
request가 최종적으로 라우팅되어 동작시킬 로직이 정의된 파일
"""

import datetime
import json

from django.http import JsonResponse

# from django.shortcuts import render
from rest_framework.decorators import api_view

from .models import database
from .serializers import DBSerializer


# Create your views here.


@api_view(["POST"])
def Kword_save(request):
    body = json.loads(request.body.decode("utf-8"))
    time_data = body["date"]
    key_list = body["keywords"]
    DB_store = database()
    for data in key_list:
        DB_store.time = time_data
        DB_store.key_word = data
        DB_store.save()
    return JsonResponse("Success!", safe=False, status=201)


@api_view(["GET"])
def req_app(request):
    now_date = datetime.datetime.now()
    before_ten = now_date - datetime.timedelta(minutes=10)
    query_set = database.objects.filter(time__gte=before_ten)
    serializer = DBSerializer(query_set, many=True)
    return JsonResponse(serializer.data, safe=False)
