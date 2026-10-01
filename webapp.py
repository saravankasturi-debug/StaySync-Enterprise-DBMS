import streamlit as st
import pandas as pd
import sqlite3
import datetime
import os

# ==========================================
# 1. PAGE SETUP & DAE DARK NAVY PALETTE
# ==========================================
st.set_page_config(
    page_title="StaySync Enterprise — Review-2",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force Pure DAE Dark Navy & Electric Cyan Palette
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    /* Global App Canvas: Deep Navy Blue */
    html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #0B132B !important;
        color: #FFFFFF !important;
    }

    /* Transparent Top Header */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Left Sidebar: Navy Blue */
    section[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background-color: #111D4A !important;
        border-right: 1px solid #1E293B !important;
    }

    /* Force All Text in Sidebar to Pure High-Contrast White */
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    /* Dark Slate Radio Navigation Cards */
    div[data-testid="stRadio"] > div {
        gap: 10px;
    }
    div[data-testid="stRadio"] label {
        background-color: #1C2541 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        cursor: pointer !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stRadio"] label:hover {
        background-color: #232D4F !important;
        border-color: #00B4D8 !important;
    }
    /* Hide default radio circle dots */
    div[data-testid="stRadio"] label > div:first-child {
        display: none !important;
    }
    /* Bold White Navigation Text */
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span,
    div[data-testid="stRadio"] label div {
        color: #FFFFFF !important;
        font-size: 14px !important;
        font-weight: 700 !important;
    }

    /* Main Branding Header */
    .brand-title {
        font-size: 30px;
        font-weight: 800;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 10px;
        letter-spacing: -0.5px;
    }
    .brand-highlight {
        color: #00B4D8;
    }

    /* DAE Amber Gold Metric Box */
    .metric-box {
        background-color: #1C2541;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .metric-box:hover {
        transform: translateY(-2px);
        border-color: #00B4D8;
    }
    .metric-label {
        color: #94A3B8;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-number {
        color: #FFC107;
        font-size: 32px;
        font-weight: 800;
        margin-top: 6px;
    }

    /* High-Contrast Information Box */
    .info-card-box {
        background-color: #1C2541;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .card-title-text {
        color: #00B4D8;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    .card-body-text {
        font-size: 15px;
        font-weight: 500;
        color: #E2E8F0;
        line-height: 1.5;
    }

    /* Yellow Accent Reality Check Banner */
    .disclaimer-card {
        background: #1C2541;
        border-left: 5px solid #FFC107;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 18px 0px;
        color: #FFFFFF;
        font-size: 14px;
        line-height: 1.5;
    }

    /* Resale Listing Card */
    .resale-listing-card {
        background-color: #1C2541;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 14px;
        transition: border-color 0.2s ease;
    }
    .resale-listing-card:hover {
        border-color: #00B4D8;
    }

    /* Electric Cyan Action Buttons */
    .stButton button {
        background-color: #00B4D8 !important;
        color: #0A192F !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 9px 20px !important;
    }
    .stButton button:hover {
        background-color: #90E0EF !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATABASE INITIALIZATION & 3NF SEEDING
# ==========================================
@st.cache_resource
def setup_database():
    conn = sqlite3.connect("staysync_live.db", check_same_thread=False)
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS Guests (
        guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT UNIQUE, phone TEXT, credit_card TEXT
    );
    CREATE TABLE IF NOT EXISTS Hotels (
        hotel_id INTEGER PRIMARY KEY AUTOINCREMENT,
        hotel_name TEXT, city TEXT, star_rating INTEGER
    );
    CREATE TABLE IF NOT EXISTS Room_Types (
        room_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_name TEXT UNIQUE, base_price_per_night REAL, hourly_rate REAL, max_occupancy INTEGER
    );
    CREATE TABLE IF NOT EXISTS Rooms (
        room_id INTEGER PRIMARY KEY AUTOINCREMENT,
        hotel_id INTEGER, room_type_id INTEGER, room_number TEXT, room_status TEXT DEFAULT 'AVAILABLE',
        FOREIGN KEY (hotel_id) REFERENCES Hotels(hotel_id),
        FOREIGN KEY (room_type_id) REFERENCES Room_Types(room_type_id)
    );
    CREATE TABLE IF NOT EXISTS Reservations (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_id INTEGER, hotel_id INTEGER, room_id INTEGER, booking_type TEXT,
        check_in TEXT, check_out TEXT, total_amount REAL, booking_status TEXT DEFAULT 'CONFIRMED'
    );
    CREATE TABLE IF NOT EXISTS Reservation_Resale (
        resale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER UNIQUE, original_guest_id INTEGER, new_buyer_guest_id INTEGER,
        original_price REAL, discounted_price REAL, resale_status TEXT DEFAULT 'ACTIVE'
    );
    """)
    conn.commit()

    # Seed Master Properties & Room Types
    cur.execute("SELECT COUNT(*) FROM Hotels")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO Hotels (hotel_name, city, star_rating) VALUES (?, ?, ?)", [
            ("ITC Kakatiya Luxury", "Hyderabad", 5),
            ("Novotel Varun Beach", "Visakhapatnam", 5),
            ("Grand Kakinada Residency", "Kakinada", 4)
        ])
        cur.executemany("INSERT INTO Room_Types (type_name, base_price_per_night, hourly_rate, max_occupancy) VALUES (?, ?, ?, ?)", [
            ("Standard Deluxe", 3200.0, 400.0, 2),
            ("Executive Suite", 6000.0, 750.0, 3),
            ("Presidential Villa", 12500.0, 1600.0, 4)
        ])
        cur.executemany("INSERT INTO Rooms (hotel_id, room_type_id, room_number, room_status) VALUES (?, ?, ?, ?)", [
            (1, 1, "101", "AVAILABLE"), (1, 2, "201", "AVAILABLE"), (1, 3, "301", "AVAILABLE"),
            (2, 1, "102", "AVAILABLE"), (2, 2, "202", "AVAILABLE"),
            (3, 1, "103", "AVAILABLE"), (3, 2, "203", "OCCUPIED")
        ])
        conn.commit()

    # Ingest Seed Profiles from Kaggle Export 'DBMS data set.xlsx'
    cur.execute("SELECT COUNT(*) FROM Guests")
    if cur.fetchone()[0] == 0:
        if os.path.exists("DBMS data set.xlsx"):
            try:
                df = pd.read_excel("DBMS data set.xlsx")
                for idx, r in df.iterrows():
                    cur.execute("INSERT OR IGNORE INTO Guests (name, email, phone, credit_card) VALUES (?, ?, ?, ?)",
                                (str(r.get('name', f'Guest {idx+1}')),
                                 str(r.get('email', f'guest{idx+1}@staysync.com')),
                                 str(r.get('phone-number', '9848022338')),
                                 str(r.get('credit_card', '************1234'))))
                conn.commit()
            except Exception:
                pass
    return conn

conn = setup_database()

# ==========================================
# 3. LEFT SIDEBAR NAVIGATION (100% VISIBLE)
# ==========================================
with st.sidebar:
    st.markdown("""
        <div style="padding-bottom: 12px; margin-bottom: 20px; border-bottom: 1px solid #1E293B;">
            <div style="font-size: 22px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;">
                ⚡ StaySync <span style="color: #00B4D8;">Enterprise</span>
            </div>
            <div style="font-size: 12px; color: #94A3B8; margin-top: 3px;">
                DBMS Capstone Review-2 Engine
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size: 11px; font-weight: 700; color: #00B4D8; text-transform: uppercase; letter-spacing: 1px;'>Navigation Modules</p>", unsafe_allow_html=True)

    nav_option = st.radio(
        label="Select View",
        options=[
            "Executive Dashboard",
            "Micro-Stay & Nightly Booking",
            "P2P Resale Marketplace",
            "3NF Database Explorer",
            "Spot SQL Console"
        ],
        label_visibility="collapsed"
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background-color: #1C2541; border: 1px solid #334155; border-radius: 8px; padding: 14px; font-size: 12px; line-height: 1.6;">
            <b>Status:</b> <span style="color: #10B981; font-weight: 700;">ONLINE (3NF)</span><br>
            <b>Engine:</b> SQLite Live In-Memory<br>
            <b>Dept:</b> Aditya University CSE
        </div>
    """, unsafe_allow_html=True)

# Top Header Bar
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 12px; margin-bottom: 22px; border-bottom: 1px solid #1E293B;">
        <div class="brand-title">
            ⚡ StaySync <span class="brand-highlight">{nav_option}</span>
        </div>
        <div style="font-size: 13px; color: #94A3B8;">
            Department of Computer Science & Engineering
        </div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 4. VIEW 1: EXECUTIVE DASHBOARD
# ==========================================
if nav_option == "Executive Dashboard":
    total_hotels = pd.read_sql("SELECT COUNT(*) AS c FROM Hotels", conn)['c'][0]
    total_rooms = pd.read_sql("SELECT COUNT(*) AS c FROM Rooms", conn)['c'][0]
    avail_rooms = pd.read_sql("SELECT COUNT(*) AS c FROM Rooms WHERE room_status = 'AVAILABLE'", conn)['c'][0]
    active_resales = pd.read_sql("SELECT COUNT(*) AS c FROM Reservation_Resale WHERE resale_status = 'ACTIVE'", conn)['c'][0]

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-box"><div class="metric-label">Properties Registered</div><div class="metric-number">{total_hotels}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-box"><div class="metric-label">Total Inventory</div><div class="metric-number">{total_rooms} Units</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-box"><div class="metric-label">Available Vacant</div><div class="metric-number" style="color: #10B981;">{avail_rooms} Units</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-box"><div class="metric-label">Active P2P Resales</div><div class="metric-number" style="color: #00B4D8;">{active_resales} Listings</div></div>', unsafe_allow_html=True)

    st.markdown("""
        <div class="disclaimer-card">
            <b>💡 Core System Value Proposition:</b> StaySync decouples rigid 24-hr check-in constraints through dynamic <b>Micro-Stay hourly pricing</b>, while eliminating 100% financial penalty on cancellations via an automated <b>Secondary P2P Resale Ledger</b>.
        </div>
    """, unsafe_allow_html=True)

    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("""
            <div class="info-card-box">
                <div class="card-title-text">Micro-Stay Engine Architecture</div>
                <div class="card-body-text">
                    Decoupled pricing tables calculate discrete multi-hour windows (3, 6, 12 hrs) referencing <code>Room_Types.hourly_rate</code>, bypassing conventional 12 PM to 12 PM fixed occupancy constraints.
                </div>
            </div>
        """, unsafe_allow_html=True)
    with c_right:
        st.markdown("""
            <div class="info-card-box">
                <div class="card-title-text">Secondary Resale Market Constraint</div>
                <div class="card-body-text">
                    Enforces database-level constraint <code>CHECK (discounted_price &lt; original_price)</code> to ensure buyers receive discount incentives while sellers recover liquidity from non-refundable bookings.
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.subheader("Operational Inventory Matrix")
    inv_df = pd.read_sql("""
        SELECT h.hotel_name AS 'Hotel Property', h.city AS 'Location', r.room_number AS 'Room Number',
               rt.type_name AS 'Tier Category', rt.base_price_per_night AS 'Daily Tariff (INR)',
               rt.hourly_rate AS 'Hourly Tariff (INR)', r.room_status AS 'Live Status'
        FROM Rooms r
        JOIN Hotels h ON r.hotel_id = h.hotel_id
        JOIN Room_Types rt ON r.room_type_id = rt.room_type_id
    """, conn)
    st.dataframe(inv_df, use_container_width=True)

# ==========================================
# 5. VIEW 2: MICRO-STAY & NIGHTLY BOOKING
# ==========================================
elif nav_option == "Micro-Stay & Nightly Booking":
    st.caption("Demonstrating dynamic rate calculation and atomic ACID reservation transactions.")

    g_df = pd.read_sql("SELECT guest_id, name, email FROM Guests LIMIT 25", conn)
    h_df = pd.read_sql("SELECT hotel_id, hotel_name, city FROM Hotels", conn)

    g_map = {f"{r['name']} ({r['email']})": r['guest_id'] for _, r in g_df.iterrows()}
    h_map = {f"{r['hotel_name']} - {r['city']}": r['hotel_id'] for _, r in h_df.iterrows()}

    b_col1, b_col2 = st.columns(2)

    with b_col1:
        st.markdown("#### 1. Target Allocation")
        selected_guest_str = st.selectbox("Select Certified Guest Profile", list(g_map.keys()))
        selected_hotel_str = st.selectbox("Select Target Property", list(h_map.keys()))
        chosen_hotel_id = h_map[selected_hotel_str]

        vacant_units = pd.read_sql(f"""
            SELECT r.room_id, r.room_number, rt.type_name, rt.base_price_per_night, rt.hourly_rate
            FROM Rooms r
            JOIN Room_Types rt ON r.room_type_id = rt.room_type_id
            WHERE r.hotel_id = {chosen_hotel_id} AND r.room_status = 'AVAILABLE'
        """, conn)

        if vacant_units.empty:
            st.error("Zero vacant units currently available in this property.")
            active_unit_data = None
        else:
            unit_map = {
                f"Unit {row['room_number']} — {row['type_name']} (Nightly: INR {row['base_price_per_night']}, Hourly: INR {row['hourly_rate']})":
                (row['room_id'], row['base_price_per_night'], row['hourly_rate'])
                for _, row in vacant_units.iterrows()
            }
            selected_unit_str = st.selectbox("Select Available Room", list(unit_map.keys()))
            active_unit_data = unit_map[selected_unit_str]

    with b_col2:
        if active_unit_data:
            st.markdown("#### 2. Pricing & Slot Configuration")
            unit_pk, daily_rate, hourly_rate = active_unit_data
            booking_strategy = st.radio("Occupancy Mode", ["MICRO_STAY (Hourly Allocation)", "NIGHTLY (Full Day Allocation)"], horizontal=True)

            if "MICRO_STAY" in booking_strategy:
                duration_hrs = st.slider("Duration (Hours)", 2, 12, 4)
                total_computed = duration_hrs * hourly_rate
                c_in_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                c_out_time = (datetime.datetime.now() + datetime.timedelta(hours=duration_hrs)).strftime("%Y-%m-%d %H:%M")
                strategy_type = "MICRO_STAY"

                st.markdown(f"""
                    <div class="info-card-box">
                        <div class="card-title-text">Computed Micro-Stay Fare</div>
                        <div style="font-size: 26px; font-weight: 800; color: #00B4D8;">INR {total_computed:.2f}</div>
                        <div style="color: #94A3B8; font-size: 13px; margin-top: 4px;">Rate applied: INR {hourly_rate}/hr for {duration_hrs} contiguous hours</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                night_units = st.number_input("Duration (Nights)", 1, 14, 1)
                total_computed = night_units * daily_rate
                c_in_time = datetime.datetime.now().strftime("%Y-%m-%d 12:00")
                c_out_time = (datetime.datetime.now() + datetime.timedelta(days=int(night_units))).strftime("%Y-%m-%d 11:00")
                strategy_type = "NIGHTLY"

                st.markdown(f"""
                    <div class="info-card-box">
                        <div class="card-title-text">Computed Nightly Tariff</div>
                        <div style="font-size: 26px; font-weight: 800; color: #00B4D8;">INR {total_computed:.2f}</div>
                        <div style="color: #94A3B8; font-size: 13px; margin-top: 4px;">Rate applied: INR {daily_rate}/night for {night_units} night(s)</div>
                    </div>
                """, unsafe_allow_html=True)

            if st.button("Commit ACID Reservation Transaction", use_container_width=True):
                cur = conn.cursor()
                guest_pk = g_map[selected_guest_str]
                cur.execute("""
                    INSERT INTO Reservations (guest_id, hotel_id, room_id, booking_type, check_in, check_out, total_amount, booking_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'CONFIRMED')
                """, (guest_pk, chosen_hotel_id, unit_pk, strategy_type, c_in_time, c_out_time, total_computed))
                cur.execute("UPDATE Rooms SET room_status = 'OCCUPIED' WHERE room_id = ?", (unit_pk,))
                conn.commit()
                st.success(f"Transaction Committed! Record ID #{cur.lastrowid} written to database. Room updated to OCCUPIED.")
                st.rerun()

# ==========================================
# 6. VIEW 3: P2P RESALE MARKETPLACE
# ==========================================
elif nav_option == "P2P Resale Marketplace":
    st.caption("Preventing 100% cancellation losses by reselling non-refundable bookings to secondary buyers.")

    resale_view_tab1, resale_view_tab2 = st.tabs(["Active Secondary Market Listings", "List Confirmed Booking for Resale"])

    with resale_view_tab1:
        resales = pd.read_sql("""
            SELECT rr.resale_id, rr.booking_id, g.name AS seller, h.hotel_name,
                   r.booking_type, r.check_in, rr.original_price, rr.discounted_price, rr.resale_status
            FROM Reservation_Resale rr
            JOIN Reservations r ON rr.booking_id = r.booking_id
            JOIN Guests g ON rr.original_guest_id = g.guest_id
            JOIN Hotels h ON r.hotel_id = h.hotel_id
            WHERE rr.resale_status = 'ACTIVE'
        """, conn)

        if resales.empty:
            st.info("No active resales listed in the ledger. You can list a confirmed booking using the next tab.")
        else:
            for _, item in resales.iterrows():
                savings = item['original_price'] - item['discounted_price']
                discount_pct = (savings / item['original_price']) * 100

                st.markdown(f"""
                    <div class="resale-listing-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <b style="font-size: 16px; color: #FFFFFF;">{item['hotel_name']}</b>
                                <span style="color: #94A3B8; font-size: 13px;">({item['booking_type']})</span><br>
                                <span style="color: #64748B; font-size: 13px;">Original Seller: {item['seller']} | Arrival Slot: {item['check_in']}</span>
                            </div>
                            <div style="text-align: right;">
                                <span style="font-size: 22px; font-weight: 800; color: #00B4D8;">INR {item['discounted_price']:.2f}</span><br>
                                <span style="color: #10B981; font-size: 12px; font-weight: 600;">Original: INR {item['original_price']:.2f} (-{discount_pct:.0f}% OFF)</span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if st.button(f"Acquire Resale Booking #{item['resale_id']}", key=f"buy_btn_{item['resale_id']}"):
                    cur = conn.cursor()
                    cur.execute("UPDATE Reservation_Resale SET resale_status = 'SOLD' WHERE resale_id = ?", (item['resale_id'],))
                    conn.commit()
                    st.success("Ownership transfer committed! Listing status marked SOLD.")
                    st.rerun()

    with resale_view_tab2:
        confirmed_eligible = pd.read_sql("""
            SELECT r.booking_id, g.name, h.hotel_name, r.total_amount, r.guest_id
            FROM Reservations r
            JOIN Guests g ON r.guest_id = g.guest_id
            JOIN Hotels h ON r.hotel_id = h.hotel_id
            WHERE r.booking_status = 'CONFIRMED'
            AND r.booking_id NOT IN (SELECT booking_id FROM Reservation_Resale)
        """, conn)

        if confirmed_eligible.empty:
            st.warning("No eligible unlisted bookings found. Complete a reservation in Module 2 first.")
        else:
            elig_dict = {
                f"Booking #{r['booking_id']} — {r['name']} at {r['hotel_name']} (Paid: INR {r['total_amount']})":
                (r['booking_id'], r['total_amount'], r['guest_id'])
                for _, r in confirmed_eligible.iterrows()
            }
            chosen_resale_key = st.selectbox("Select Confirmed Reservation", list(elig_dict.keys()))
            b_pk, orig_tariff, s_pk = elig_dict[chosen_resale_key]

            st.write(f"Original Settlement Tariff: **INR {orig_tariff:.2f}**")
            resale_price = st.number_input(
                "Secondary Market Listing Price (INR) — Must be lower than original tariff",
                min_value=100.0,
                max_value=float(orig_tariff - 1.0),
                value=float(orig_tariff * 0.8),
                step=50.0
            )

            if st.button("Publish Listing to Secondary Marketplace"):
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO Reservation_Resale (booking_id, original_guest_id, original_price, discounted_price, resale_status)
                    VALUES (?, ?, ?, ?, 'ACTIVE')
                """, (b_pk, s_pk, orig_tariff, resale_price))
                conn.commit()
                st.success("Listing published successfully with relational integrity constraint validated.")
                st.rerun()

# ==========================================
# 7. VIEW 4: 3NF DATABASE EXPLORER
# ==========================================
elif nav_option == "3NF Database Explorer":
    st.caption("Inspect raw relational tables and schema integrity constraints directly from SQLite engine.")

    chosen_table = st.selectbox("Select Target Relation", ["Guests", "Hotels", "Room_Types", "Rooms", "Reservations", "Reservation_Resale"])
    table_df = pd.read_sql(f"SELECT * FROM {chosen_table}", conn)

    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin: 14px 0;">
            <div style="color: #94A3B8; font-size: 13px;">Displaying committed physical records in table <b>{chosen_table}</b></div>
            <div style="color: #FFC107; font-size: 14px; font-weight: 700;">Total Records: {len(table_df)}</div>
        </div>
    """, unsafe_allow_html=True)
    st.dataframe(table_df, use_container_width=True)

# ==========================================
# 8. VIEW 5: SPOT SQL CONSOLE
# ==========================================
elif nav_option == "Spot SQL Console":
    st.caption("Directly execute SQL DQL/DML against the live in-memory database during faculty Viva questioning.")

    sample_queries = [
        "SELECT * FROM Rooms WHERE room_status = 'AVAILABLE';",
        "SELECT g.name, h.hotel_name, r.booking_type, r.total_amount FROM Reservations r JOIN Guests g ON r.guest_id = g.guest_id JOIN Hotels h ON r.hotel_id = h.hotel_id;",
        "SELECT room_type_id, type_name, hourly_rate, base_price_per_night FROM Room_Types;",
        "SELECT * FROM Reservation_Resale WHERE resale_status = 'ACTIVE';",
        "SELECT h.hotel_name, COUNT(r.booking_id) AS total_bookings FROM Hotels h LEFT JOIN Reservations r ON h.hotel_id = r.hotel_id GROUP BY h.hotel_id;"
    ]

    selected_query_preset = st.selectbox("Select Query Presets (or write custom SQL query below):", sample_queries)
    custom_sql = st.text_area("SQL Statement Editor", value=selected_query_preset, height=110)

    if st.button("Execute SQL Query", use_container_width=True):
        try:
            query_output = pd.read_sql(custom_sql, conn)
            st.success(f"Execution Successful! Total Records Returned: {len(query_output)}")
            st.dataframe(query_output, use_container_width=True)
        except Exception as err:
            st.error(f"SQL Parser Exception: {err}")



