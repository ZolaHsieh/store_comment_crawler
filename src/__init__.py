from src.common import setup_logger, setup_db, get_args


args = get_args.get_()
logging_ = setup_logger.setup()
store_reviews_db = setup_db.setup(args.db_type)

