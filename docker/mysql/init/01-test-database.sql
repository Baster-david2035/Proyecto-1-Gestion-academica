CREATE DATABASE IF NOT EXISTS test_gestion_academica CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON test_gestion_academica.* TO 'academico'@'%';
GRANT CREATE, DROP ON *.* TO 'academico'@'%';
