import json
import pathlib
import requests
import my_logger


def send_json_to_model():
    #latest file 10
    with open(JSON_PATH.joinpath('data_to_model.json')) as json_file:
        model_json = json.load(json_file)

    model_api = "http://10.0.2.208:8000/keyword"
    try:
        res = requests.post(model_api, json=model_json)
        assert res.status_code == 200,  "Requset Failed check out header or request parameter"
        print(res.text)

    except Exception as e:
        logger.warning(e)


if __name__ == '__main__':
    logger = my_logger.create_logger('Api')
    JSON_PATH = pathlib.Path(__file__).parent.joinpath("./json/")
    send_json_to_model()

