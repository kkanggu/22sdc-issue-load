import aiohttp
import asyncio
from bs4 import BeautifulSoup as bs
import datetime
import json
import pathlib
import re
import requests
import my_logger

def get_exist_aritcle_codes():
    """
    Read exist article codes in latest json file

    Returns:
        list: exists aritcle codes in json file
    """
    aritcle_codes = []
    try:
        with open(FILE_PATH, "r") as json_file:
            last_infos = json.load(json_file)
            if last_infos:
                aritcle_codes = [info.get('article_code') for info in last_infos]
    
    except Exception as e:
        logger.warning(e)
    
    finally:
        return aritcle_codes


def get_article_info_urls(board_name):
    """
    Sends get request to blind and gets valid urls of articles.
    Filter valid urls by checking data is already in json file.
    
    Args:
        exist_article_codes(list): article codes already exist in main json file
    
    Return:
        list: urls of valid articles, not exist in json file
    """
    try:
        url = f"{base_url}/kr/topics/{board_name}"
        resp = requests.get(url, headers=headers)
        assert resp.status_code == 200, "Requset Failed check out header or request parameter"
    
        soup = bs(resp.text, 'html.parser')
        scrapped_urls = [a['href'] for a in soup.select('.article-list-pre .category > a') if a.has_attr('href')]
        article_codes = [href.split("-")[-1] for href in scrapped_urls]
        #get already existed articles codes
        exist_article_codes = set(get_exist_aritcle_codes())
        valid_urls = [url for url, code in zip(scrapped_urls, article_codes) if code not in exist_article_codes]
        return valid_urls
    
    except Exception as e:
        logger.error(e)


async def get_all_article(article_urls):
    """
    Sends requests to each article url and get information of each articles.
    
    Args:
        article_urls (list): urls of valid article
    
    Return:
        infos(list): list of info dictionaries
    """
    
    #create tasks to async job
    tasks = [asyncio.create_task(get_article_info(base_url + l)) for l in article_urls]
    infos = await asyncio.gather(*tasks)
    return infos


async def get_article_info(article_url):
    """
    Return info of one article
    Run formatting function to change data format.
    Create information dictionary of article.

    Args:
        article_url (str): url of article

    Returns:
        dictionary: 
            {
                date:"2022-08-01-07:00", "name": "한샘", title:"블라보면 징징이가 왜이리 많은지",
                content:"9급이나 대기업이나. 걍 하면 되는거지 꼭 물고 뜯고 뒤지게 싸우는지 왜", "url":"https://..."
            }
    """

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(article_url) as resp:
                assert resp.status == 200, "Requset Failed" #if reponse has error then occur exception
                html_text = await resp.text()
                
                #get parsed data of html text
                date, name, title, content = parse_article_info(html_text)
                
                #If author is 팀 블라인드 then article is advertise or announcemnet.
                assert name != '팀블라인드', "This article is advertise"
                
                #convert date format to yyyy-mm-dd hh-MM
                foramtted_date = convert_date_format(date)
                article_code = article_url.split("-")[-1]

                keys = ["article_code", "date","name", "title", "content", "url"]
                values = [article_code, foramtted_date, name, title, content, article_url]
                info = {k:v for k, v in zip(keys, values)}
                return info
    

    except Exception as e:
        logger.warning(e)


def convert_date_format(raw_date):
    """
    Convert date time format to (yyyy-mm-dd HH:MM) from blind's raw date format "8 min", "1 hour", "3 days".
    Use regex to extract time unit and amount in raw data and convert it to timedelta.
    Finally minus time delta object from datetime.now() and convert it to string.
    
    "방금" converted to timedelta(mins=0)
    "어제" converted to timedelta(days=1)

    Args:
        raw_date (str): raw date format 
    
    Return:
        date(str): creation date with yyyy-mm-dd HH:MM format.
    """

    #find time amount, unit by regex
    time_amount = ''.join(re.findall('\d', raw_date))
    time_unit = ''.join(re.findall('[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]', raw_date))
    # print(time_amount, time_unit)
    try:
        if time_amount: 
            time_amount = int(time_amount)
            if time_unit == "분":
                time_ago = datetime.timedelta(minutes=time_amount)
            elif time_unit == "시간":
                time_ago = datetime.timedelta(hours=time_amount)
            elif time_unit == "일":
                time_ago = datetime.timedelta(days=time_amount)
        
        else:
            if time_unit ==  "방금":
                time_ago = datetime.timedelta(minutes=0)
            elif time_unit == "어제":
                time_ago = datetime.timedelta(days=1)
            else:
                return 

        date = datetime.datetime.now() - time_ago
        date = date.strftime("%Y-%m-%d %H: %M")
        return date
    
    except Exception as e:
        # logger.warning(f"raw_date: {raw_date} ,amonut :{time_amount} unit: {time_unit}")
        logger.warning(e)


def parse_article_info(html_text):
    """
    Parse article html to extract title, content, author company, date.
    This fuction extract the data as raw text data.

    Args:
        html_text(str): html text of article page
    
    Return:
        list: datas in article html page
        ["8분", "새회사", "경찰들 일좀 하세요", "연락너무 늦고 처리 늦어서 뺑소니 직접 잡음. 노력이라도 하던가..."]
    """
    
    try:
        soup = bs(html_text, 'html.parser')
        #parse elements in page
        title = soup.select_one('.article-view-head h2')
        name = soup.select_one('.article-view-head .name > *')
        content = soup.select_one('.article-view-contents .contents-txt')
        date = soup.select_one('.wrap-info .date')

        decompose_tags = lambda element: element.decompose() if element else element
        
        #decompose not needed tag
        decompose_tags(date.find("i"))
        decompose_tags(title.find("a"))
        decompose_tags(content.find("br"))

        parsing_data = [d.get_text() for d in [date, name, title, content]]
        return parsing_data
    
    except Exception as e:
        # logger.warning(title, date, name, content)
        logger.warning(e)


def create_json(infos):
    try:
        infos = sorted(infos, key=lambda x: x['date'])
        with open(FILE_PATH, "w") as json_file:
            json.dump(infos, json_file, indent=4)
        return

    except Exception as e:
        logger.warning(e)


async def run():
    """
    Run scrapping and Upload json result to S3
    """

    #should change as article code
    try:
        board_name = "블라블라"
        encoded_board_name = requests.utils.quote(board_name)
        urls = get_article_info_urls(encoded_board_name)
        if urls:
            #drop advertise articles
            infos = [info for info in await get_all_article(urls) if info]
            
            logger.info(f"Counts of new articles : {len(infos)}")
            #when new article is morethan 50
            if len(infos) > 50:
                create_json(infos)
            
            else:
                logger.info("Not enough new articles")
    
    except Exception as e:
        logger.warning(e)


if __name__ == '__main__':
    #use pathlib to set path option
    JSON_PATH = pathlib.Path(__file__).parent.joinpath("./json/")
    FILE_PATH = JSON_PATH.joinpath("last_scrapped.json")
    #add your user agent 
    headers = ''

    #blind base url
    base_url = "https://www.teamblind.com"
    logger = my_logger.create_logger('Scrap')
    asyncio.run(run())