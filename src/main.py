import argparse
import logging

# from common.setup_logger import logger
from src.google_map_crawler import main as gm_crawler


logger = logging.getLogger(__name__)
mode_type = {
    'gm_crawl' : gm_crawler
}

def run_mode():
    """A dummy description."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', help="Please enter the mode to run", required=True)
    args = parser.parse_args()

    try:
        mode_type[args.mode]()
    except Exception as run_exec:
        logger.error(run_exec)
        exit(1)
    else:
        logger.info('Running mode')


if __name__ == '__main__':
    run_mode()
