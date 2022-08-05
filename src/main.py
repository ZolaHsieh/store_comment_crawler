import argparse
import logging

# from common.setup_logger import logger




if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info('Start job.')

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--store', action="store_true")
    parser.add_argument('-m', '--menu', action="store_true")
    parser.add_argument('-uc', '--update_chain', action="store_true")
    

    args = parser.parse_args()