-- MySQL dump 10.13  Distrib 5.7.24, for osx11.1 (x86_64)
--
-- Host: localhost    Database: CVD_RiskDB
-- ------------------------------------------------------
-- Server version	9.0.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts_user`
--

DROP TABLE IF EXISTS `accounts_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `accounts_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `role` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts_user`
--

LOCK TABLES `accounts_user` WRITE;
/*!40000 ALTER TABLE `accounts_user` DISABLE KEYS */;
INSERT INTO `accounts_user` VALUES (1,'pbkdf2_sha256$870000$XfRYiBcg6z2Ucm0k4kYXdm$XX6yf3dLs7jmr+LhQY8NuNHupEjtLGi+MVKixTNx+8c=','2025-03-24 15:00:53.042989',1,'sanjanasnvs','','','sanjanasrini30@gmail.com',1,1,'2025-03-24 14:15:13.157453',''),(2,'pbkdf2_sha256$870000$zuCjH3XmKSI5rinyvqEaIJ$ss0VwmNc+cczG6+3F24UQK6b5FEd6GOCuR3e5K3NJN4=','2025-03-24 15:49:00.625252',0,'bob_marley','','','bob.marley@gmail.com',0,1,'2025-03-24 15:13:07.115670','patient'),(3,'pbkdf2_sha256$870000$ZMHyW9PAdihDCgQlXHFsUl$Oy7xBI73jEhztjeI1WwE5rs3W5jPV5Fi6By6LfBnBt8=','2025-03-27 16:02:32.723894',1,'adminuser','','','',1,1,'2025-03-27 16:01:30.640340','admin');
/*!40000 ALTER TABLE `accounts_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Admins`
--

DROP TABLE IF EXISTS `Admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Admins` (
  `admin_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('SuperAdmin','Manager','Support') DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`admin_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Admins`
--

LOCK TABLES `Admins` WRITE;
/*!40000 ALTER TABLE `Admins` DISABLE KEYS */;
/*!40000 ALTER TABLE `Admins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=117 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add user',6,'add_user'),(22,'Can change user',6,'change_user'),(23,'Can delete user',6,'delete_user'),(24,'Can view user',6,'view_user'),(25,'Can add response',7,'add_response'),(26,'Can change response',7,'change_response'),(27,'Can delete response',7,'delete_response'),(28,'Can view response',7,'view_response'),(29,'Can add questionnaire',8,'add_questionnaire'),(30,'Can change questionnaire',8,'change_questionnaire'),(31,'Can delete questionnaire',8,'delete_questionnaire'),(32,'Can view questionnaire',8,'view_questionnaire'),(33,'Can add accounts questionnaire',9,'add_accountsquestionnaire'),(34,'Can change accounts questionnaire',9,'change_accountsquestionnaire'),(35,'Can delete accounts questionnaire',9,'delete_accountsquestionnaire'),(36,'Can view accounts questionnaire',9,'view_accountsquestionnaire'),(37,'Can add accounts response',10,'add_accountsresponse'),(38,'Can change accounts response',10,'change_accountsresponse'),(39,'Can delete accounts response',10,'delete_accountsresponse'),(40,'Can view accounts response',10,'view_accountsresponse'),(41,'Can add accounts user',11,'add_accountsuser'),(42,'Can change accounts user',11,'change_accountsuser'),(43,'Can delete accounts user',11,'delete_accountsuser'),(44,'Can view accounts user',11,'view_accountsuser'),(45,'Can add accounts user groups',12,'add_accountsusergroups'),(46,'Can change accounts user groups',12,'change_accountsusergroups'),(47,'Can delete accounts user groups',12,'delete_accountsusergroups'),(48,'Can view accounts user groups',12,'view_accountsusergroups'),(49,'Can add accounts user user permissions',13,'add_accountsuseruserpermissions'),(50,'Can change accounts user user permissions',13,'change_accountsuseruserpermissions'),(51,'Can delete accounts user user permissions',13,'delete_accountsuseruserpermissions'),(52,'Can view accounts user user permissions',13,'view_accountsuseruserpermissions'),(53,'Can add admins',14,'add_admins'),(54,'Can change admins',14,'change_admins'),(55,'Can delete admins',14,'delete_admins'),(56,'Can view admins',14,'view_admins'),(57,'Can add auth group',15,'add_authgroup'),(58,'Can change auth group',15,'change_authgroup'),(59,'Can delete auth group',15,'delete_authgroup'),(60,'Can view auth group',15,'view_authgroup'),(61,'Can add auth group permissions',16,'add_authgrouppermissions'),(62,'Can change auth group permissions',16,'change_authgrouppermissions'),(63,'Can delete auth group permissions',16,'delete_authgrouppermissions'),(64,'Can view auth group permissions',16,'view_authgrouppermissions'),(65,'Can add auth permission',17,'add_authpermission'),(66,'Can change auth permission',17,'change_authpermission'),(67,'Can delete auth permission',17,'delete_authpermission'),(68,'Can view auth permission',17,'view_authpermission'),(69,'Can add clinicians',18,'add_clinicians'),(70,'Can change clinicians',18,'change_clinicians'),(71,'Can delete clinicians',18,'delete_clinicians'),(72,'Can view clinicians',18,'view_clinicians'),(73,'Can add django admin log',19,'add_djangoadminlog'),(74,'Can change django admin log',19,'change_djangoadminlog'),(75,'Can delete django admin log',19,'delete_djangoadminlog'),(76,'Can view django admin log',19,'view_djangoadminlog'),(77,'Can add django content type',20,'add_djangocontenttype'),(78,'Can change django content type',20,'change_djangocontenttype'),(79,'Can delete django content type',20,'delete_djangocontenttype'),(80,'Can view django content type',20,'view_djangocontenttype'),(81,'Can add django migrations',21,'add_djangomigrations'),(82,'Can change django migrations',21,'change_djangomigrations'),(83,'Can delete django migrations',21,'delete_djangomigrations'),(84,'Can view django migrations',21,'view_djangomigrations'),(85,'Can add django session',22,'add_djangosession'),(86,'Can change django session',22,'change_djangosession'),(87,'Can delete django session',22,'delete_djangosession'),(88,'Can view django session',22,'view_djangosession'),(89,'Can add ml models',23,'add_mlmodels'),(90,'Can change ml models',23,'change_mlmodels'),(91,'Can delete ml models',23,'delete_mlmodels'),(92,'Can view ml models',23,'view_mlmodels'),(93,'Can add patient outcomes',24,'add_patientoutcomes'),(94,'Can change patient outcomes',24,'change_patientoutcomes'),(95,'Can delete patient outcomes',24,'delete_patientoutcomes'),(96,'Can view patient outcomes',24,'view_patientoutcomes'),(97,'Can add patients',25,'add_patients'),(98,'Can change patients',25,'change_patients'),(99,'Can delete patients',25,'delete_patients'),(100,'Can view patients',25,'view_patients'),(101,'Can add responses',26,'add_responses'),(102,'Can change responses',26,'change_responses'),(103,'Can delete responses',26,'delete_responses'),(104,'Can view responses',26,'view_responses'),(105,'Can add risk stratification',27,'add_riskstratification'),(106,'Can change risk stratification',27,'change_riskstratification'),(107,'Can delete risk stratification',27,'delete_riskstratification'),(108,'Can view risk stratification',27,'view_riskstratification'),(109,'Can add users',28,'add_users'),(110,'Can change users',28,'change_users'),(111,'Can delete users',28,'delete_users'),(112,'Can view users',28,'view_users'),(113,'Can add clinician patient',29,'add_clinicianpatient'),(114,'Can change clinician patient',29,'change_clinicianpatient'),(115,'Can delete clinician patient',29,'delete_clinicianpatient'),(116,'Can view clinician patient',29,'view_clinicianpatient');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Clinician_Patient`
--

DROP TABLE IF EXISTS `Clinician_Patient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Clinician_Patient` (
  `clinician_id` int NOT NULL,
  `patient_id` int NOT NULL,
  `assigned_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`clinician_id`,`patient_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `clinician_patient_ibfk_1` FOREIGN KEY (`clinician_id`) REFERENCES `Clinicians` (`clinician_id`) ON DELETE CASCADE,
  CONSTRAINT `clinician_patient_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `Patients` (`patient_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Clinician_Patient`
--

LOCK TABLES `Clinician_Patient` WRITE;
/*!40000 ALTER TABLE `Clinician_Patient` DISABLE KEYS */;
/*!40000 ALTER TABLE `Clinician_Patient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Clinicians`
--

DROP TABLE IF EXISTS `Clinicians`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Clinicians` (
  `clinician_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `specialty` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `admin_id` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`clinician_id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `fk_admin_clinicians` (`admin_id`),
  CONSTRAINT `fk_admin_clinicians` FOREIGN KEY (`admin_id`) REFERENCES `Admins` (`admin_id`),
  CONSTRAINT `fk_clinicians_users` FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Clinicians`
--

LOCK TABLES `Clinicians` WRITE;
/*!40000 ALTER TABLE `Clinicians` DISABLE KEYS */;
/*!40000 ALTER TABLE `Clinicians` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_accounts_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_accounts_user_id` FOREIGN KEY (`user_id`) REFERENCES `accounts_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (9,'accounts','accountsquestionnaire'),(10,'accounts','accountsresponse'),(11,'accounts','accountsuser'),(12,'accounts','accountsusergroups'),(13,'accounts','accountsuseruserpermissions'),(14,'accounts','admins'),(15,'accounts','authgroup'),(16,'accounts','authgrouppermissions'),(17,'accounts','authpermission'),(29,'accounts','clinicianpatient'),(18,'accounts','clinicians'),(19,'accounts','djangoadminlog'),(20,'accounts','djangocontenttype'),(21,'accounts','djangomigrations'),(22,'accounts','djangosession'),(23,'accounts','mlmodels'),(24,'accounts','patientoutcomes'),(25,'accounts','patients'),(8,'accounts','questionnaire'),(7,'accounts','response'),(26,'accounts','responses'),(27,'accounts','riskstratification'),(6,'accounts','user'),(28,'accounts','users'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(5,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-03-24 14:13:12.776504'),(2,'contenttypes','0002_remove_content_type_name','2025-03-24 14:13:12.801315'),(3,'auth','0001_initial','2025-03-24 14:13:12.871880'),(4,'auth','0002_alter_permission_name_max_length','2025-03-24 14:13:12.890683'),(5,'auth','0003_alter_user_email_max_length','2025-03-24 14:13:12.893716'),(6,'auth','0004_alter_user_username_opts','2025-03-24 14:13:12.896031'),(7,'auth','0005_alter_user_last_login_null','2025-03-24 14:13:12.898134'),(8,'auth','0006_require_contenttypes_0002','2025-03-24 14:13:12.898485'),(9,'auth','0007_alter_validators_add_error_messages','2025-03-24 14:13:12.900636'),(10,'auth','0008_alter_user_username_max_length','2025-03-24 14:13:12.902950'),(11,'auth','0009_alter_user_last_name_max_length','2025-03-24 14:13:12.905206'),(12,'auth','0010_alter_group_name_max_length','2025-03-24 14:13:12.911378'),(13,'auth','0011_update_proxy_permissions','2025-03-24 14:13:12.915514'),(14,'auth','0012_alter_user_first_name_max_length','2025-03-24 14:13:12.917614'),(15,'accounts','0001_initial','2025-03-24 14:13:12.999239'),(16,'admin','0001_initial','2025-03-24 14:13:13.032240'),(17,'admin','0002_logentry_remove_auto_add','2025-03-24 14:13:13.040492'),(18,'admin','0003_logentry_add_action_flag_choices','2025-03-24 14:13:13.045212'),(19,'sessions','0001_initial','2025-03-24 14:13:13.053002'),(20,'accounts','0002_questionnaire_response','2025-03-27 15:53:06.980701'),(21,'accounts','0003_accountsquestionnaire_accountsresponse_accountsuser_and_more','2025-03-28 14:19:53.249371');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('51vvlh6dagw9kgili0mxx691ospxpa4r','.eJxVjDsOgzAQRO_iOrKMwZ9NmZ4zWLtrOyaJjIShinL3gESRdKN5b-YtAm5rCVtLS5iiuIpeXH47Qn6meoD4wHqfJc91XSaShyJP2uQ4x_S6ne7fQcFW9jVoVuDJwoARaTDETLpnn9AxDTp3SvlswFnoLLN1ezBeaYCcUzYYxecL7sI4IQ:1txpge:zaRvn6F-B0Mz5ktU4zNUnH63eriOZs2rDxdtsJd_UYA','2025-04-10 16:02:32.727372');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ML_Models`
--

DROP TABLE IF EXISTS `ML_Models`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ML_Models` (
  `model_id` int NOT NULL AUTO_INCREMENT,
  `method` varchar(100) NOT NULL,
  `title` varchar(255) NOT NULL,
  PRIMARY KEY (`model_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ML_Models`
--

LOCK TABLES `ML_Models` WRITE;
/*!40000 ALTER TABLE `ML_Models` DISABLE KEYS */;
/*!40000 ALTER TABLE `ML_Models` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Patient_Outcomes`
--

DROP TABLE IF EXISTS `Patient_Outcomes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Patient_Outcomes` (
  `outcome_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int DEFAULT NULL,
  `outcome_description` text NOT NULL,
  `reported_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`outcome_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `patient_outcomes_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `Patients` (`patient_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Patient_Outcomes`
--

LOCK TABLES `Patient_Outcomes` WRITE;
/*!40000 ALTER TABLE `Patient_Outcomes` DISABLE KEYS */;
/*!40000 ALTER TABLE `Patient_Outcomes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Patients`
--

DROP TABLE IF EXISTS `Patients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Patients` (
  `patient_id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `gender` enum('Male','Female','Other') DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `admin_id` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`patient_id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `fk_admin_patients` (`admin_id`),
  CONSTRAINT `fk_admin_patients` FOREIGN KEY (`admin_id`) REFERENCES `Admins` (`admin_id`),
  CONSTRAINT `fk_patients_users` FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Patients`
--

LOCK TABLES `Patients` WRITE;
/*!40000 ALTER TABLE `Patients` DISABLE KEYS */;
/*!40000 ALTER TABLE `Patients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Questionnaire`
--

DROP TABLE IF EXISTS `Questionnaire`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Questionnaire` (
  `question_id` int NOT NULL AUTO_INCREMENT,
  `question_text` text NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `dependencies` int DEFAULT NULL,
  `admin_id` int DEFAULT NULL,
  `question_order` int NOT NULL DEFAULT '0',
  `subcategory` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`question_id`),
  KEY `fk_admin_questionnaire` (`admin_id`),
  KEY `fk_dependencies_self` (`dependencies`),
  CONSTRAINT `fk_admin_questionnaire` FOREIGN KEY (`admin_id`) REFERENCES `Admins` (`admin_id`),
  CONSTRAINT `fk_dependencies_self` FOREIGN KEY (`dependencies`) REFERENCES `Questionnaire` (`question_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Questionnaire`
--

LOCK TABLES `Questionnaire` WRITE;
/*!40000 ALTER TABLE `Questionnaire` DISABLE KEYS */;
/*!40000 ALTER TABLE `Questionnaire` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `QuestionResponseOptions`
--

DROP TABLE IF EXISTS `QuestionResponseOptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `QuestionResponseOptions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `question_id` int DEFAULT NULL,
  `option_text` text,
  `value_range_start` float DEFAULT NULL,
  `value_range_end` float DEFAULT NULL,
  `option_label` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `question_id` (`question_id`),
  CONSTRAINT `questionresponseoptions_ibfk_1` FOREIGN KEY (`question_id`) REFERENCES `Questionnaire` (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `QuestionResponseOptions`
--

LOCK TABLES `QuestionResponseOptions` WRITE;
/*!40000 ALTER TABLE `QuestionResponseOptions` DISABLE KEYS */;
/*!40000 ALTER TABLE `QuestionResponseOptions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Responses`
--

DROP TABLE IF EXISTS `Responses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Responses` (
  `response_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int DEFAULT NULL,
  `question_id` int DEFAULT NULL,
  `response_text` text NOT NULL,
  `response_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `response_type` varchar(50) DEFAULT NULL,
  `numeric_response` float DEFAULT NULL,
  `boolean_response` tinyint(1) DEFAULT NULL,
  `option_selected_id` int DEFAULT NULL,
  PRIMARY KEY (`response_id`),
  KEY `patient_id` (`patient_id`),
  KEY `question_id` (`question_id`),
  KEY `option_selected_id` (`option_selected_id`),
  CONSTRAINT `responses_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `Patients` (`patient_id`) ON DELETE CASCADE,
  CONSTRAINT `responses_ibfk_2` FOREIGN KEY (`question_id`) REFERENCES `Questionnaire` (`question_id`) ON DELETE CASCADE,
  CONSTRAINT `responses_ibfk_3` FOREIGN KEY (`option_selected_id`) REFERENCES `QuestionResponseOptions` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Responses`
--

LOCK TABLES `Responses` WRITE;
/*!40000 ALTER TABLE `Responses` DISABLE KEYS */;
/*!40000 ALTER TABLE `Responses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Risk_Stratification`
--

DROP TABLE IF EXISTS `Risk_Stratification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Risk_Stratification` (
  `stratification_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int DEFAULT NULL,
  `risk_score` decimal(5,2) DEFAULT NULL,
  `recommendation` text,
  `assessed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `model_id` int DEFAULT NULL,
  PRIMARY KEY (`stratification_id`),
  KEY `patient_id` (`patient_id`),
  KEY `fk_risk_ml` (`model_id`),
  CONSTRAINT `fk_risk_ml` FOREIGN KEY (`model_id`) REFERENCES `ML_Models` (`model_id`) ON DELETE SET NULL,
  CONSTRAINT `risk_stratification_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `Patients` (`patient_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Risk_Stratification`
--

LOCK TABLES `Risk_Stratification` WRITE;
/*!40000 ALTER TABLE `Risk_Stratification` DISABLE KEYS */;
/*!40000 ALTER TABLE `Risk_Stratification` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Users`
--

DROP TABLE IF EXISTS `Users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('patient','clinician','admin') NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Users`
--

LOCK TABLES `Users` WRITE;
/*!40000 ALTER TABLE `Users` DISABLE KEYS */;
/*!40000 ALTER TABLE `Users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-05 19:08:13
