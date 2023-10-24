# Store Comment Crawler

## Introduction
    

## Getting Started
- Run docker environment
```bash
    docker-compose up -d
    docker exec -it python bash
```

- Run job
```bash
    python -m src.main --mode fd_crawl --db_type mariadb
    python -m src.main --mode gm_crawl --db_type mariadb (--exist_g_update)
```

## Contribution

<!-- <a href="https://github.com/ZolaHsieh/google_comment_analysis/graphs/contributors"><img src="https://opencollective.com/google_comment_analysis/contributors.svg?width=890" /></a> -->


## License

<!-- [MIT](https://opensource.org/licenses/MIT) -->


## Issue Tracking
- Google 店家評論順序可能會調整

Copyright (c) 2022-present, Zola and Jay
