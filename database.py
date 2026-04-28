import sqlite3
import os

DB_NAME = "travelbot.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Table for Holiday Packages
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS holiday_packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            destination TEXT NOT NULL,
            duration TEXT,
            price REAL,
            description TEXT,
            category TEXT
        )
    ''')

    # Table for Hotels
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hotels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            star_rating INTEGER,
            price_per_night REAL,
            amenities TEXT
        )
    ''')

    # Table for Destinations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS destinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            attractions TEXT,
            climate TEXT,
            best_time TEXT
        )
    ''')

    # Table for Learned Responses (ML Component)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learned_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            confidence REAL DEFAULT 1.0,
            upvotes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table for Users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table for Chat History
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Seed Data
    cursor.execute("SELECT COUNT(*) FROM holiday_packages")
    if cursor.fetchone()[0] == 0:
        packages = [
            ('Sigiriya Heritage Tour', 'Sigiriya', '3 Days', 250.0, 'Explore the ancient rock fortress and surrounding temples.', 'Cultural'),
            ('Ella Adventure Trip', 'Ella', '4 Days', 180.0, 'Hiking, tea plantations, and scenic train rides.', 'Adventure'),
            ('Bentota Beach Escape', 'Bentota', '5 Days', 350.0, 'Relaxing stay by the beach with water sports.', 'Relaxation'),
            ('Kandy Temple Visit', 'Kandy', '2 Days', 120.0, 'Visit the Temple of the Tooth and botanical gardens.', 'Cultural'),
            ('Yala Safari Quest', 'Yala', '3 Days', 220.0, 'Wildlife safari to see leopards and elephants.', 'Wildlife')
        ]
        cursor.executemany('INSERT INTO holiday_packages (name, destination, duration, price, description, category) VALUES (?,?,?,?,?,?)', packages)

    cursor.execute("SELECT COUNT(*) FROM hotels")
    if cursor.fetchone()[0] == 0:
        hotels = [
            ('Cinnamon Grand', 'Colombo', 5, 150.0, 'Pool, Spa, Multiple Restaurants'),
            ('98 Acres Resort', 'Ella', 5, 200.0, 'Mountain View, Eco-friendly, Spa'),
            ('Jetwing Lighthouse', 'Galle', 5, 180.0, 'Beachfront, Architecture, Fine Dining'),
            ('Heritance Kandalama', 'Dambulla', 5, 190.0, 'Eco-design, Lake View, Wildlife'),
            ('Earls Regency', 'Kandy', 5, 130.0, 'Luxury, River View, Gym')
        ]
        cursor.executemany('INSERT INTO hotels (name, location, star_rating, price_per_night, amenities) VALUES (?,?,?,?,?)', hotels)

    cursor.execute("SELECT COUNT(*) FROM destinations")
    if cursor.fetchone()[0] == 0:
        destinations = [
            ('Ella', 'Little Adams Peak, Nine Arch Bridge', 'Cool & Misty', 'January to April'),
            ('Galle', 'Galle Fort, Unawatuna Beach', 'Tropical', 'December to April'),
            ('Nuwara Eliya', 'Gregory Lake, Tea Factories', 'Cold', 'April to June'),
            ('Arugam Bay', 'Surfing Points', 'Dry & Sunny', 'May to September'),
            ('Anuradhapura', 'Ancient Ruins, Stupas', 'Dry', 'July to September'),
            ('Kandy', 'Temple of the Tooth, Peradeniya Gardens', 'Mild', 'December to April'),
            ('Jaffna', 'Nallur Kandaswamy Kovil, Jaffna Fort', 'Dry & Hot', 'January to March'),
            ('Colombo', 'Galle Face Green, Gangaramaya Temple', 'Humid', 'January to March'),
            ('Matale', 'Aluvihare Rock Temple, Spice Gardens', 'Tropical', 'Throughout the year'),
            ('Ratnapura', 'Gem Museums, Adam\'s Peak access', 'Wet', 'January to March')
        ]
        cursor.executemany('INSERT INTO destinations (name, attractions, climate, best_time) VALUES (?,?,?,?)', destinations)

    conn.commit()
    conn.close()

def query_packages(destination=None):
    conn = get_connection()
    cursor = conn.cursor()
    if destination:
        cursor.execute("SELECT * FROM holiday_packages WHERE destination LIKE ?", (f'%{destination}%',))
    else:
        cursor.execute("SELECT * FROM holiday_packages")
    results = cursor.fetchall()
    conn.close()
    return results

def query_hotels(location=None):
    conn = get_connection()
    cursor = conn.cursor()
    if location:
        cursor.execute("SELECT * FROM hotels WHERE location LIKE ?", (f'%{location}%',))
    else:
        cursor.execute("SELECT * FROM hotels")
    results = cursor.fetchall()
    conn.close()
    return results

def query_destinations(name=None):
    conn = get_connection()
    cursor = conn.cursor()
    if name:
        cursor.execute("SELECT * FROM destinations WHERE name LIKE ?", (f'%{name}%',))
    else:
        cursor.execute("SELECT * FROM destinations")
    results = cursor.fetchall()
    conn.close()
    return results

def save_learned_response(user_input, bot_response):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO learned_responses (user_input, bot_response) VALUES (?, ?)", (user_input, bot_response))
    conn.commit()
    conn.close()

def get_learned_responses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_input, bot_response FROM learned_responses")
    results = cursor.fetchall()
    conn.close()
    return results

def create_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))
    conn.commit()
    conn.close()

def get_user(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def save_chat_message(email, role, content):
    """Saves a single chat message to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (user_email, role, content) VALUES (?, ?, ?)", (email, role, content))
    conn.commit()
    conn.close()

def get_chat_history(email):
    """Retrieves all chat messages for a specific user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM chat_history WHERE user_email = ? ORDER BY timestamp ASC", (email,))
    history = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
    conn.close()
    return history

def clear_chat_history(email):
    """Deletes all chat messages for a specific user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE user_email = ?", (email,))
    conn.commit()
    conn.close()

# Initialize the database automatically when this module is imported
initialize_db()

if __name__ == "__main__":
    print("Database initialized and seeded.")
