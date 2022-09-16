import json
import pathlib
import datetime
import requests
import my_logger


def send_json_to_model(model_json_file):
    #latest file 10
    model_api = "http://10.0.2.208:8000/keyword"
    try:
        res = requests.post(model_api, json=model_json_file)
        assert res.status_code == 200,  "Requset Failed check out header or request parameter"
        return res

    except Exception as e:
        logger.warning(e)


def send_json_to_service(json_data):
    service_api = 'http://10.0.2.208:8080/service/modeling'
    try:
        res = requests.post(service_api, json=json_data)
        assert res.status_code == 200,  "Requset Failed check out header or request parameter"
        return res

    except Exception as e:
        logger.warning(e)


if __name__ == '__main__':
    logger = my_logger.create_logger('Api')
    JSON_PATH = pathlib.Path(__file__).parent.joinpath("./json/")

    with open(JSON_PATH.joinpath('data_to_model.json'), "r") as json_file:
        model_json_file = json.load(json_file)

    json_data = send_json_to_model(model_json_file).json()
    
    now_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    json_data['date'] = now_date
    print(json_data)

    send_json_to_service(json_data)