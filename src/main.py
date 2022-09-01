import argparse
from src import logging_
from src.google_map_crawler.run_google_map_crawler import run_gm_crawler
from src.foodpanda_crawler.run_foodpanda_crawler import run_fd_crawler

mode_type = {
    'gm_crawl' : run_gm_crawler,
    'fd_crawl' : run_fd_crawler
}
logger = logging_.getLogger(__name__)

def run_mode():
    """A dummy description."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', help="Please enter the mode to run", required=True)


    args = parser.parse_args()

    try:
        logger.info(f'Running mode {args.mode}')
        mode_type[args.mode]()
    except Exception as run_exec:
        logger.error(run_exec)
    finally:
        logger.info(f'The end {args.mode}')

if __name__ == '__main__':
    run_mode()
