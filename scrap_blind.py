import aiohttp
import asyncio
from bs4 import BeautifulSoup as bs
import datetime
import json
import re
import requests
import my_logger

def get_article_info_urls(board_name):
    """
    Sends get request to blind and gets valid urls of articles.
    Filter valid urls by checking data is already in csv file.
    
    Args:
        exist_article_codes(list): article codes already exist in main csv file
    
    Return:
        list: urls of valid articles, not exist in csv file
    """
    try:
        url = f"{base_url}/kr/topics/{board_name}"
        resp = requests.get(url, headers=headers)
        assert resp.status_code == 200, "Requset Failed"
    
        soup = bs(resp.text, 'html.parser')
        hrefs = [a['href'] for a in soup.select('.article-list-pre .category > a') if a.has_attr('href')]
        return hrefs
    
    except Exception as e:
        logger.error(e)


async def get_all_aritcle(article_urls):
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
    print(f"article counts: {len(infos)}")
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
    now = datetime.datetime.now()
    file_name = JSON_PATH + datetime.datetime.strftime(now, "%Y-%m-%d %H:%M") + ".json"
    with open(file_name, "w") as json_:
        json.dump(infos, json_, indent=4)
    return


async def run():
    """
    Run scrapping each 10 minutes.
    """

    #should change as article code
    board_name = "자동차"
    encoded_board_name = requests.utils.quote(board_name)
    urls = get_article_info_urls(encoded_board_name)
    infos = await get_all_aritcle(urls)
    create_json(infos)
    # update_csv(csv_file, infos)


if __name__ == '__main__':
    JSON_PATH = "./json/"
    #add your user agent 
    headers = ''

    #blind base url
    base_url = "https://www.teamblind.com"

    logger = my_logger.create_logger()
    asyncio.run(run())