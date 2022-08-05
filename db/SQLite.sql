-- SQLite
.open foodpanda_store_info.db
SELECT count() FROM foodpanda_store where city_name='台北市';

-- SELECT EXISTS (SELECT 1 
-- FROM foodpanda_store 
-- WHERE foodpanda_store.city_name='市'
-- ) AS anon_1;

delete from foodpanda_store_schedule;