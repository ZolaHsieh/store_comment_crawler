
from src import logging_, args
from src.google_map_crawler.run_google_map_crawler import run_gm_crawler
from src.foodpanda_crawler.run_foodpanda_crawler import run_fd_crawler

mode_type = {
    'gm_crawl' : run_gm_crawler,
    'fd_crawl' : run_fd_crawler
}

logger = logging_.getLogger(__name__)

def run_mode():
    try:
        logger.info(f'Running mode {args.mode}')
        mode_type[args.mode]()
    except Exception as run_exec:
        logger.error(run_exec)
    finally:
        logger.info(f'The end {args.mode}')

if __name__ == '__main__':
    run_mode()
