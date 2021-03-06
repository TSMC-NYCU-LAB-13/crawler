# Crawler

[![Build Workflow](https://github.com/TSMC-NYCU-LAB-13/crawler/actions/workflows/build.yml/badge.svg?event=push)](https://github.com/TSMC-NYCU-LAB-13/crawler/actions/workflows/build.yml)
[![Docker Repository on Quay](https://quay.io/repository/tsmc-nycu-lab-13/crawler/status "Docker Repository on Quay")](https://quay.io/repository/tsmc-nycu-lab-13/crawler)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=TSMC-NYCU-LAB-13_crawler&metric=bugs)](https://sonarcloud.io/summary/new_code?id=TSMC-NYCU-LAB-13_crawler)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=TSMC-NYCU-LAB-13_crawler&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=TSMC-NYCU-LAB-13_crawler)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=TSMC-NYCU-LAB-13_crawler&metric=coverage)](https://sonarcloud.io/summary/new_code?id=TSMC-NYCU-LAB-13_crawler)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=TSMC-NYCU-LAB-13_crawler&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=TSMC-NYCU-LAB-13_crawler)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=TSMC-NYCU-LAB-13_crawler&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=TSMC-NYCU-LAB-13_crawler)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=TSMC-NYCU-LAB-13_crawler&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=TSMC-NYCU-LAB-13_crawler)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=TSMC-NYCU-LAB-13_crawler&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=TSMC-NYCU-LAB-13_crawler)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=TSMC-NYCU-LAB-13_crawler&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=TSMC-NYCU-LAB-13_crawler)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=TSMC-NYCU-LAB-13_crawler&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=TSMC-NYCU-LAB-13_crawler)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=TSMC-NYCU-LAB-13_crawler&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=TSMC-NYCU-LAB-13_crawler)

> Google news crawler (last-7-day news) on keyword, ??????

## Main function
```bash
# crawler
python crawler.py

# test
python -m unittest -v test_crawler.py
# test per function
python -m unittest -v test_crawler.TestCrawler.test_html_getText
```

## Build environment
- Run containers: mariadb && crawler
- Prepare database
- Perform main function
### Run containers: mariadb && crawler
```bash
# create and customise the local env file
cp .env.example .env

# create docker network for crawler to connect mariadb
docker network create cloud_native_final

# build crawler image
docker build -t cloud_native_crawler .

# run mariadb (root/P@55w0Rd)
docker run -dit --env MARIADB_ROOT_PASSWORD=P@55w0Rd --network cloud_native_final --name mariadb bitnami/mariadb

# run crawler
docker run -dit --network cloud_native_final --name cloud_native_crawler cloud_native_crawler
```

### Prepare database
#### Go to mariadb container
```bash
docker exec -it mariadb bash
```
#### login to mariadb
```bash
# in mariadb container
mysql -u root -p
# // type root password on prompt
```
#### create database and table
```bash
# in mariadb daemon
# create database and go into it
CREATE DATABASE crawler;
USE crawler;

# create table (spec from backend)
SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';
SET NAMES utf8mb4;
DROP TABLE IF EXISTS `articles`;
CREATE TABLE `articles` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `title` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `url` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `time` datetime NOT NULL,
  `keyword` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `emotional_value` double DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `url_unique` (`url`) USING HASH,
  KEY `keyword_index` (`keyword`(768))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

# perhaps need to delete table
DROP TABLE articles;
```

### Perform main function
#### Go to crawler container
```bash
docker exec -it cloud_native_crawler bash
```
#### Run command
```bash
# in cloud_native_crawler container
# crawler
python crawler.py

# test
python -m unittest -v test_crawler.py
```
