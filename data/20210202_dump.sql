-- MySQL dump 10.18  Distrib 10.3.27-MariaDB, for debian-linux-gnueabihf (armv8l)
--
-- Host: localhost    Database: ELECTINEOS
-- ------------------------------------------------------
-- Server version	10.3.27-MariaDB-0+deb10u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `devices`
--

DROP TABLE IF EXISTS `devices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `devices` (
  `id` tinyint(4) NOT NULL AUTO_INCREMENT,
  `alias` varchar(255) DEFAULT NULL,
  `model` varchar(50) DEFAULT NULL,
  `host` varchar(100) DEFAULT NULL,
  `hardware` varchar(50) DEFAULT NULL,
  `mac` varchar(50) DEFAULT NULL,
  `led_state` varchar(25) DEFAULT NULL,
  `led_state_since` timestamp NULL DEFAULT NULL,
  `plug` varchar(10) DEFAULT NULL,
  `statut` varchar(50) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=29 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devices`
--

LOCK TABLES `devices` WRITE;
/*!40000 ALTER TABLE `devices` DISABLE KEYS */;
INSERT INTO `devices` VALUES (2,'Prise_zehcnas','HS110(FR)','192.168.1.3','4.0','1C:3B:F3:8D:27:C2','True',NULL,'on','1','2020-12-12 10:09:24','2021-02-02 19:49:36'),(28,'Prise connecte CDS','HS110(FR)','172.16.130.216','4.0','CC:32:E5:B7:8E:4A','True',NULL,'off','2','2021-01-19 15:35:55','2021-02-02 17:46:26');
/*!40000 ALTER TABLE `devices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `schedules`
--

DROP TABLE IF EXISTS `schedules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `schedules` (
  `id` tinyint(4) NOT NULL AUTO_INCREMENT,
  `device` tinyint(4) DEFAULT 0,
  `actionScheduling` tinyint(1) DEFAULT 0,
  `timeScheduling` time DEFAULT NULL,
  `monday` tinyint(1) DEFAULT 0,
  `tuesday` tinyint(1) DEFAULT 0,
  `wednesday` tinyint(1) DEFAULT 0,
  `thursday` tinyint(1) DEFAULT 0,
  `friday` tinyint(1) DEFAULT 0,
  `saturday` tinyint(1) DEFAULT 0,
  `sunday` tinyint(1) DEFAULT 0,
  `isActive` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `fk_id_device` (`device`)
) ENGINE=MyISAM AUTO_INCREMENT=42 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schedules`
--

LOCK TABLES `schedules` WRITE;
/*!40000 ALTER TABLE `schedules` DISABLE KEYS */;
/*!40000 ALTER TABLE `schedules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `statements`
--

DROP TABLE IF EXISTS `statements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `statements` (
  `id` tinyint(4) NOT NULL AUTO_INCREMENT,
  `host` varchar(100) DEFAULT NULL,
  `statement_date` timestamp NULL DEFAULT NULL,
  `emeter_current` float DEFAULT NULL,
  `emeter_voltage` float DEFAULT NULL,
  `emeter_power` float DEFAULT NULL,
  `emeter_total_concumption` float DEFAULT NULL,
  `emeter_today` float DEFAULT NULL,
  `emeter_month` float DEFAULT NULL,
  `device` tinyint(4) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `fk_id_device` (`host`)
) ENGINE=MyISAM AUTO_INCREMENT=66 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `statements`
--

LOCK TABLES `statements` WRITE;
/*!40000 ALTER TABLE `statements` DISABLE KEYS */;
INSERT INTO `statements` VALUES (15,'192.168.1.3','2020-12-17 12:17:04',0.035,230.066,2.488,0.421,0.002,0.421,2),(16,'192.168.1.3','2020-12-17 18:00:04',0.011,230.231,0,0.427,0.008,0.427,2),(17,'192.168.1.3','2020-12-18 18:00:03',0.011,233.974,0,0.427,0,0.427,2),(18,'192.168.1.3','2020-12-19 18:00:03',0.011,232.736,0,0.46,0.001,0.46,2),(19,'192.168.1.3','2020-12-20 18:00:03',0.011,236.056,0,0.46,0,0.46,2),(20,'192.168.1.3','2020-12-21 18:00:04',0.065,229.654,6.481,0.48,0.02,0.48,2),(37,'192.168.1.3','2021-01-05 18:00:03',0.051,229.74,5.514,1.065,0.026,0.226,2),(25,'192.168.1.3','2020-12-22 18:00:04',0.034,234.297,2.576,0.524,0.022,0.524,2),(26,'192.168.1.3','2020-12-23 18:00:03',0.011,234.017,0,0.558,0,0.558,2),(27,'192.168.1.3','2020-12-24 18:00:04',0.034,231.557,2.793,0.569,0.011,0.569,2),(28,'192.168.1.3','2020-12-25 18:00:04',0.011,234.719,0,0.585,0.002,0.585,2),(29,'192.168.1.3','2020-12-26 18:00:04',0.062,232.666,5.626,0.591,0.006,0.591,2),(30,'192.168.1.3','2020-12-27 18:00:03',0.033,229.908,1.691,0.642,0.016,0.642,2),(31,'192.168.1.3','2020-12-28 18:00:03',0.011,233.793,0,0.658,0.003,0.658,2),(32,'192.168.1.3','2020-12-29 18:00:03',0.034,230.36,1.41,0.807,0.149,0.807,2),(33,'192.168.1.3','2020-12-30 18:00:03',0.011,229.927,0,0.821,0.004,0.821,2),(34,'192.168.1.3','2020-12-31 18:00:03',0.011,231.631,0,0.839,0,0.839,2),(35,'192.168.1.3','2021-01-03 18:00:05',0.049,231.802,5.508,0.996,0.106,0.157,2),(36,'192.168.1.3','2021-01-04 18:00:03',0.034,234.115,1.337,1.016,0.059,0.177,2),(38,'192.168.1.3','2021-01-06 18:00:03',0.011,233.086,0,1.097,0.061,0.258,2),(39,'192.168.1.3','2021-01-07 18:00:03',0.011,234.482,0,1.097,0.006,0.258,2),(40,'192.168.1.3','2021-01-09 18:00:06',0.06,232.169,5.351,1.117,0.02,0.278,2),(41,'192.168.1.3','2021-01-10 18:00:05',0.031,231.089,1.388,1.164,0.019,0.325,2),(42,'192.168.1.3','2021-01-11 18:00:06',0.011,232.536,0,1.19,0.001,0.351,2),(43,'192.168.1.3','2021-01-12 18:00:05',0.011,228.857,0,1.19,0,0.351,2),(44,'192.168.1.3','2021-01-13 18:00:05',0.061,235.724,5.421,1.205,0.007,0.366,2),(45,'192.168.1.3','2021-01-14 18:00:06',0.052,235.735,5.633,1.258,0.032,0.419,2),(46,'192.168.1.3','2021-01-15 18:00:07',0.031,229.96,1.438,1.305,0.027,0.466,2),(47,'192.168.1.3','2021-01-16 18:00:05',0.011,234.234,0,1.34,0.002,0.501,2),(48,'192.168.1.3','2021-01-17 18:00:05',0.031,235.227,1.377,1.348,0.007,0.51,2),(49,'192.168.1.3','2021-01-18 18:00:06',0.011,230.649,0,1.361,0.002,0.522,2),(50,'192.168.1.3','2021-01-19 18:00:06',0.011,233.322,0,1.386,0.009,0.547,2),(51,'192.168.1.3','2021-01-20 18:00:05',0.011,234.214,0,1.386,0,0.547,2),(52,'192.168.1.3','2021-01-21 18:00:06',0.011,236.581,0,1.386,0,0.547,2),(53,'192.168.1.3','2021-01-22 18:00:06',0.011,234.125,0,1.416,0.03,0.577,2),(54,'192.168.1.3','2021-01-24 18:00:06',0.011,236.754,0,1.433,0.015,0.594,2),(55,'192.168.1.3','2021-01-25 16:55:57',0.061,236.206,5.477,1.448,0.017,0.609,0),(56,'192.168.1.3','2021-01-25 16:57:45',0.058,234.141,5.378,1.448,0.017,0.609,2),(57,'192.168.1.3','2021-01-25 18:00:06',0.031,233.544,1.391,1.452,0.021,0.613,2),(58,'192.168.1.3','2021-01-26 18:00:05',0.011,229.455,0,1.466,0.002,0.627,2),(59,'192.168.1.3','2021-01-27 18:00:06',0.011,232.055,0,1.466,0,0.627,2),(60,'192.168.1.3','2021-01-28 18:00:06',0.011,232.61,0,1.499,0.02,0.66,2),(61,'192.168.1.3','2021-01-29 18:00:05',0.031,230.328,1.42,1.537,0.02,0.698,2),(62,'192.168.1.3','2021-01-30 18:00:05',0.031,232.582,1.362,1.575,0.017,0.736,2),(63,'192.168.1.3','2021-01-31 18:00:06',0.031,233.309,1.302,1.603,0.011,0.764,2),(64,'192.168.1.3','2021-02-01 18:00:06',0.059,228.683,5.274,1.639,0.027,0.027,2),(65,'192.168.1.3','2021-02-02 18:00:06',0.031,236.759,1.471,1.674,0.025,0.062,2);
/*!40000 ALTER TABLE `statements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `status`
--

DROP TABLE IF EXISTS `status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `status` (
  `id` tinyint(4) NOT NULL AUTO_INCREMENT,
  `status` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `status`
--

LOCK TABLES `status` WRITE;
/*!40000 ALTER TABLE `status` DISABLE KEYS */;
INSERT INTO `status` VALUES (1,'Equipement disponible'),(2,'Equipement indisponible');
/*!40000 ALTER TABLE `status` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-02-02 19:56:36
