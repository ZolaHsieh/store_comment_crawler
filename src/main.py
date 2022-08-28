import argparse
from src import logging_
from src.google_map_crawler.main import crawler as gm_crawl
from src.foodpanda_crawler.run_foodpandas_crawler import run_fd_crawler

mode_type = {
    'gm_crawl' : gm_crawl,
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
        pass

if __name__ == '__main__':
    run_mode()
