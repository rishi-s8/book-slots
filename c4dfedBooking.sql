-- MySQL dump 10.13  Distrib 8.0.22, for Linux (x86_64)
--
-- Host: localhost    Database: c4dfedBooking
-- ------------------------------------------------------
-- Server version	8.0.22

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Bookings`
--

DROP TABLE IF EXISTS `Bookings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Bookings` (
  `UserId` int NOT NULL,
  `EquipID` int NOT NULL,
  `fromDateTime` datetime NOT NULL,
  `toDateTime` datetime NOT NULL,
  `RequestStatus` enum('Awaited','Accepted','Rescheduled','Rejected') NOT NULL,
  `SName` varchar(120) NOT NULL,
  `SEmail` varchar(500) NOT NULL,
  `BookingID` int unsigned NOT NULL AUTO_INCREMENT,
  `Payment` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`BookingID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Bookings`
--

LOCK TABLES `Bookings` WRITE;
/*!40000 ALTER TABLE `Bookings` DISABLE KEYS */;
INSERT INTO `Bookings` VALUES (1,7,'2012-06-18 10:34:09','2012-06-18 10:34:12','Awaited','superviser','email',1,1),(7,1,'2020-11-13 22:00:00','2020-11-13 23:03:00','Awaited','Rishi','b17138@students.iitmandi.ac.in',2,0),(1,1,'2020-11-09 10:36:00','2020-11-09 15:30:00','Awaited','newUser','newUser@email.com',3,0);
/*!40000 ALTER TABLE `Bookings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Equipments`
--

DROP TABLE IF EXISTS `Equipments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Equipments` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(500) NOT NULL,
  `Company` varchar(500) DEFAULT NULL,
  `Model` varchar(500) DEFAULT NULL,
  `Purpose` varchar(1000) DEFAULT NULL,
  `CostOther` float DEFAULT NULL,
  `CostInstitute` float DEFAULT NULL,
  `CostAcademic` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Equipments`
--

LOCK TABLES `Equipments` WRITE;
/*!40000 ALTER TABLE `Equipments` DISABLE KEYS */;
INSERT INTO `Equipments` VALUES (1,'Helium IonBeam Lithography','Carl Zeiss Microscope','ORION Nano Fab','For fabricating new semiconductor devices',10000,2000,5000),(2,'Electron Beam Lithography(Exposure only)','Raith','eLine Plus','To  pattern the substrate',5000,1000,2500),(3,'FESEM (Field Emission Scanning Electron Microscope)','Carl Zeiss Microscope','GeminiSEM 500','To provide Topographical and Elemental information at high magnifications',3750,750,1875),(4,'Mask Aligner: Optical Lithography',' EV group','EVG610','For mask dependent Lithography',1250,250,625),(5,'AFM (Atomic Force Microscopy)','Bruker','Dimension ICON PT',' To analyse the surface properties of thin films',2500,500,1250),(6,'Ellipsometer(Modeling and Analysis)','Accurion','EP4','For extraction of Dielectric properties',12500,2500,6250),(7,'Maskless Lithography','Intelligent Micro Patterning','SF - 100 Xpress Maskless Exposure','For patterning in device fabrication using CAD based Mask',1000,200,500),(8,'Reactive Ion Etching','PLANAR tech.','PlanarRIE-6s','For dry etching using reactive gas discharge',1500,300,750),(9,'Multi Chamber Sputtering System','Advanced Process Technology','Self Assembled','For solid-state thin film deposition for Device Fabrication',2000,400,1000),(10,'Optical Profilometer','Bruker','CONTOURGT-K Automated System','To get surface morphology, step heights and surface roughness',750,150,375),(11,'Thermal Evaporator','Hind High Vacuum','BC -300','For physical vapour deposition of the material',1500,300,750),(12,'Glove Box','SciLab - Vigro Gas Purification tech','SGI 200/750TS','For the synthesis of the device',750,150,375),(13,'Contact Angle','SEO (Surface Electro Optics) Phoenix 300','SEO Phoenix 300','To verify whether the substrate is hydrophobic or hydrophilic',400,100,125),(14,'Electrochemical Analyzer','CH instrument','(CHI604E)','For the measurement of potential, charge, or current',500,100,250),(15,'Optical Microscope','Olympus','BX-51 TRF','For temperature dependent analysis',500,100,250),(16,'Electrical Characterization System','Tektronics.','Keithley 4200 SCS','For electrical characterisation of the devices',500,100,250),(17,'3D Printer','General Laboratory equipment','XYZ Printing PRO','Joins or solidifies polymer under computer control',500,100,250),(18,'Stylis Profiler','AEP Technology','Nano Map-LS','To get surface morphology',500,100,250),(19,'Spin Coater','Laurell International','WS-650MZ-23NPP','For thin film deposition',600,75,200),(20,'3 Zone Furnace','Thermo scientific','Lindberg Blue M','For the oxidation and annealing of the devices',500,100,250),(21,'Elipsometer(Data Acquisition)',NULL,'Accurion',NULL,2500,1250,500),(22,'Optical Lithography',NULL,'EV Group',NULL,1250,625,250),(23,'E-spin',NULL,'E-Spin nanotech',NULL,500,250,100),(24,'Spin Coater(In air)',NULL,'Spectro Spin',NULL,250,125,50),(25,'Vacuum Oven',NULL,'Nanosemi Technology',NULL,500,250,100),(26,'DI water',NULL,'Millipore',NULL,250,125,50),(27,'Clean Lab Space(5\'x5\')',NULL,'-',NULL,10000,5000,2000);
/*!40000 ALTER TABLE `Equipments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `UserId` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `username` varchar(500) NOT NULL,
  `accountType` varchar(500) NOT NULL,
  `password` varchar(500) NOT NULL,
  PRIMARY KEY (`UserId`),
  UNIQUE KEY `unique_email` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Manvi','Manvi_Gupta','Institute','$5$rounds=535000$TFFaIWG/CpVBkyi0$DFlja.gyWbvraJJ22O81qKsD2dS1E1CkYoeAfVqxSt/'),(3,'Manvi','b17092@students.iitmandi.ac.in','Institute','$5$rounds=535000$HORNwAiYtguwwuO5$2.dvYd/1KkAi/1G6nzGtlkZ8/.rhRdGXPSJ.slZaUB1'),(5,'TestUser','mail','Other','$5$rounds=535000$W/eICHAB4kIRTesu$z0jut0uRw2GoluxSeNpf4bLyTPGQeGos262Xb.wutB8'),(6,'BookUser','user@email.com','Academic','$5$rounds=535000$IqbGJ59bdD/lHoqm$/1c7HnR6AO17j5mLgi5V1YUt.qghH4M1SbyX3pvuPY4'),(7,'Rishi Sharma','b17138@students.iitmandi.ac.in','Institute','$5$rounds=535000$6wmXLHn6/0BN6kMp$jRioU7JX1BcAh9d2mdc6DLvlJhtB8ljzFGsgeVn39l4'),(8,'Administrator','admin@c4dfed.com','admin','$5$rounds=535000$nOgt8/gavSReSrFM$Xb9zZi5NEUIo8UFzydA6Vk492DT87olnDeRdOwOVks3');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-11-24 17:09:55
