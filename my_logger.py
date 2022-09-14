import logging
import pathlib
def create_logger():
    path = pathlib.Path(__file__).parent
    logger = logging.getLogger(name='scrap')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s:%(module)s:%(levelname)s:%(message)s %(funcName)s', datefmt='%Y-%m-%d %H:%M:%S')

    #consol logger
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    #file logger
    log_file_name = 'log/scrap.log'
    file_handler = logging.FileHandler(path.joinpath(log_file_name))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


# if __name__ == '__main__':
#     logger = create_logger()
#     logger.info("hello")