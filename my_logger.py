import logging
def create_logger():
    logger = logging.getLogger(name='crawl')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s:%(module)s:%(levelname)s:%(message)s %(funcName)s', datefmt='%Y-%m-%d %H:%M:%S')

    #consol logger
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    #file logger
    file_handler = logging.FileHandler('crawl.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
