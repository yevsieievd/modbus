-- phpMyAdmin SQL Dump
-- version 3.4.11.1deb2+deb7u2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jul 06, 2016 at 01:12 AM
-- Server version: 5.5.47
-- PHP Version: 5.4.45-0+deb7u2

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `celse`
--
CREATE DATABASE IF NOT EXISTS `celse` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `celse`;

-- --------------------------------------------------------

--
-- Table structure for table `ctrls`
--

DROP TABLE IF EXISTS `ctrls`;
CREATE TABLE IF NOT EXISTS `ctrls` (
  `idctrls` int(11) NOT NULL AUTO_INCREMENT,
  `bus_id` int(11) NOT NULL COMMENT 'Адрес на шине',
  `online` int(11) DEFAULT NULL COMMENT '0 - не насвязи\n1 - насвязи',
  `type` int(11) NOT NULL COMMENT '0 - датчик температуры\n1 - термостат сервопривода\n3 - частотный преобразователь',
  `description` varchar(100) DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  PRIMARY KEY (`idctrls`),
  UNIQUE KEY `idctrls_UNIQUE` (`idctrls`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=9 ;

--
-- Dumping data for table `ctrls`
--

INSERT INTO `ctrls` (`bus_id`, `online`, `type`, `description`, `last_update`) VALUES
(1, 0, 5, 'Сервопривод', '2016-01-01 02:11:49');
-- --------------------------------------------------------

--
-- Table structure for table `parametrs`
--

DROP TABLE IF EXISTS `parametrs`;
CREATE TABLE IF NOT EXISTS `parametrs` (
  `idparametrs` int(11) NOT NULL AUTO_INCREMENT,
  `bus_id` int(11) NOT NULL COMMENT 'Адрес в сети RTU \nили последнне число IP адреса',
  `addr` int(11) NOT NULL COMMENT 'Номер регистра.',
  `value` float DEFAULT NULL COMMENT 'Текущее значение',
  `to_log` int(11) NOT NULL DEFAULT '0',
  `description` varchar(45) DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  `addr_type` int(11) NOT NULL COMMENT '1 - holding register',
  `direction` int(11) NOT NULL COMMENT 'Направление информации:\n0 - в контроллер;\n1 - в интерфейс',
  `to_set` int(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`idparametrs`),
  UNIQUE KEY `idparametrs_UNIQUE` (`idparametrs`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=58 ;

--
-- Dumping data for table `parametrs`
--

INSERT INTO `parametrs` (`bus_id`, `addr`, `value`, `to_log`, `description`, `last_update`, `addr_type`, `direction`, `to_set`) VALUES
( 1, 0, 50, 0, 'Уставка положения %', '2000-01-01 02:11:17', 1, 0, 0),
( 1, 1, 0, 0, 'Пренудительное положение 1-Откр 2-Закр 3-Мин 4-Макс', '2000-01-01 02:11:17', 1, 0, 0),
( 1, 2, 0, 0, 'Комманда (серв.)', '2000-01-01 02:11:17', 1, 0, 0),
( 1, 3, 0, 0, 'Тип управляемого ус-ва.', '2000-01-01 02:11:17', 1, 0, 0),
( 1, 4, 0, 0, 'Относительная позиция', '2000-01-01 02:11:17', 1, 1, 0),
( 1, 5, 0, 0, 'Абсолютная позиция', '2000-01-01 02:11:17', 1, 1, 0),
( 1, 6, 0, 0, 'Относительная величина протока', '2016-02-28 13:13:52', 1, 1, 0),
( 1, 7, 0, 0, 'Абсолютная величина протока', '2000-01-01 02:11:17', 1, 1, 0),
( 1, 8, 0, 1, 'Температура', '2000-01-01 02:11:50', 1, 1, 0)
;

-- --------------------------------------------------------
--
-- Table structure for table `paramlog`
--

DROP TABLE IF EXISTS `paramlog`;
CREATE TABLE IF NOT EXISTS `paramlog` (
  `idparamlog` int(11) NOT NULL AUTO_INCREMENT,
  `bus_id` int(11) NOT NULL COMMENT 'Адрес в сети RTU \nили последнне число IP адреса',
  `addr` int(11) NOT NULL COMMENT 'Номер регистра.',
  `addr_type` int(11) NOT NULL COMMENT '1 - holding register',
  `value` float DEFAULT NULL COMMENT 'Значение',
  `time` datetime DEFAULT NULL,
  PRIMARY KEY (`idparamlog`),
  UNIQUE KEY `idparamlog_UNIQUE` (`idparamlog`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=47389 ;

--
-- Dumping data for table `paramlog`
--

-- --------------------------------------------------------

--
-- Table structure for table `t_ctrl`
--

DROP TABLE IF EXISTS `t_ctrl`;
CREATE TABLE IF NOT EXISTS `t_ctrl` (
  `idtable1` int(11) NOT NULL AUTO_INCREMENT,
  `type_id` int(11) NOT NULL,
  `description` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`idtable1`),
  UNIQUE KEY `idtable1_UNIQUE` (`idtable1`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='Типы контроллеров - определяет шаблон отображения' AUTO_INCREMENT=4 ;

--
-- Dumping data for table `t_ctrl`
--

INSERT INTO `t_ctrl` (`idtable1`, `type_id`, `description`) VALUES
(1, 0, 'Датчики температуры'),
(2, 1, 'Контроллеры сервопривода'),
(3, 2, 'Частотные преобразователи'),
(4, 3, 'Фанкойлы'),
(5, 4, 'Модуль DO'),
(6, 5, 'Сервопривод');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
