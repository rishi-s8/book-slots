-- MySQL dump 10.13  Distrib 8.0.22, for Linux (x86_64)
--
-- Host: localhost    Database: c4dfedBooking
-- ------------------------------------------------------
-- Server version	8.0.22-0ubuntu0.20.04.2

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
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Equipments`
--

LOCK TABLES `Equipments` WRITE;
/*!40000 ALTER TABLE `Equipments` DISABLE KEYS */;
INSERT INTO `Equipments` VALUES (1,'Helium IonBeam Lithography','Carl Zeiss Microscope','ORION Nano Fab','for fabricating new semiconductor devices'),(2,'Electron Beam Lithography','Raith','eLine Plus','to  pattern the substrate'),(3,'FESEM (Field Emission Scanning Electron Microscope)','Carl Zeiss Microscope','GeminiSEM 500','to provide topographical and elemental information at high magnifications'),(4,'Mask Aligner: Lithography',' EV group','EVG610','for mask dependent lithography'),(5,'AFM (Atomic Force Microscopy)','Bruker','Dimension ICON PT',' to analyse the surface properties of thin films'),(6,'Ellipsometry','Accurion','EP4','for extraction of the dielectric properties'),(7,'Maskless Lithography','Intelligent Micro Patterning','SF - 100 Xpress Maskless Exposure','for pattering for device fabrication using CAD based Mask'),(8,'Reactive Ion Etching','PLANAR tech.','PlanarRIE-6s','for dry etching using reactive gas discharge'),(9,'Multi Chamber Sputtering System','Advanced Process Technology','Self Assembled','for the solid-state thin film deposition for device fabrication'),(10,'Optical Profilometer','Bruker','CONTOURGT-K Automated System','to get surface morphology, step heights and surface roughness'),(11,'Thermal Evaporator','Hind High Vacuum','BC -300','for physical vapour deposition of the material'),(12,'Glove Box','SciLab - Vigro Gas Purification tech','SGI 200/750TS','for the synthesis of the device'),(13,'Contact Angle','SEO (Surface Electro Optics) Phoenix 300','SEO Phoenix 300','to verify whether the substrate is hydrophobic or hydrophilic'),(14,'Electrochemical Analyzer','CH instrument','(CHI604E)','for the measurement of potential, charge, or current'),(15,'Optical Microscope','Olympus','BX-51 TRF','for temperature dependent analysis'),(16,'Electrical Characterization System','Tektronics.','Keithley 4200 SCS','for electrical characterisation of the devices'),(17,'3D Printer','General Laboratory equipment','XYZ Printing PRO','joins or solidifies polymer under computer control'),(18,'Stylus Profilometer','AEP Technology','Nano Map-LS','to get surface morphology'),(19,'Spin Coater','Laurell International','WS-650MZ-23NPP','for the thin film deposition'),(20,'3 Zone Furnace','Thermo scientific','Lindberg Blue M','for the oxidation and annealing of the devices');
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Manvi','Manvi_Gupta','Institute','$5$rounds=535000$TFFaIWG/CpVBkyi0$DFlja.gyWbvraJJ22O81qKsD2dS1E1CkYoeAfVqxSt/'),(3,'Manvi','b17092@students.iitmandi.ac.in','Institute','$5$rounds=535000$HORNwAiYtguwwuO5$2.dvYd/1KkAi/1G6nzGtlkZ8/.rhRdGXPSJ.slZaUB1');
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

-- Dump completed on 2020-11-06 19:16:56
