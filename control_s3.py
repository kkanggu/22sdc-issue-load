import datetime
import json
import pathlib
import boto3
import my_logger

def upload_json():
    try:
        now = datetime.datetime.now()
        key = "json/" + datetime.datetime.strftime(now, "%Y-%m-%d %H:%M") + ".json"
        s3.upload_file(str(FILE_PATH), BUCKET_NAME, key)
        logger.info("Upload json to S3!")
    
    except Exception as e:
        logger.warning(e)


def create_json_to_send():
    try:
        file_list = (s3.list_objects(Bucket=BUCKET_NAME, Prefix='json/')['Contents'])[-10:-1]
        s3_objects = [s3.get_object(Bucket=BUCKET_NAME, Key=content['Key']) for content in file_list]
        json_objects = [json.loads(obj_dict['Body'].read().decode()) for obj_dict in s3_objects]
        title_contents = [article['title'] + " " + article['content'] for j_obj in json_objects for article in j_obj]
        model_json = {'articles': title_contents}

        with open(JSON_PATH.joinpath('data_to_model.json'), "w") as json_file:
            json.dump(model_json, json_file, indent=4)
        
        logger.info("Create json file to send model.")

    except Exception as e:
        logger.warning(e)


if __name__ == "__main__":
    s3 = boto3.client('s3', region_name='ap-northeast-2')
    BUCKET_NAME = "issue-keyword-storage"
    JSON_PATH = pathlib.Path(__file__).parent.joinpath("./json/")
    FILE_PATH = JSON_PATH.joinpath("last_scrapped.json")
    logger = my_logger.create_logger('S3')
    upload_json()
    create_json_to_send()