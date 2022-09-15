"""
앱에서 사용하기 위한 데이터 베이스 테이블을 작성한 파일
클래스는 DB에서 테이블과, 각 멤버 객체들은 column에 대응한다
"""

from django.db import models


# Create your models here.


class database(models.Model):
    key_word = models.CharField(max_length=20, default="")
    time = models.DateTimeField()
