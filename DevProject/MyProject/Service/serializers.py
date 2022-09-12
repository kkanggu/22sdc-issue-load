from rest_framework import serializers

from .models import database


# Service 모델의 데이터를  title body answer를 담고 있는 json 타입의 데이터로 변환
class DBSerializer(serializers.ModelSerializer):
    class Meta:
        model = database
        fields = ("kword", "time")
