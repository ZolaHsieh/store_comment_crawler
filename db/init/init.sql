CREATE DATABASE IF NOT EXISTS `mydatabase`;
GRANT ALL ON `mydatabase`.* TO 'user'@'%';

-- create foodpanda_store table 
CREATE TABLE `foodpanda_store` (
  `city_name` varchar(16) NOT NULL,
  `city_url` varchar(256) DEFAULT NULL,
  `store_id` varchar(16) NOT NULL,
  `chain_id` varchar(16) NOT NULL,
  `store_name` varchar(256) NOT NULL,
  `rating` varchar(8) DEFAULT NULL,
  `store_url` varchar(256) NOT NULL,
  `address` varchar(1024) DEFAULT NULL,
  `longitude` varchar(16) DEFAULT NULL,
  `latitude` varchar(16) DEFAULT NULL,
  `chk` tinyint(1) DEFAULT NULL,
  `record_time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `foodpanda_store`
  ADD PRIMARY KEY (`city_name`,`store_id`,`chain_id`,`store_name`);
COMMIT;


-- create foodpanda_store_menu table 
CREATE TABLE `foodpanda_store_menu` (
  `dishes_id` varchar(16) NOT NULL,
  `dishes_code` varchar(64) DEFAULT NULL,
  `menu_url` varchar(256) DEFAULT NULL,
  `dishes_name` varchar(256) DEFAULT NULL,
  `description` varchar(1024) DEFAULT NULL,
  `display_price` varchar(16) DEFAULT NULL,
  `master_category_id` varchar(8) DEFAULT NULL,
  `category` varchar(128) DEFAULT NULL,
  `tags` varchar(128) DEFAULT NULL,
  `city_name` varchar(16) DEFAULT NULL,
  `store_id` varchar(16) DEFAULT NULL,
  `chain_id` varchar(16) DEFAULT NULL,
  `store_name` varchar(256) DEFAULT NULL,
  `record_time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `foodpanda_store_menu`
  ADD PRIMARY KEY (`dishes_id`),
  ADD KEY `store` (`city_name`,`store_id`,`chain_id`,`store_name`);

ALTER TABLE `foodpanda_store_menu`
  ADD CONSTRAINT `foodpanda_store_menu_ibfk_1` FOREIGN KEY (`city_name`,`store_id`,`chain_id`,`store_name`) REFERENCES `foodpanda_store` (`city_name`, `store_id`, `chain_id`, `store_name`, `store_url`);
COMMIT;

-- create foodpanda_store_schedule table
CREATE TABLE `foodpanda_store_schedule` (
  `id_` int(11) NOT NULL,
  `weekday` varchar(8) DEFAULT NULL,
  `opening_type` varchar(16) DEFAULT NULL,
  `opening_time` varchar(16) DEFAULT NULL,
  `closing_time` varchar(16) DEFAULT NULL,
  `city_name` varchar(16) DEFAULT NULL,
  `store_id` varchar(16) DEFAULT NULL,
  `chain_id` varchar(16) DEFAULT NULL,
  `store_name` varchar(256) DEFAULT NULL,
  `record_time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `foodpanda_store_schedule`
  ADD PRIMARY KEY (`id_`),
  ADD KEY `store` (`city_name`,`store_id`,`chain_id`,`store_name`);

ALTER TABLE `foodpanda_store_schedule`
  MODIFY `id_` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `foodpanda_store_schedule`
  ADD CONSTRAINT `foodpanda_store_schedule_ibfk_1` FOREIGN KEY (`city_name`,`store_id`,`chain_id`,`store_name`) REFERENCES `foodpanda_store` (`city_name`, `store_id`, `chain_id`, `store_name`);
COMMIT;


-- create google_store table
CREATE TABLE `google_store` (
  `name` varchar(256) NOT NULL,
  `services` varchar(64) DEFAULT NULL,
  `avg_rating` float DEFAULT NULL,
  `reviews_count` int(11) DEFAULT NULL,
  `reviews_url` varchar(256) DEFAULT NULL,
  `tags` varchar(128) DEFAULT NULL,
  `chk` tinyint(1) NOT NULL,
  `address` varchar(1024) DEFAULT NULL,

  `city_name` varchar(16) DEFAULT NULL,
  `store_id` varchar(16) DEFAULT NULL,
  `chain_id` varchar(16) DEFAULT NULL,
  `store_name` varchar(256) DEFAULT NULL,

  `record_time` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `google_store`
  ADD PRIMARY KEY `store` (`name`,`city_name`,`store_id`,`chain_id`);;

ALTER TABLE `google_store`
  ADD CONSTRAINT `google_store_ibfk_1` FOREIGN KEY (`city_name`,`store_id`,`chain_id`,`store_name`) REFERENCES `foodpanda_store` (`city_name`, `store_id`, `chain_id`, `store_name`,);
COMMIT;


-- create google_store_review table
CREATE TABLE `google_store_review` (
  `review_id` varchar(96) NOT NULL,
  `reviewer_id` varchar(32) NOT NULL,
  `reviewer_name` varchar(128) DEFAULT NULL,
  `reviewer_self_count` varchar(16) DEFAULT NULL,
  `reviewer_lang` varchar(16) DEFAULT NULL,
  `rating` float DEFAULT NULL,
  `date_range` varchar(16) DEFAULT NULL,
  `review_content` text(20000) DEFAULT NULL,
  `dining_mode` varchar(16) DEFAULT NULL,
  `dining_meal_type` varchar(16) DEFAULT NULL,
  `pic_url` text(20000) DEFAULT NULL,
  `phone_brand` varchar(64) DEFAULT NULL,
  `pic_date` varchar(16) DEFAULT NULL,

  `city_name` varchar(16) DEFAULT NULL,
  `store_id` varchar(16) DEFAULT NULL,
  `chain_id` varchar(16) DEFAULT NULL,
  `store_name` varchar(256) DEFAULT NULL,
  
  `record_time` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `google_store_review`
  ADD PRIMARY KEY (`review_id`);

ALTER TABLE `google_store_review`
  ADD CONSTRAINT `google_store_review_ibfk_1` FOREIGN KEY (`city_name`,`store_id`,`chain_id`,`store_name`) REFERENCES `google_store` (`city_name`, `store_id`, `chain_id`, `store_name`);
COMMIT;
