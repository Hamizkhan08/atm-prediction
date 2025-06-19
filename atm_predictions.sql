-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 19, 2025 at 10:00 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `atm_predictions`
--

-- --------------------------------------------------------

--
-- Table structure for table `prediction_history`
--

CREATE TABLE `prediction_history` (
  `id` int(11) NOT NULL,
  `atm_id` varchar(50) NOT NULL,
  `prediction_date` date NOT NULL,
  `transactions` int(11) NOT NULL,
  `cash_loaded` decimal(15,2) NOT NULL,
  `prediction_result` varchar(100) NOT NULL,
  `prediction_status` enum('✅ Sufficiently Loaded','⚠️ Likely to Run Out') NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `prediction_history`
--

INSERT INTO `prediction_history` (`id`, `atm_id`, `prediction_date`, `transactions`, `cash_loaded`, `prediction_result`, `prediction_status`, `created_at`) VALUES
(19, '1', '2025-06-19', 150, 500000.00, 'ATM 1 on 2025-06-19: ✅ Sufficiently Loaded. (Predicted dispense: ₹134,320, Est. remaining: ₹365,680)', '✅ Sufficiently Loaded', '2025-06-19 19:59:28'),
(20, '2', '2025-06-19', 100, 2000.00, 'ATM 2 on 2025-06-19: ⚠️ Likely to Run Out. (Predicted dispense: ₹134,320, Est. remaining: ₹-132,320)', '⚠️ Likely to Run Out', '2025-06-19 19:59:41');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `prediction_history`
--
ALTER TABLE `prediction_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_atm_date` (`atm_id`,`prediction_date`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `prediction_history`
--
ALTER TABLE `prediction_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
