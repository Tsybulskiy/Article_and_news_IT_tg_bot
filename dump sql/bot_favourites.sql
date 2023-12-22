-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: bot
-- ------------------------------------------------------
-- Server version	8.0.32

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `favourites`
--

DROP TABLE IF EXISTS `favourites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `favourites` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `FavouriteLink` text,
  `FavouriteCategory` text,
  `UserId` bigint DEFAULT NULL,
  `SiteId` int DEFAULT NULL,
  `Title` longtext,
  PRIMARY KEY (`Id`),
  KEY `SiteId` (`SiteId`),
  KEY `UserId` (`UserId`),
  CONSTRAINT `favourites_ibfk_1` FOREIGN KEY (`SiteId`) REFERENCES `sites` (`Id`),
  CONSTRAINT `favourites_ibfk_2` FOREIGN KEY (`SiteId`) REFERENCES `sites` (`Id`),
  CONSTRAINT `favourites_ibfk_3` FOREIGN KEY (`UserId`) REFERENCES `users` (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `favourites`
--

LOCK TABLES `favourites` WRITE;
/*!40000 ALTER TABLE `favourites` DISABLE KEYS */;
INSERT INTO `favourites` VALUES (45,NULL,'DLP',967275153,NULL,NULL),(46,'https://www.itsec.ru/articles/novoe-vremya-diktuet-otkaz-ot-staryh-predstavlenij-o-dlp-sistemah-i-zashchite-ot-utechek-informacii',NULL,967275153,3,'Новое время диктует отказ от старых представлений о DLP-системах и защите от утечек информации'),(47,NULL,NULL,853060527,NULL,NULL),(48,NULL,NULL,777273030,NULL,NULL),(49,NULL,NULL,777273030,NULL,NULL),(50,NULL,NULL,777273030,NULL,NULL),(51,NULL,'UEBA',853060527,NULL,NULL),(52,NULL,NULL,6014347389,NULL,NULL),(53,NULL,NULL,6014347389,NULL,NULL),(54,'https://www.secuteck.ru/articles/iskusstvennyj-intellekt-i-videoanalitika-v-multirubezhnyh-perimetrah-zashchity',NULL,6014347389,5,'Искусственный интеллект и видеоаналитика в мультирубежных периметрах защиты'),(55,NULL,NULL,6014347389,NULL,NULL),(56,NULL,NULL,6014347389,NULL,NULL),(57,NULL,NULL,853060527,NULL,NULL);
/*!40000 ALTER TABLE `favourites` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `favorites_siteid` BEFORE UPDATE ON `favourites` FOR EACH ROW SET NEW.siteid = (

SELECT id
  FROM sites
  WHERE NEW.Favouritelink LIKE CONCAT(sites.sitename, '%')
) */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-12-23  2:40:34
