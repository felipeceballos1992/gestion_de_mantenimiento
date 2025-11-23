USE gestion_mtto;
-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: gestion_mtto
-- ------------------------------------------------------
-- Server version	8.0.44

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
-- Table structure for table `cronograma`
--

DROP TABLE IF EXISTS `cronograma`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cronograma` (
  `id` int NOT NULL AUTO_INCREMENT,
  `equipo_id` int NOT NULL,
  `tipo` varchar(50) NOT NULL,
  `subcategoria` varchar(100) DEFAULT NULL,
  `frecuencia` int DEFAULT NULL,
  `ultimo_mtto` date DEFAULT NULL,
  `proximo_mtto` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `equipo_id` (`equipo_id`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cronograma`
--

INSERT INTO `cronograma` VALUES (1,1,'preventivo','Revisión de válvulas y conexiones de gas',15,'2025-11-21','2025-12-06'),(2,1,'preventivo','Limpieza y verificación de estructura',30,'2025-11-21','2025-12-21'),(3,1,'preventivo','Mantenimiento general y pintura',365,'2024-11-10','2025-11-10'),(4,2,'preventivo','Revisión de válvulas y conexiones de gas',15,'2025-10-25','2025-11-09'),(5,2,'preventivo','Limpieza y verificación de estructura',30,'2025-10-20','2025-11-19'),(6,2,'preventivo','Mantenimiento general y pintura',365,'2024-11-15','2025-11-15'),(7,3,'preventivo','Revisión de válvulas y conexiones de gas',15,'2025-11-21','2025-12-06'),(8,3,'preventivo','Limpieza y verificación de estructura',30,'2025-10-17','2025-11-16'),(9,3,'preventivo','Mantenimiento general y pintura',365,'2024-11-12','2025-11-12'),(10,4,'preventivo','Revisión de válvulas y conexiones de gas',15,'2025-10-27','2025-11-11'),(11,4,'preventivo','Limpieza y verificación de estructura',30,'2025-10-22','2025-11-21'),(12,4,'preventivo','Mantenimiento general y pintura',365,'2024-11-17','2025-11-17'),(13,7,'preventivo','Cambio de cerámicas de lámparas de calor',90,'2025-08-15','2025-11-15'),(14,7,'preventivo','Ajuste de tornillería general',15,'2025-10-28','2025-11-12'),(15,7,'preventivo','Mantenimiento de variadores de velocidad',30,'2025-10-20','2025-11-19'),(16,7,'preventivo','Revisión de banda transportadora',30,'2025-10-15','2025-11-14'),(17,7,'preventivo','Aplicación de pintura y protección',365,'2024-11-20','2025-11-20'),(18,5,'preventivo','Lubricación de rodamientos y ejes',15,'2025-10-26','2025-11-10'),(19,5,'preventivo','Revisión de motor y conexiones',30,'2025-10-17','2025-11-16'),(20,5,'preventivo','Ajuste de tornillería general',30,'2025-10-18','2025-11-17'),(21,5,'preventivo','Mantenimiento general y pintura',365,'2024-11-22','2025-11-22'),(22,6,'preventivo','Ajuste de rodillos y mecanismos',15,'2025-10-27','2025-11-11'),(23,6,'preventivo','Lubricación de poleas y ejes',30,'2025-11-21','2025-12-21'),(24,6,'preventivo','Verificación de motores y variadores',30,'2025-10-16','2025-11-15'),(25,6,'preventivo','Mantenimiento general y pintura',365,'2024-11-18','2025-11-18'),(26,8,'preventivo','Lubricación de rodamientos y ejes',30,'2025-10-21','2025-11-20'),(27,8,'preventivo','Verificación de motores de transmisión',60,'2025-11-21','2026-01-20'),(28,8,'preventivo','Limpieza profunda y mantenimiento',90,'2025-08-25','2025-11-23'),(29,9,'preventivo','Lubricación de mecanismos de corte',15,'2025-10-29','2025-11-13'),(30,9,'preventivo','Verificación de sensores y conexiones',30,'2025-10-22','2025-11-21'),(31,10,'preventivo','Lubricación de mecanismos de corte',15,'2025-10-30','2025-11-14'),(32,10,'preventivo','Verificación de sensores y conexiones',30,'2025-10-23','2025-11-22'),(33,11,'preventivo','Limpieza de cabezal de impresión',7,'2025-11-21','2025-11-28'),(34,11,'preventivo','Verificación de sistema de calentamiento',30,'2025-11-21','2025-12-21'),(35,11,'preventivo','Ajuste de mecanismo de transporte',30,'2025-10-16','2025-11-15'),(36,12,'preventivo','Calibración y verificación de precisión',30,'2025-10-21','2025-11-20'),(37,13,'preventivo','Calibración y verificación de impresora',30,'2025-10-14','2025-11-13'),(38,14,'preventivo','Calibración y verificación de precisión',30,'2025-10-17','2025-11-16'),(39,15,'preventivo','Calibración y verificación de precisión',30,'2025-10-19','2025-11-18'),(40,16,'preventivo','Limpieza de aspas y rejillas',15,'2025-11-21','2025-12-06'),(41,16,'preventivo','Lubricación de rodamientos',180,'2025-11-21','2026-05-20'),(42,16,'preventivo','Verificación de motor y conexiones',90,'2025-08-25','2025-11-23'),(43,17,'preventivo','Limpieza de filtros y ductos',30,'2025-11-21','2025-12-21'),(44,17,'preventivo','Verificación de ventiladores y motores',90,'2025-08-26','2025-11-24'),(45,17,'preventivo','Mantenimiento completo del sistema',365,'2024-11-28','2025-11-28'),(46,18,'preventivo','Limpieza interior y exterior',15,'2025-11-01','2025-11-16'),(47,18,'preventivo','Verificación de sistema de refrigeración',30,'2025-10-19','2025-11-18'),(48,18,'preventivo','Revisión de sellos y bisagras',90,'2025-08-29','2025-11-27'),(49,18,'preventivo','Mantenimiento preventivo completo',180,'2025-05-25','2025-11-21'),(50,19,'preventivo','Cambio de aceite',30,'2025-11-21','2025-12-21'),(51,19,'preventivo','fsdsdfasf',2,'2025-11-21','2025-11-23'),(52,3,'preventivo','nkjn',1,NULL,'2025-11-22'),(53,15,'preventivo','jklkññklh',1,NULL,'2025-11-22'),(54,4,'preventivo','fdaasfgfsd',1,NULL,'2025-11-22');

--
-- Table structure for table `equipos`
--

DROP TABLE IF EXISTS `equipos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `fabricante` varchar(255) DEFAULT NULL,
  `contacto_fabricante` text,
  `ubicacion` varchar(255) DEFAULT NULL,
  `fecha_compra` date DEFAULT NULL,
  `estado` varchar(50) DEFAULT 'activo',
  `potencia` varchar(100) DEFAULT NULL,
  `voltaje` varchar(100) DEFAULT NULL,
  `tipo_alimentacion` varchar(50) DEFAULT NULL,
  `potencia_motor` varchar(100) DEFAULT NULL,
  `relacion_motoreductor` varchar(100) DEFAULT NULL,
  `diametro_polea` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipos`
--

INSERT INTO `equipos` VALUES (1,'Marmita 1','Fabricante Marmitas',NULL,'Área de cocción',NULL,'activo',NULL,NULL,'Gas',NULL,NULL,NULL),(2,'Marmita 2','Fabricante Marmitas',NULL,'Área de cocción',NULL,'activo',NULL,NULL,'Gas',NULL,NULL,NULL),(3,'Marmita 3','Fabricante Marmitas',NULL,'Área de cocción',NULL,'activo',NULL,NULL,'Gas',NULL,NULL,NULL),(4,'Marmita 4','Fabricante Marmitas',NULL,'Área de cocción',NULL,'activo',NULL,NULL,'Gas',NULL,NULL,NULL),(5,'Molino','Fabricante Molinos',NULL,'Área de molienda',NULL,'activo',NULL,NULL,'Energía eléctrica',NULL,NULL,NULL),(6,'Laminadora','Fabricante Laminadoras',NULL,'Área de formado',NULL,'activo',NULL,NULL,'Energía eléctrica',NULL,NULL,NULL),(7,'Horno','Fabricante Hornos',NULL,'Área de horneado',NULL,'activo',NULL,NULL,'Gas y energía eléctrica',NULL,NULL,NULL),(8,'Zona fría','Fabricante Sistemas',NULL,'Área de enfriamiento',NULL,'activo',NULL,NULL,'Energía eléctrica',NULL,NULL,NULL),(9,'Atadora 1','Fabricante Atadoras',NULL,'Área de empaque',NULL,'activo',NULL,NULL,'Energía eléctrica',NULL,NULL,NULL),(10,'Atadora 2','Fabricante Atadoras',NULL,'Área de empaque',NULL,'activo',NULL,NULL,'Energía eléctrica',NULL,NULL,NULL),(11,'Fechadora','Fabricante Fechadoras',NULL,'Área de empaque',NULL,'activo',NULL,NULL,'Energía eléctrica',NULL,NULL,NULL),(12,'Báscula de piso','Fabricante Básculas',NULL,'Recepción materia prima',NULL,'activo',NULL,NULL,'Energía eléctrica',NULL,NULL,NULL),(13,'Báscula con impresora','Fabricante Básculas',NULL,'Área de preparación',NULL,'activo',NULL,NULL,'Energía eléctrica',NULL,NULL,NULL),(14,'Báscula sencilla 1','Fabricante Básculas',NULL,'Área de laminación',NULL,'activo',NULL,NULL,'Energía eléctrica',NULL,NULL,NULL),(15,'Báscula sencilla 2','Fabricante Básculas',NULL,'Área de empaque',NULL,'activo',NULL,NULL,'Energía eléctrica',NULL,NULL,NULL),(16,'Ventiladores','Fabricante Ventilación',NULL,'Zona fría',NULL,'activo',NULL,NULL,'Energía eléctrica',NULL,NULL,NULL),(17,'Sistema de extracción e inyección de aire','Fabricante Ventilación',NULL,'Área de producción',NULL,'activo',NULL,NULL,'Energía eléctrica',NULL,NULL,NULL),(18,'Cuarto frío','Fabricante Refrigeración',NULL,'Almacenamiento',NULL,'activo',NULL,NULL,'Energía eléctrica',NULL,NULL,NULL),(19,'Equipo de prueba','YO','Desarrollador de apps','Mi ppc','2025-11-21','activo','','','','','',''),(21,'jkljñlkjñlk','kljñlkjñl','lñkjñlkjñlj','jñljñlkjñl','2025-11-21','activo','','','','','','');

--
-- Table structure for table `fotos_mantenimiento`
--

DROP TABLE IF EXISTS `fotos_mantenimiento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fotos_mantenimiento` (
  `id` int NOT NULL AUTO_INCREMENT,
  `mantenimiento_id` int NOT NULL,
  `ruta_archivo` varchar(500) NOT NULL,
  `tipo` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `mantenimiento_id` (`mantenimiento_id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fotos_mantenimiento`
--

INSERT INTO `fotos_mantenimiento` VALUES (1,2,'2_antes_20251121_091436.jpg','antes'),(2,2,'2_despues_20251121_091436.jpg','despues'),(3,3,'3_antes_20251121_091841.jpg','antes'),(4,3,'3_despues_20251121_091841.jpg','despues'),(5,4,'4_antes_20251121_092235.jpg','antes'),(6,5,'5_antes_20251121_092326.jpg','antes'),(7,7,'7_antes_20251121_101652.jpg','antes'),(8,7,'7_despues_20251121_101653.jpg','despues'),(9,9,'9_antes_20251121_145403.jpg','antes'),(10,9,'9_antes_20251121_145403.jpg','antes'),(11,9,'9_antes_20251121_145403.jpg','antes'),(12,9,'9_despues_20251121_145403.jpg','despues'),(13,9,'9_despues_20251121_145403.jpg','despues'),(14,9,'9_despues_20251121_145403.jpg','despues'),(15,10,'10_antes_20251121_150956.jpg','antes'),(16,10,'10_antes_20251121_150956.jpg','antes'),(17,10,'10_antes_20251121_150956.jpg','antes'),(18,12,'12_antes_20251121_151539_0.jpg','antes'),(19,12,'12_antes_20251121_151539_1.jpg','antes'),(20,12,'12_antes_20251121_151539_2.jpg','antes'),(21,13,'13_antes_20251121_151636_0.jpg','antes'),(22,13,'13_antes_20251121_151636_1.jpg','antes'),(23,13,'13_antes_20251121_151636_2.jpg','antes'),(24,13,'13_despues_20251121_151636_0.jpg','despues'),(25,13,'13_despues_20251121_151636_1.jpg','despues'),(26,13,'13_despues_20251121_151636_2.jpg','despues'),(27,14,'14_antes_20251121_153039_0.jpg','antes'),(28,15,'15_antes_20251121_153753_0.jpg','antes'),(29,16,'16_antes_20251121_155106_0.jpg','antes'),(30,16,'16_antes_20251121_155106_1.jpg','antes'),(31,16,'16_despues_20251121_155106_0.jpg','despues'),(32,16,'16_despues_20251121_155106_1.jpg','despues');

--
-- Table structure for table `mantenimientos`
--

DROP TABLE IF EXISTS `mantenimientos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mantenimientos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `equipo_id` int NOT NULL,
  `fecha` date NOT NULL,
  `tipo` varchar(50) NOT NULL,
  `descripcion` text NOT NULL,
  `estado` varchar(50) DEFAULT 'completado',
  `hora` time DEFAULT '00:00:00',
  `cronograma_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `equipo_id` (`equipo_id`),
  KEY `idx_mantenimientos_cronograma_id` (`cronograma_id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mantenimientos`
--

INSERT INTO `mantenimientos` VALUES (1,6,'2025-11-21','preventivo','se lubricaron las poleas','completado','08:46:17',23),(2,8,'2025-11-21','preventivo','Se verificaron los motores','completado','09:14:36',27),(3,5,'2025-11-21','correctivo','Cambio de gusano','completado','09:18:41',NULL),(4,1,'2025-11-21','preventivo','Se limpió','completado','09:22:35',2),(5,2,'2025-11-21','correctivo','fadsfsdf','completado','09:23:26',NULL),(6,1,'2025-11-21','preventivo','hola','completado','10:07:20',1),(7,3,'2025-11-21','preventivo','se lavo la olla','completado','10:16:52',7),(8,11,'2025-11-21','preventivo','aaa','completado','14:26:12',33),(9,18,'2025-11-21','correctivo','tres fotos antes y 3 despues','completado','14:54:03',NULL),(10,17,'2025-11-21','preventivo','fasasdfasfasdf','completado','15:09:55',43),(11,16,'2025-11-21','preventivo','ventiladores','completado','15:14:39',40),(12,16,'2025-11-21','preventivo','kjñlkjñ','completado','15:15:39',41),(13,11,'2025-11-21','preventivo','vfasgf','completado','15:16:36',34),(14,19,'2025-11-21','preventivo','Este es un mantenimiento de prueba','completado','15:30:39',NULL),(15,19,'2025-11-21','preventivo','fgsdfgsdgfdgsdfg','completado','15:37:53',50),(16,19,'2025-11-21','preventivo','sfdsdfsdf','completado','15:51:05',51),(17,19,'2025-11-21','correctivo','sfdgfdgfdbdsgf','completado','15:52:15',NULL);

--
-- Table structure for table `repuestos`
--

DROP TABLE IF EXISTS `repuestos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `repuestos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `mantenimiento_id` int NOT NULL,
  `nombre` varchar(255) NOT NULL,
  `cantidad` int DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `mantenimiento_id` (`mantenimiento_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `rol` varchar(50) NOT NULL,
  `usuario` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `usuario` (`usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

INSERT INTO `usuarios` VALUES (1,'Diego','Gerente','diegoramirez','abcd1234');