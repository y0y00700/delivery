-- psql -v run_id=p51_실행ID 에서 사용. 조회 전용.
BEGIN READ ONLY;

SELECT current_database() AS database_name,
       current_setting('server_version') AS postgres_version;

SELECT user_id, login_id, user_type,
       (left(password, 4) IN ('$2a$', '$2b$', '$2y$') AND length(password) = 60) AS bcrypt_format,
       created_at IS NOT NULL AS created_at_set,
       modified_at IS NOT NULL AS modified_at_set
FROM users
WHERE left(login_id, length(:'run_id') + 1) = :'run_id' || '_'
ORDER BY user_id;

SELECT m.menu_id, m.price, m.deleted_at IS NOT NULL AS soft_deleted,
       m.created_at IS NOT NULL AS created_at_set,
       m.modified_at IS NOT NULL AS modified_at_set,
       m.modified_at > m.created_at AS modification_recorded
FROM menus m JOIN users u ON u.user_id = m.owner_id
WHERE left(u.login_id, length(:'run_id') + 1) = :'run_id' || '_'
ORDER BY m.menu_id;

SELECT o.order_id, o.menu_id, o.order_status, o.quantity, o.order_price,
       o.created_at IS NOT NULL AS created_at_set,
       o.modified_at IS NOT NULL AS modified_at_set
FROM orders o JOIN users u ON u.user_id = o.orderer_id
WHERE left(u.login_id, length(:'run_id') + 1) = :'run_id' || '_'
ORDER BY o.order_id;

SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND ((table_name = 'users' AND column_name = 'user_type')
    OR (table_name = 'orders' AND column_name = 'order_status'))
ORDER BY table_name, column_name;

SELECT to_regclass('public.payments') IS NOT NULL AS payments_table_exists;

COMMIT;
