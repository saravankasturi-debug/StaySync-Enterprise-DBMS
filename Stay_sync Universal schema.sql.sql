-- ============================================================
-- PROJECT TITLE : StaySync Enterprise Ledger
-- FILE NAME     : staysync_universal_schema.sql
-- COMPATIBILITY : MySQL 8.0+, PostgreSQL, SQLite, Online Compilers
-- EXECUTION     : ONE-CLICK BATCH EXECUTION
-- ============================================================

-- 1. CLEANUP EXISTING TABLES (Child-to-Parent Order: No Cascade Issues)
DROP TABLE IF EXISTS Reservation_Resale_Marketplace;
DROP TABLE IF EXISTS Payments;
DROP TABLE IF EXISTS Reservation_Rooms;
DROP TABLE IF EXISTS Reservations;
DROP TABLE IF EXISTS Rooms;
DROP TABLE IF EXISTS Room_Types;
DROP TABLE IF EXISTS Hotels;
DROP TABLE IF EXISTS Guests;

-- 2. GUESTS MASTER TABLE
CREATE TABLE Guests (
    guest_id INT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone_number VARCHAR(15) NOT NULL UNIQUE,
    gov_id_type VARCHAR(30) NOT NULL,
    gov_id_number VARCHAR(50) NOT NULL UNIQUE,
    CONSTRAINT chk_email CHECK (email LIKE '%@%.%')
);

-- 3. HOTELS MASTER TABLE
CREATE TABLE Hotels (
    hotel_id INT PRIMARY KEY,
    hotel_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    address VARCHAR(255) NOT NULL,
    star_rating INT DEFAULT 3,
    contact_phone VARCHAR(15) NOT NULL,
    CONSTRAINT chk_star_rating CHECK (star_rating BETWEEN 1 AND 5)
);

-- 4. ROOM_TYPES MASTER TABLE
CREATE TABLE Room_Types (
    room_type_id INT PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL UNIQUE,
    base_price_per_night DECIMAL(10, 2) NOT NULL,
    hourly_rate DECIMAL(10, 2) NOT NULL,
    max_occupancy INT DEFAULT 2 NOT NULL,
    CONSTRAINT chk_base_price CHECK (base_price_per_night > 0.00),
    CONSTRAINT chk_hourly_rate CHECK (hourly_rate > 0.00)
);

-- 5. ROOMS INVENTORY TABLE
CREATE TABLE Rooms (
    room_id INT PRIMARY KEY,
    hotel_id INT NOT NULL,
    room_type_id INT NOT NULL,
    room_number VARCHAR(10) NOT NULL,
    floor_number INT NOT NULL,
    room_status VARCHAR(20) DEFAULT 'AVAILABLE',
    FOREIGN KEY (hotel_id) REFERENCES Hotels(hotel_id),
    FOREIGN KEY (room_type_id) REFERENCES Room_Types(room_type_id),
    CONSTRAINT uk_hotel_room UNIQUE (hotel_id, room_number)
);

-- 6. RESERVATIONS CORE ENGINE
CREATE TABLE Reservations (
    booking_id INT PRIMARY KEY,
    guest_id INT NOT NULL,
    hotel_id INT NOT NULL,
    booking_type VARCHAR(20) DEFAULT 'NIGHTLY' NOT NULL,
    check_in_time VARCHAR(30) NOT NULL,
    check_out_time VARCHAR(30) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    booking_status VARCHAR(25) DEFAULT 'CONFIRMED',
    FOREIGN KEY (guest_id) REFERENCES Guests(guest_id),
    FOREIGN KEY (hotel_id) REFERENCES Hotels(hotel_id)
);

-- 7. RESERVATION_ROOMS JUNCTION TABLE
CREATE TABLE Reservation_Rooms (
    booking_id INT NOT NULL,
    room_id INT NOT NULL,
    locked_price_per_unit DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (booking_id, room_id),
    FOREIGN KEY (booking_id) REFERENCES Reservations(booking_id),
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id)
);

-- 8. PAYMENTS FINANCIAL LEDGER
CREATE TABLE Payments (
    payment_id INT PRIMARY KEY,
    booking_id INT NOT NULL,
    payer_guest_id INT NOT NULL,
    amount_paid DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    transaction_status VARCHAR(20) DEFAULT 'SUCCESS',
    transaction_reference VARCHAR(100) UNIQUE,
    FOREIGN KEY (booking_id) REFERENCES Reservations(booking_id),
    FOREIGN KEY (payer_guest_id) REFERENCES Guests(guest_id)
);

-- 9. P2P RESALE MARKETPLACE
CREATE TABLE Reservation_Resale_Marketplace (
    resale_id INT PRIMARY KEY,
    booking_id INT NOT NULL UNIQUE,
    original_guest_id INT NOT NULL,
    new_buyer_guest_id INT,
    original_price DECIMAL(10, 2) NOT NULL,
    discounted_resale_price DECIMAL(10, 2) NOT NULL,
    resale_status VARCHAR(20) DEFAULT 'ACTIVE',
    FOREIGN KEY (booking_id) REFERENCES Reservations(booking_id),
    FOREIGN KEY (original_guest_id) REFERENCES Guests(guest_id),
    FOREIGN KEY (new_buyer_guest_id) REFERENCES Guests(guest_id)
);

-- ============================================================
-- DML POPULATION (SAMPLE INPUT INSERTS)
-- ============================================================

INSERT INTO Guests VALUES (1, 'Rahul', 'Sharma', 'rahul.sharma@gmail.com', '9876543210', 'AADHAAR', '1234-5678-9012');
INSERT INTO Guests VALUES (2, 'Priya', 'Verma', 'priya.v@yahoo.com', '9812345678', 'PASSPORT', 'A1234567');
INSERT INTO Guests VALUES (3, 'Anish', 'Reddy', 'anish.reddy@outlook.com', '9988776655', 'PAN', 'ABCDE1234F');

INSERT INTO Hotels VALUES (1, 'Taj Banjara', 'Hyderabad', 'Road No 12, Banjara Hills', 5, '040-23355000');
INSERT INTO Hotels VALUES (2, 'Novotel Airport', 'Hyderabad', 'Shamshabad Airport', 4, '040-66250000');

INSERT INTO Room_Types VALUES (1, 'Deluxe Executive', 4500.00, 500.00, 2);
INSERT INTO Room_Types VALUES (2, 'Presidential Suite', 12000.00, 1500.00, 4);

INSERT INTO Rooms VALUES (1, 1, 1, '101', 1, 'OCCUPIED');
INSERT INTO Rooms VALUES (2, 1, 2, '201', 2, 'AVAILABLE');
INSERT INTO Rooms VALUES (3, 2, 1, '102', 1, 'RESERVED');

INSERT INTO Reservations VALUES (1, 1, 1, 'NIGHTLY', '2026-08-15 12:00:00', '2026-08-17 12:00:00', 9000.00, 'LISTED_FOR_RESALE');
INSERT INTO Reservations VALUES (2, 2, 2, 'MICRO_STAY', '2026-08-16 08:00:00', '2026-08-16 14:00:00', 3000.00, 'CONFIRMED');

INSERT INTO Reservation_Rooms VALUES (1, 1, 4500.00);
INSERT INTO Reservation_Rooms VALUES (2, 3, 3000.00);

INSERT INTO Payments VALUES (1, 1, 1, 9000.00, 'UPI', 'SUCCESS', 'TXN_UPI_99887711');
INSERT INTO Payments VALUES (2, 2, 2, 3000.00, 'CREDIT_CARD', 'SUCCESS', 'TXN_CC_44556677');

INSERT INTO Reservation_Resale_Marketplace VALUES (1, 1, 1, NULL, 9000.00, 7200.00, 'ACTIVE');

-- VERIFICATION QUERY
SELECT 
    b.booking_id,
    g.first_name,
    h.hotel_name,
    b.booking_type,
    b.total_amount,
    r.discounted_resale_price,
    r.resale_status
FROM Reservations b
JOIN Guests g ON b.guest_id = g.guest_id
JOIN Hotels h ON b.hotel_id = h.hotel_id
LEFT JOIN Reservation_Resale_Marketplace r ON b.booking_id = r.booking_id;