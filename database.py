import sqlite3
import json
from datetime import datetime
import os

DB_PATH = "jeeptrack.db"

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            license_number TEXT NOT NULL UNIQUE,
            license_plate TEXT NOT NULL UNIQUE,
            route TEXT NOT NULL,
            max_capacity INTEGER NOT NULL,
            current_capacity INTEGER DEFAULT 0,
            photo BLOB,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_trips INTEGER DEFAULT 0,
            total_distance REAL DEFAULT 0.0,
            average_rating REAL DEFAULT 0.0,
            total_ratings INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commuters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            email TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id INTEGER NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            start_lat REAL NOT NULL,
            start_lon REAL NOT NULL,
            end_lat REAL,
            end_lon REAL,
            distance REAL DEFAULT 0.0,
            passengers INTEGER DEFAULT 0,
            route TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (driver_id) REFERENCES drivers(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id INTEGER NOT NULL,
            commuter_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            comment TEXT,
            review_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (driver_id) REFERENCES drivers(id),
            FOREIGN KEY (commuter_id) REFERENCES commuters(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS location_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id INTEGER NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (driver_id) REFERENCES drivers(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_driver(driver_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO drivers (
                first_name, last_name, contact_number, license_number, 
                license_plate, route, max_capacity, current_capacity,
                photo, latitude, longitude
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            driver_data['first_name'],
            driver_data['last_name'],
            driver_data['contact_number'],
            driver_data['license_number'],
            driver_data['license_plate'],
            driver_data['route'],
            driver_data['max_capacity'],
            driver_data.get('current_capacity', 0),
            driver_data['photo'],
            driver_data['location'][0],
            driver_data['location'][1]
        ))
        conn.commit()
        driver_id = cursor.lastrowid
        conn.close()
        return driver_id
    except sqlite3.IntegrityError as e:
        conn.close()
        return None

def add_commuter(commuter_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO commuters (
            first_name, last_name, contact_number, email,
            latitude, longitude
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        commuter_data['first_name'],
        commuter_data['last_name'],
        commuter_data['contact_number'],
        commuter_data.get('email', ''),
        commuter_data['location'][0],
        commuter_data['location'][1]
    ))
    conn.commit()
    commuter_id = cursor.lastrowid
    conn.close()
    return commuter_id

def get_all_drivers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM drivers')
    rows = cursor.fetchall()
    conn.close()
    
    drivers = []
    for row in rows:
        drivers.append({
            'id': row[0],
            'first_name': row[1],
            'last_name': row[2],
            'contact_number': row[3],
            'license_number': row[4],
            'license_plate': row[5],
            'route': row[6],
            'max_capacity': row[7],
            'current_capacity': row[8],
            'photo': row[9],
            'location': [row[10], row[11]],
            'registration_time': row[12],
            'total_trips': row[13],
            'total_distance': row[14],
            'average_rating': row[15],
            'total_ratings': row[16]
        })
    return drivers

def get_driver_by_license(license_plate):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM drivers WHERE license_plate = ?', (license_plate,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'first_name': row[1],
            'last_name': row[2],
            'contact_number': row[3],
            'license_number': row[4],
            'license_plate': row[5],
            'route': row[6],
            'max_capacity': row[7],
            'current_capacity': row[8],
            'photo': row[9],
            'location': [row[10], row[11]],
            'registration_time': row[12],
            'total_trips': row[13],
            'total_distance': row[14],
            'average_rating': row[15],
            'total_ratings': row[16]
        }
    return None

def update_driver_location(driver_id, lat, lon):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE drivers SET latitude = ?, longitude = ? WHERE id = ?
    ''', (lat, lon, driver_id))
    
    cursor.execute('''
        INSERT INTO location_updates (driver_id, latitude, longitude)
        VALUES (?, ?, ?)
    ''', (driver_id, lat, lon))
    
    conn.commit()
    conn.close()

def update_driver_capacity(driver_id, capacity):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE drivers SET current_capacity = ? WHERE id = ?
    ''', (capacity, driver_id))
    
    conn.commit()
    conn.close()

def start_trip(driver_id, start_lat, start_lon, route):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO trips (driver_id, start_time, start_lat, start_lon, route, status)
        VALUES (?, ?, ?, ?, ?, 'active')
    ''', (driver_id, datetime.now(), start_lat, start_lon, route))
    
    conn.commit()
    trip_id = cursor.lastrowid
    conn.close()
    return trip_id

def end_trip(trip_id, end_lat, end_lon, distance, passengers):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE trips 
        SET end_time = ?, end_lat = ?, end_lon = ?, distance = ?, passengers = ?, status = 'completed'
        WHERE id = ?
    ''', (datetime.now(), end_lat, end_lon, distance, passengers, trip_id))
    
    cursor.execute('SELECT driver_id FROM trips WHERE id = ?', (trip_id,))
    driver_id = cursor.fetchone()[0]
    
    cursor.execute('''
        UPDATE drivers 
        SET total_trips = total_trips + 1, total_distance = total_distance + ?
        WHERE id = ?
    ''', (distance, driver_id))
    
    conn.commit()
    conn.close()

def get_driver_trips(driver_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM trips WHERE driver_id = ? ORDER BY start_time DESC
    ''', (driver_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    trips = []
    for row in rows:
        trips.append({
            'id': row[0],
            'driver_id': row[1],
            'start_time': row[2],
            'end_time': row[3],
            'start_lat': row[4],
            'start_lon': row[5],
            'end_lat': row[6],
            'end_lon': row[7],
            'distance': row[8],
            'passengers': row[9],
            'route': row[10],
            'status': row[11]
        })
    return trips

def add_review(driver_id, commuter_id, rating, comment):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO reviews (driver_id, commuter_id, rating, comment)
        VALUES (?, ?, ?, ?)
    ''', (driver_id, commuter_id, rating, comment))
    
    cursor.execute('''
        SELECT AVG(rating), COUNT(*) FROM reviews WHERE driver_id = ?
    ''', (driver_id,))
    avg_rating, total_ratings = cursor.fetchone()
    
    cursor.execute('''
        UPDATE drivers SET average_rating = ?, total_ratings = ? WHERE id = ?
    ''', (avg_rating, total_ratings, driver_id))
    
    conn.commit()
    conn.close()

def get_driver_reviews(driver_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT r.*, c.first_name, c.last_name 
        FROM reviews r
        JOIN commuters c ON r.commuter_id = c.id
        WHERE r.driver_id = ?
        ORDER BY r.review_time DESC
    ''', (driver_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    reviews = []
    for row in rows:
        reviews.append({
            'id': row[0],
            'driver_id': row[1],
            'commuter_id': row[2],
            'rating': row[3],
            'comment': row[4],
            'review_time': row[5],
            'commuter_name': f"{row[6]} {row[7]}"
        })
    return reviews

def get_commuter_by_contact(contact_number):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM commuters WHERE contact_number = ?', (contact_number,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'first_name': row[1],
            'last_name': row[2],
            'contact_number': row[3],
            'email': row[4],
            'location': [row[5], row[6]],
            'registration_time': row[7]
        }
    return None
