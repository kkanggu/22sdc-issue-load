from datetime import date, timedelta

import mysql.connector

from dateutil import relativedelta
from fastapi import FastAPI
from pydantic import BaseModel


class dateAndDuration(BaseModel):
    def __getitem__(self, key):
        return getattr(self, key)

    startDate: str
    duration: str


def getStartDate(startDate: str):
    return date(int(startDate[:3]), int(startDate[5:6]), int(startDate[8:9]))


def isValidDateAndDuration(startDate: date, duration: str):
    if (
        ("daily" == duration)
        or ("weekly" == duration and 0 == startDate.weekday())
        or ("monthly" == duration and 1 == startDate.day)
    ):
        return True
    else:
        return False


def convertDuration(startDate: date, duration: str):
    startDateStr = startDate.strftime("%Y/%m/%d")
    endDateStr = ""

    if "daily" == duration:
        endDateStr = startDateStr
    elif "weekly" == duration:
        endDateStr = (startDate + timedelta(days=6)).strftime("%Y/%m/%d")
    else:
        endDateStr = (startDate + relativedelta.relativedelta(months=1) - timedelta(days=1)).strftime("%Y/%m/%d")

    return startDateStr + "~" + endDateStr


# 임시 함수, Scarpping 함수 작업이 완료되면 해당 구문 삭제 예정
def getScrappedData(temp: str):
    return list()


# 임시 함수, S3 세팅 후 업데이트 예정
def getKeywords(duration: str, datas):
    return str()


app = FastAPI()


@app.get("/")
async def getKeyword(dateInfo: dateAndDuration):
    startDate = getStartDate(dateInfo.startDate)

    if not isValidDateAndDuration(startDate, dateInfo.duration):
        return "Wrong Duration"

    duration = convertDuration(startDate, dateInfo.duration)

    try:
        config = {"user": "api", "password": "ipa", "host": "localhost", "database": "keyword"}
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        version_query = "SELECT MAX(version) FROM keyword"
        cursor.execute(version_query)
        version = cursor.fetchall()

        keyword_query = "SELECT keywords FROM keyword WHERE duration=(%s) AND version=(%s)"
        cursor.execute(keyword_query, (duration, version))
        keywords = cursor.fetchall()

        # Keyword not exist, request
        if 0 == keywords[0][0]:
            keywords = getKeywords(duration, getScrappedData(duration)).split(" ")

            update_query = "INSERT INTO keyword (duration, version, keywords) VALUES (%s, %s, %s)"

            for keyword in keywords:
                cursor.execute(update_query, version, keyword)

            connection.commit()

    except mysql.connector.Error as error:
        print("Query Failed {}".format(error))
    finally:
        cursor.close()
        connection.close()

    return keywords
