-- phpMyAdmin SQL Dump
-- version 4.7.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Dec 01, 2017 at 09:22 PM
-- Server version: 10.1.26-MariaDB
-- PHP Version: 7.1.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `KSL_WebScraper`
--

-- --------------------------------------------------------

--
-- Table structure for table `Cars`
--

CREATE TABLE `Cars` (
  `id` varchar(36) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `ad_identifier` int(10) UNSIGNED NOT NULL,
  `title` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `mileage` mediumint(6) UNSIGNED DEFAULT NULL,
  `year` smallint(4) UNSIGNED DEFAULT NULL,
  `make` tinyint(3) UNSIGNED DEFAULT NULL,
  `model` varchar(15) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `trim` varchar(15) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `body` varchar(15) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `vin` varchar(17) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `title_type` tinyint(1) DEFAULT NULL,
  `transmission` tinyint(1) DEFAULT NULL,
  `exterior_color` tinyint(2) DEFAULT NULL,
  `interior_color` tinyint(2) DEFAULT NULL,
  `liters` varchar(5) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `fuel_type` tinyint(2) DEFAULT NULL,
  `exterior_condition` tinyint(1) DEFAULT NULL,
  `interior_condition` tinyint(1) DEFAULT NULL,
  `drive_type` tinyint(1) DEFAULT NULL,
  `make_label` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `cylinders` varchar(4) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `popularity` tinyint(3) UNSIGNED NOT NULL DEFAULT '0',
  `longevity` tinyint(3) UNSIGNED NOT NULL DEFAULT '11',
  `make_reliability` tinyint(3) NOT NULL DEFAULT '50',
  `bad_model` bit(1) NOT NULL DEFAULT b'0',
  `value_accuracy` tinyint(3) DEFAULT NULL,
  `value` mediumint(6) NOT NULL,
  `price` mediumint(6) NOT NULL,
  `date_posted` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


--
-- Indexes for table `Cars`
--
ALTER TABLE `Cars`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `id` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
