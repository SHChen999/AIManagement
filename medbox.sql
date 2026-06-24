/*
SQLyog Community v13.1.8 (64 bit)
MySQL - 8.0.32 : Database - m
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`m` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `m`;

/*Table structure for table `family` */

DROP TABLE IF EXISTS `family`;

CREATE TABLE `family` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `age` int DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `allergies` text,
  `medical_history` text,
  `current_medications` text,
  `email` varchar(255) DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `ix_family_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `family` */

insert  into `family`(`id`,`name`,`age`,`gender`,`allergies`,`medical_history`,`current_medications`,`email`) values 
(4,'小王',36,'男','gAAAAABqOyiODi3lcwhxZ4JYUdR2OsthG2QCNIq9Z4CSKPbL_9t-Yk5cjc5aed2G25M_q0puQrSSzFVDkexK8k-sfOyhGaghWw==','gAAAAABqOyiO5qt062xdfYTbY-CGXkVIl7CXmdheyqF8KMLPs0i4acgnKiEyqF6M1bS1rztTFjvC1iva293L1TlVBxAvU_ZWQA==','gAAAAABqOyiOSfNxsPL6VsghhyuX89pqKGjTxUARM-wuEQ2iILjO3Jtyo1Bd9B14hL4FqAOLSDLdnWcxKQFnMsnun93ObXU3Cqyjnp2cr6QYYkj9XmGXmWY=','');

/*Table structure for table `medicine` */

DROP TABLE IF EXISTS `medicine`;

CREATE TABLE `medicine` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `medicine_name` varchar(100) NOT NULL COMMENT '药品名称（含常见商品名）',
  `ingredients` text NOT NULL COMMENT '主要成分',
  `indications` text NOT NULL COMMENT '适应症',
  `contraindications` text NOT NULL COMMENT '禁忌症',
  `side_effects` text NOT NULL COMMENT '常见副作用',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='常见感冒药信息表';

/*Data for the table `medicine` */

insert  into `medicine`(`id`,`medicine_name`,`ingredients`,`indications`,`contraindications`,`side_effects`) values 
(1,'复方氨酚烷胺胶囊（感康、快克、仁和可立克）','对乙酰氨基酚250mg、盐酸金刚烷胺100mg、马来酸氯苯那敏2mg、人工牛黄10mg、咖啡因15mg','普通感冒及流行性感冒引起的发热、头痛、四肢酸痛、打喷嚏、流鼻涕、鼻塞、咽痛','1. 对任一成分过敏者；2. 严重肝肾功能不全者；3. 孕妇及哺乳期妇女','轻度头晕、乏力、嗜睡、口干、恶心、上腹不适、皮疹'),
(2,'酚麻美敏片（泰诺、新康泰克红盒）','对乙酰氨基酚325mg、盐酸伪麻黄碱30mg、氢溴酸右美沙芬15mg、马来酸氯苯那敏2mg','普通感冒或流行性感冒引起的发热、头痛、四肢酸痛、打喷嚏、流鼻涕、鼻塞、咳嗽、咽痛','1. 对任一成分过敏者；2. 严重高血压、冠心病患者；3. 甲状腺功能亢进患者；4. 严重肝肾功能不全者','嗜睡、头晕、口干、恶心、上腹不适、心慌、便秘'),
(3,'氨咖黄敏胶囊（速效伤风胶囊）','对乙酰氨基酚250mg、咖啡因15mg、马来酸氯苯那敏1mg、人工牛黄10mg','普通感冒及流行性感冒引起的发热、头痛、鼻塞、打喷嚏、流鼻涕、咽痛','1. 对任一成分过敏者；2. 严重肝肾功能不全者','轻度头晕、乏力、嗜睡、口干、食欲减退、恶心'),
(4,'布洛芬缓释胶囊（芬必得、缓士芬）','布洛芬0.3g/0.4g（单方）','1. 感冒引起的发热；2. 缓解轻至中度疼痛：头痛、关节痛、肌肉痛、牙痛、痛经','1. 对布洛芬及其他非甾体抗炎药过敏者；2. 活动性消化道溃疡/出血患者；3. 严重心力衰竭患者；4. 严重肝肾功能不全者；5. 妊娠晚期妇女','胃烧灼感、胃痛、恶心、呕吐、头晕、皮疹、肾功能异常'),
(5,'对乙酰氨基酚片（扑热息痛、必理通）','对乙酰氨基酚0.3g/0.5g（单方）','1. 感冒引起的发热；2. 缓解轻至中度疼痛：头痛、咽痛、肌肉痛','1. 对本品过敏者；2. 严重肝肾功能不全者','偶见皮疹、荨麻疹、药热及粒细胞减少'),
(6,'999感冒灵颗粒','三叉苦、野菊花、岗梅、薄荷油、对乙酰氨基酚200mg、马来酸氯苯那敏4mg、咖啡因4mg','风热感冒引起的头痛、发热、鼻塞、流涕、咽痛','1. 对任一成分过敏者；2. 严重肝肾功能不全者','困倦、嗜睡、口渴、虚弱感、偶见皮疹、荨麻疹'),
(7,'连花清瘟胶囊','连翘、金银花、炙麻黄、炒苦杏仁、石膏、板蓝根、绵马贯众、鱼腥草、广藿香、大黄、红景天、薄荷脑、甘草','1. 流行性感冒属热毒袭肺证；2. 新型冠状病毒肺炎轻型、普通型','对本品及所含成分过敏者','恶心、呕吐、腹痛、腹泻、腹胀、皮疹、瘙痒、口干、头晕'),
(8,'感冒清热颗粒','荆芥穗、薄荷、防风、柴胡、紫苏叶、葛根、桔梗、苦杏仁、白芷、苦地丁、芦根','风寒感冒，头痛发热，恶寒身痛，鼻流清涕，咳嗽咽干','对本品及所含成分过敏者','偶见恶心、呕吐、腹胀、腹泻'),
(9,'维C银翘片','金银花、连翘、荆芥、淡豆豉、牛蒡子、桔梗、薄荷油、芦根、淡竹叶、甘草、维生素C、对乙酰氨基酚105mg、马来酸氯苯那敏1.05mg','外感风热所致的流行性感冒，症见发热、头痛、咳嗽、口干、咽喉疼痛','1. 对任一成分过敏者；2. 严重肝肾功能不全者','困倦、嗜睡、口渴、虚弱感、偶见皮疹、荨麻疹、药热及粒细胞减少'),
(10,'疏风解毒胶囊','虎杖、连翘、板蓝根、柴胡、败酱草、马鞭草、芦根、甘草','急性上呼吸道感染属风热证，症见发热、恶风、咽痛、头痛、鼻塞、流浊涕、咳嗽','对本品及所含成分过敏者','偶见恶心、呕吐、腹痛、腹泻、皮疹、胸闷');

/*Table structure for table `mlist` */

DROP TABLE IF EXISTS `mlist`;

CREATE TABLE `mlist` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `ingredients` text,
  `indications` text,
  `contraindications` text,
  `side_effects` text,
  `production_date` varchar(20) DEFAULT NULL,
  `expiry_date` varchar(20) DEFAULT NULL,
  `image_path` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_mlist_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `mlist` */

insert  into `mlist`(`id`,`name`,`ingredients`,`indications`,`contraindications`,`side_effects`,`production_date`,`expiry_date`,`image_path`) values 
(25,'复方氨酚烷胺胶囊','对乙酰氨基酚250mg、盐酸金刚烷胺100mg、马来酸氯苯那敏2mg、人工牛黄10mg、咖啡因15mg','普通感冒及流行性感冒引起的发热、头痛、四肢酸痛、打喷嚏、流鼻涕、鼻塞、咽痛','1. 对任一成分过敏者；2. 严重肝肾功能不全者；3. 孕妇及哺乳期妇女','轻度头晕、乏力、嗜睡、口干、恶心、上腹不适、皮疹','2025-05-19','2026-11-19','uploads/7389c9d30f1041799d597e6f12f8e26d.jpg'),
(27,'连花清瘟胶囊','连翘、金银花、炙麻黄、炒苦杏仁、石膏、板蓝根、绵马贯众、鱼腥草、广藿香、大黄、红景天、薄荷脑、甘草','1. 流行性感冒属热毒袭肺证；2. 新型冠状病毒肺炎轻型、普通型','对本品及所含成分过敏者','恶心、呕吐、腹痛、腹泻、腹胀、皮疹、瘙痒、口干、头晕','2025-03-04','2026-08-12','uploads/378686e2897d43d88bab08dfc171d375.jpg');

/*Table structure for table `reminders` */

DROP TABLE IF EXISTS `reminders`;

CREATE TABLE `reminders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `member_id` int NOT NULL,
  `drug_name` varchar(200) NOT NULL,
  `reminder_time` varchar(19) NOT NULL COMMENT 'YYYY-MM-DD HH:MM:SS',
  `frequency` varchar(50) DEFAULT NULL,
  `interval_hours` int DEFAULT NULL,
  `notes` varchar(500) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `day_of_month` int DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `ix_reminders_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `reminders` */

insert  into `reminders`(`id`,`member_id`,`drug_name`,`reminder_time`,`frequency`,`interval_hours`,`notes`,`active`,`day_of_month`) values 
(6,4,'复方氨酚烷胺胶囊','2026-06-02 18:21:00','daily',0,'1次2粒',1,1);

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
