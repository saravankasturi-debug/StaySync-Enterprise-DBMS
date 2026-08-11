-- ============================================================
-- PROJECT TITLE : StaySync Enterprise Ledger
-- FILE NAME     : staysync_oracle10g_schema.sql
-- TARGET ENGINE : Oracle 10g / 11g / 19c / SQL*Plus
-- DESCRIPTION   : Strict Oracle SQL Script with Foreign Keys, 
--                 Check Constraints, and Sample Data.
-- ============================================================

-- 1. SAFE DROP EXISTING TABLES IN ORACLE
BEGIN
   EXECUTE IMMEDIATE 'DROP TABLE Reservation_Resale_Marketplace CASCADE CONSTRAINTS';
   EXECUTE IMMEDIATE 'DROP TABLE Payments CASCADE CONSTRAINTS';
   EXECUTE IMMEDIATE 'DROP TABLE Reservation_Rooms CASCADE CONSTRAINTS';
   EXECUTE IMMEDIATE 'DROP TABLE Reservations CASCADE CONSTRAINTS';
   EXECUTE IMMEDIATE 'DROP TABLE Rooms CASCADE CONSTRAINTS';
   EXECUTE IMMEDIATE 'DROP TABLE Room_Types CASCADE CONSTRAINTS';
   EXECUTE IMMEDIATE 'DROP TABLE Hotels CASCADE CONSTRAINTS';
   EXECUTE IMMEDIATE 'DROP TABLE Guests CASCADE CONSTRAINTS';
EXCEPTION
   WHEN OTHERS THEN NULL;
END;
/

-- ------------------------------------------------------------
-- 1. GUESTS TABLE
-- ------------------------------------------------------------
CREATE TABLE Guests (
    guest_id NUMBER PRIMARY KEY,
    first_name VARCHAR2(50) NOT NULL,
    last_name VARCHAR2(50) NOT NULL,
    email VARCHAR2(100) NOT NULL UNIQUE,
    phone_number VARCHAR2(15) NOT NULL UNIQUE,
    gov_id_type VARCHAR2(30) NOT NULL,
    gov_id_number VARCHAR2(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT chk_email_format CHECK (email LIKE '%@%.%')
);

-- ------------------------------------------------------------
-- 2. HOTELS TABLE
-- ------------------------------------------------------------
CREATE TABLE Hotels (
    hotel_id NUMBER PRIMARY KEY,
    hotel_name VARCHAR2(100) NOT NULL,
    city VARCHAR2(50) NOT NULL,
    address VARCHAR2(255) NOT NULL,
    star_rating NUMBER DEFAULT 3,
    contact_phone VARCHAR2(15) NOT NULL,
    created_at TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT chk_star_rating CHECK (star_rating BETWEEN 1 AND 5)
);

-- ------------------------------------------------------------
-- 3. ROOM_TYPES TABLE
-- ------------------------------------------------------------
CREATE TABLE Room_Types (
    room_type_id NUMBER PRIMARY KEY,
    type_name VARCHAR2(50) NOT NULL UNIQUE,
    base_price_per_night NUMBER(10, 2) NOT NULL,
    hourly_rate NUMBER(10, 2) NOT NULL,
    max_occupancy NUMBER DEFAULT 2 NOT NULL,
    CONSTRAINT chk_base_price CHECK (base_price_per_night > 0.00),
    CONSTRAINT chk_hourly_rate CHECK (hourly_rate > 0.00)
);

-- ------------------------------------------------------------
-- 4. ROOMS TABLE
-- ------------------------------------------------------------
CREATE TABLE Rooms (
    room_id NUMBER PRIMARY KEY,
    hotel_id NUMBER NOT NULL,
    room_type_id NUMBER NOT NULL,
    room_number VARCHAR2(10) NOT NULL,
    floor_number NUMBER NOT NULL,
    room_status VARCHAR2(20) DEFAULT 'AVAILABLE',
    FOREIGN KEY (hotel_id) REFERENCES Hotels(hotel_id) ON DELETE CASCADE,
    FOREIGN KEY (room_type_id) REFERENCES Room_Types(room_type_id),
    CONSTRAINT uk_hotel_room UNIQUE (hotel_id, room_number),
    CONSTRAINT chk_room_status CHECK (room_status IN ('AVAILABLE', 'OCCUPIED', 'MAINTENANCE', 'RESERVED'))
);

-- ------------------------------------------------------------
-- 5. RESERVATIONS TABLE
-- ------------------------------------------------------------
CREATE TABLE Reservations (
    booking_id NUMBER PRIMARY KEY,
    guest_id NUMBER NOT NULL,
    hotel_id NUMBER NOT NULL,
    booking_type VARCHAR2(20) DEFAULT 'NIGHTLY' NOT NULL,
    check_in_time TIMESTAMP NOT NULL,
    check_out_time TIMESTAMP NOT NULL,
    total_amount NUMBER(10, 2) NOT NULL,
    booking_status VARCHAR2(25) DEFAULT 'CONFIRMED',
    created_at TIMESTAMP DEFAULT SYSTIMESTAMP,
    FOREIGN KEY (guest_id) REFERENCES Guests(guest_id),
    FOREIGN KEY (hotel_id) REFERENCES Hotels(hotel_id),
    CONSTRAINT chk_dates CHECK (check_out_time > check_in_time),
    CONSTRAINT chk_booking_type CHECK (booking_type IN ('NIGHTLY', 'MICRO_STAY'))
);

-- ------------------------------------------------------------
-- 6. RESERVATION_ROOMS TABLE (Junction Table)
-- ------------------------------------------------------------
CREATE TABLE Reservation_Rooms (
    booking_id NUMBER NOT NULL,
    room_id NUMBER NOT NULL,
    locked_price_per_unit NUMBER(10, 2) NOT NULL,
    PRIMARY KEY (booking_id, room_id),
    FOREIGN KEY (booking_id) REFERENCES Reservations(booking_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id)
);

-- ------------------------------------------------------------
-- 7. PAYMENTS TABLE
-- ------------------------------------------------------------
CREATE TABLE Payments (
    payment_id NUMBER PRIMARY KEY,
    booking_id NUMBER NOT NULL,
    payer_guest_id NUMBER NOT NULL,
    amount_paid NUMBER(10, 2) NOT NULL,
    payment_method VARCHAR2(20) NOT NULL,
    transaction_status VARCHAR2(20) DEFAULT 'SUCCESS',
    transaction_reference VARCHAR2(100) UNIQUE,
    payment_date TIMESTAMP DEFAULT SYSTIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES Reservations(booking_id) ON DELETE CASCADE,
    FOREIGN KEY (payer_guest_id) REFERENCES Guests(guest_id)
);

-- ------------------------------------------------------------
-- 8. RESERVATION_RESALE_MARKETPLACE TABLE
-- ------------------------------------------------------------
CREATE TABLE Reservation_Resale_Marketplace (
    resale_id NUMBER PRIMARY KEY,
    booking_id NUMBER NOT NULL UNIQUE,
    original_guest_id NUMBER NOT NULL,
    new_buyer_guest_id NUMBER NULL,
    original_price NUMBER(10, 2) NOT NULL,
    discounted_resale_price NUMBER(10, 2) NOT NULL,
    resale_status VARCHAR2(20) DEFAULT 'ACTIVE',
    listed_at TIMESTAMP DEFAULT SYSTIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES Reservations(booking_id) ON DELETE CASCADE,
    FOREIGN KEY (original_guest_id) REFERENCES Guests(guest_id),
    FOREIGN KEY (new_buyer_guest_id) REFERENCES Guests(guest_id),
    CONSTRAINT chk_resale_price CHECK (discounted_resale_price < original_price)
);

-- ============================================================
-- ORACLE 10g SAMPLE DATA INSERTS (DML)
-- ============================================================

INSERT INTO Guests VALUES (1, 'Rahul', 'Sharma', 'rahul.sharma@gmail.com', '9876543210', 'AADHAAR', '1234-5678-9012', SYSTIMESTAMP);
INSERT INTO Guests VALUES (2, 'Priya', 'Verma', 'priya.v@yahoo.com', '9812345678', 'PASSPORT', 'A1234567', SYSTIMESTAMP);
INSERT INTO Guests VALUES (3, 'Anish', 'Reddy', 'anish.reddy@outlook.com', '9988776655', 'PAN', 'ABCDE1234F', SYSTIMESTAMP);

INSERT INTO Hotels VALUES (1, 'Taj Banjara', 'Hyderabad', 'Road No 12, Banjara Hills', 5, '040-23355000', SYSTIMESTAMP);
INSERT INTO Hotels VALUES (2, 'Novotel Airport', 'Hyderabad', 'Shamshabad Airport', 4, '040-66250000', SYSTIMESTAMP);

INSERT INTO Room_Types VALUES (1, 'Deluxe Executive', 4500.00, 500.00, 2);
INSERT INTO Room_Types VALUES (2, 'Presidential Suite', 12000.00, 1500.00, 4);

INSERT INTO Rooms VALUES (1, 1, 1, '101', 1, 'OCCUPIED');
INSERT INTO Rooms VALUES (2, 1, 2, '201', 2, 'AVAILABLE');
INSERT INTO Rooms VALUES (3, 2, 1, '102', 1, 'RESERVED');

INSERT INTO Reservations VALUES (1, 1, 1, 'NIGHTLY', TO_TIMESTAMP('2026-08-15 12:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2026-08-17 12:00:00', 'YYYY-MM-DD HH24:MI:SS'), 9000.00, 'LISTED_FOR_RESALE', SYSTIMESTAMP);
INSERT INTO Reservations VALUES (2, 2, 2, 'MICRO_STAY', TO_TIMESTAMP('2026-08-16 08:00:00', 'YYYY-MM-DD HH24:MI:SS'), TO_TIMESTAMP('2026-08-16 14:00:00', 'YYYY-MM-DD HH24:MI:SS'), 3000.00, 'CONFIRMED', SYSTIMESTAMP);

INSERT INTO Reservation_Rooms VALUES (1, 1, 4500.00);
INSERT INTO Reservation_Rooms VALUES (2, 3, 3000.00);

INSERT INTO Payments VALUES (1, 1, 1, 9000.00, 'UPI', 'SUCCESS', 'TXN_UPI_99887711', SYSTIMESTAMP);
INSERT INTO Payments VALUES (2, 2, 2, 3000.00, 'CREDIT_CARD', 'SUCCESS', 'TXN_CC_44556677', SYSTIMESTAMP);

INSERT INTO Reservation_Resale_Marketplace VALUES (1, 1, 1, NULL, 9000.00, 7200.00, 'ACTIVE', SYSTIMESTAMP);

-- COMMIT TRANSACTION IN ORACLE
COMMIT;

-- ------------------------------------------------------------
-- VERIFICATION SELECT QUERY
-- ------------------------------------------------------------
SELECT 
    b.booking_id,
    g.first_name || ' ' || g.last_name AS guest_name,
    h.hotel_name,
    b.booking_type,
    b.total_amount,
    r.discounted_resale_price,
    r.resale_status
FROM Reservations b
JOIN Guests g ON b.guest_id = g.guest_id
JOIN Hotels h ON b.hotel_id = h.hotel_id
LEFT JOIN Reservation_Resale_Marketplace r ON b.booking_id = r.booking_id;