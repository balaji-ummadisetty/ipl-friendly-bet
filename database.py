import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.environ.get('DB_PATH', 'ipl_betting.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            balance REAL DEFAULT 0
        )
    ''')
    
    # Matches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_date TEXT NOT NULL,
            day TEXT NOT NULL,
            time TEXT NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            venue TEXT NOT NULL,
            status TEXT DEFAULT 'upcoming',
            winner TEXT
        )
    ''')
    
    # Predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            match_id INTEGER NOT NULL,
            predicted_team TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (match_id) REFERENCES matches (id),
            UNIQUE(user_id, match_id)
        )
    ''')
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            match_id INTEGER,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (match_id) REFERENCES matches (id)
        )
    ''')
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Add default admin if not exists
    if not get_user('admin'):
        add_user('admin', 'admin123', 'admin')

    # Add default members if not exists
    default_members = [
        ('shashi', 'shashi123'),
        ('balaji', 'balaji123'),
        ('purab', 'purab123'),
        ('santhosh', 'santhosh123'),
        ('sandesh', 'sandesh123'),
        ('ganesh', 'ganesh123'),
        ('manikanta', 'manikanta123'),
        ('surya', 'surya123'),
        ('vamshi', 'vamshi123'),
        ('koushal', 'koushal123'),
    ]
    for username, password in default_members:
        if not get_user(username):
            add_user(username, password, 'member')
    
    # Add default settings
    if not get_setting('invest_amount'):
        set_setting('invest_amount', '10')
    if not get_setting('prediction_open_hours'):
        set_setting('prediction_open_hours', '24')

def insert_matches():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM matches')
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    conn.close()
    matches_data = [
        {'date': '28-Mar-26', 'day': 'Sat', 'time': '7:30 PM', 'home': 'Sunrisers Hyderabad', 'away': 'Royal Challengers Bengaluru', 'venue': 'Bengaluru'},
        {'date': '29-Mar-26', 'day': 'Sun', 'time': '7:30 PM', 'home': 'Kolkata Knight Riders', 'away': 'Mumbai Indians', 'venue': 'Mumbai'},
        {'date': '30-Mar-26', 'day': 'Mon', 'time': '7:30 PM', 'home': 'Chennai Super Kings', 'away': 'Rajasthan Royals', 'venue': 'Guwahati'},
        {'date': '31-Mar-26', 'day': 'Tue', 'time': '7:30 PM', 'home': 'Gujarat Titans', 'away': 'Punjab Kings', 'venue': 'New Chandigarh'},
        {'date': '01-Apr-26', 'day': 'Wed', 'time': '7:30 PM', 'home': 'Delhi Capitals', 'away': 'Lucknow Super Giants', 'venue': 'Lucknow'},
        {'date': '02-Apr-26', 'day': 'Thu', 'time': '7:30 PM', 'home': 'Sunrisers Hyderabad', 'away': 'Kolkata Knight Riders', 'venue': 'Kolkata'},
        {'date': '03-Apr-26', 'day': 'Fri', 'time': '7:30 PM', 'home': 'Punjab Kings', 'away': 'Chennai Super Kings', 'venue': 'Chennai'},
        {'date': '04-Apr-26', 'day': 'Sat', 'time': '3:30 PM', 'home': 'Mumbai Indians', 'away': 'Delhi Capitals', 'venue': 'Delhi'},
        {'date': '04-Apr-26', 'day': 'Sat', 'time': '7:30 PM', 'home': 'Rajasthan Royals', 'away': 'Gujarat Titans', 'venue': 'Ahmedabad'},
        {'date': '05-Apr-26', 'day': 'Sun', 'time': '3:30 PM', 'home': 'Lucknow Super Giants', 'away': 'Sunrisers Hyderabad', 'venue': 'Hyderabad'},
        {'date': '05-Apr-26', 'day': 'Sun', 'time': '7:30 PM', 'home': 'Chennai Super Kings', 'away': 'Royal Challengers Bengaluru', 'venue': 'Bengaluru'},
        {'date': '06-Apr-26', 'day': 'Mon', 'time': '7:30 PM', 'home': 'Punjab Kings', 'away': 'Kolkata Knight Riders', 'venue': 'Kolkata'},
        {'date': '07-Apr-26', 'day': 'Tue', 'time': '7:30 PM', 'home': 'Mumbai Indians', 'away': 'Rajasthan Royals', 'venue': 'Guwahati'},
        {'date': '08-Apr-26', 'day': 'Wed', 'time': '7:30 PM', 'home': 'Gujarat Titans', 'away': 'Delhi Capitals', 'venue': 'Delhi'},
        {'date': '09-Apr-26', 'day': 'Thu', 'time': '7:30 PM', 'home': 'Lucknow Super Giants', 'away': 'Kolkata Knight Riders', 'venue': 'Kolkata'},
        {'date': '10-Apr-26', 'day': 'Fri', 'time': '7:30 PM', 'home': 'Royal Challengers Bengaluru', 'away': 'Rajasthan Royals', 'venue': 'Guwahati'},
        {'date': '11-Apr-26', 'day': 'Sat', 'time': '3:30 PM', 'home': 'Sunrisers Hyderabad', 'away': 'Punjab Kings', 'venue': 'New Chandigarh'},
        {'date': '11-Apr-26', 'day': 'Sat', 'time': '7:30 PM', 'home': 'Delhi Capitals', 'away': 'Chennai Super Kings', 'venue': 'Chennai'},
        {'date': '12-Apr-26', 'day': 'Sun', 'time': '3:30 PM', 'home': 'Gujarat Titans', 'away': 'Lucknow Super Giants', 'venue': 'Lucknow'},
        {'date': '12-Apr-26', 'day': 'Sun', 'time': '7:30 PM', 'home': 'Royal Challengers Bengaluru', 'away': 'Mumbai Indians', 'venue': 'Mumbai'},
        {'date': '13-Apr-26', 'day': 'Mon', 'time': '7:30 PM', 'home': 'Rajasthan Royals', 'away': 'Sunrisers Hyderabad', 'venue': 'Hyderabad'},
        {'date': '14-Apr-26', 'day': 'Tue', 'time': '7:30 PM', 'home': 'Kolkata Knight Riders', 'away': 'Chennai Super Kings', 'venue': 'Chennai'},
        {'date': '15-Apr-26', 'day': 'Wed', 'time': '7:30 PM', 'home': 'Lucknow Super Giants', 'away': 'Royal Challengers Bengaluru', 'venue': 'Bengaluru'},
        {'date': '16-Apr-26', 'day': 'Thu', 'time': '7:30 PM', 'home': 'Punjab Kings', 'away': 'Mumbai Indians', 'venue': 'Mumbai'},
        {'date': '17-Apr-26', 'day': 'Fri', 'time': '7:30 PM', 'home': 'Kolkata Knight Riders', 'away': 'Gujarat Titans', 'venue': 'Ahmedabad'},
        {'date': '18-Apr-26', 'day': 'Sat', 'time': '3:30 PM', 'home': 'Delhi Capitals', 'away': 'Royal Challengers Bengaluru', 'venue': 'Bengaluru'},
        {'date': '18-Apr-26', 'day': 'Sat', 'time': '7:30 PM', 'home': 'Chennai Super Kings', 'away': 'Sunrisers Hyderabad', 'venue': 'Hyderabad'},
        {'date': '19-Apr-26', 'day': 'Sun', 'time': '3:30 PM', 'home': 'Rajasthan Royals', 'away': 'Kolkata Knight Riders', 'venue': 'Kolkata'},
        {'date': '19-Apr-26', 'day': 'Sun', 'time': '7:30 PM', 'home': 'Lucknow Super Giants', 'away': 'Punjab Kings', 'venue': 'New Chandigarh'},
        {'date': '20-Apr-26', 'day': 'Mon', 'time': '7:30 PM', 'home': 'Mumbai Indians', 'away': 'Gujarat Titans', 'venue': 'Ahmedabad'},
        {'date': '21-Apr-26', 'day': 'Tue', 'time': '7:30 PM', 'home': 'Delhi Capitals', 'away': 'Sunrisers Hyderabad', 'venue': 'Hyderabad'},
        {'date': '22-Apr-26', 'day': 'Wed', 'time': '7:30 PM', 'home': 'Rajasthan Royals', 'away': 'Lucknow Super Giants', 'venue': 'Lucknow'},
        {'date': '23-Apr-26', 'day': 'Thu', 'time': '7:30 PM', 'home': 'Chennai Super Kings', 'away': 'Mumbai Indians', 'venue': 'Mumbai'},
        {'date': '24-Apr-26', 'day': 'Fri', 'time': '7:30 PM', 'home': 'Gujarat Titans', 'away': 'Royal Challengers Bengaluru', 'venue': 'Bengaluru'},
        {'date': '25-Apr-26', 'day': 'Sat', 'time': '3:30 PM', 'home': 'Punjab Kings', 'away': 'Delhi Capitals', 'venue': 'Delhi'},
        {'date': '25-Apr-26', 'day': 'Sat', 'time': '7:30 PM', 'home': 'Sunrisers Hyderabad', 'away': 'Rajasthan Royals', 'venue': 'Jaipur'},
        {'date': '26-Apr-26', 'day': 'Sun', 'time': '3:30 PM', 'home': 'Chennai Super Kings', 'away': 'Gujarat Titans', 'venue': 'Ahmedabad'},
        {'date': '26-Apr-26', 'day': 'Sun', 'time': '7:30 PM', 'home': 'Kolkata Knight Riders', 'away': 'Lucknow Super Giants', 'venue': 'Lucknow'},
        {'date': '27-Apr-26', 'day': 'Mon', 'time': '7:30 PM', 'home': 'Royal Challengers Bengaluru', 'away': 'Delhi Capitals', 'venue': 'Delhi'},
        {'date': '28-Apr-26', 'day': 'Tue', 'time': '7:30 PM', 'home': 'Rajasthan Royals', 'away': 'Punjab Kings', 'venue': 'New Chandigarh'},
        {'date': '29-Apr-26', 'day': 'Wed', 'time': '7:30 PM', 'home': 'Sunrisers Hyderabad', 'away': 'Mumbai Indians', 'venue': 'Mumbai'},
        {'date': '30-Apr-26', 'day': 'Thu', 'time': '7:30 PM', 'home': 'Royal Challengers Bengaluru', 'away': 'Gujarat Titans', 'venue': 'Ahmedabad'},
        {'date': '01-May-26', 'day': 'Fri', 'time': '7:30 PM', 'home': 'Delhi Capitals', 'away': 'Rajasthan Royals', 'venue': 'Jaipur'},
        {'date': '02-May-26', 'day': 'Sat', 'time': '7:30 PM', 'home': 'Mumbai Indians', 'away': 'Chennai Super Kings', 'venue': 'Chennai'},
        {'date': '03-May-26', 'day': 'Sun', 'time': '3:30 PM', 'home': 'Kolkata Knight Riders', 'away': 'Sunrisers Hyderabad', 'venue': 'Hyderabad'},
        {'date': '03-May-26', 'day': 'Sun', 'time': '7:30 PM', 'home': 'Punjab Kings', 'away': 'Gujarat Titans', 'venue': 'Ahmedabad'},
        {'date': '04-May-26', 'day': 'Mon', 'time': '7:30 PM', 'home': 'Lucknow Super Giants', 'away': 'Mumbai Indians', 'venue': 'Mumbai'},
        {'date': '05-May-26', 'day': 'Tue', 'time': '7:30 PM', 'home': 'Chennai Super Kings', 'away': 'Delhi Capitals', 'venue': 'Delhi'},
        {'date': '06-May-26', 'day': 'Wed', 'time': '7:30 PM', 'home': 'Punjab Kings', 'away': 'Sunrisers Hyderabad', 'venue': 'Hyderabad'},
        {'date': '07-May-26', 'day': 'Thu', 'time': '7:30 PM', 'home': 'Royal Challengers Bengaluru', 'away': 'Lucknow Super Giants', 'venue': 'Lucknow'},
        {'date': '08-May-26', 'day': 'Fri', 'time': '7:30 PM', 'home': 'Kolkata Knight Riders', 'away': 'Delhi Capitals', 'venue': 'Delhi'},
        {'date': '09-May-26', 'day': 'Sat', 'time': '7:30 PM', 'home': 'Gujarat Titans', 'away': 'Rajasthan Royals', 'venue': 'Jaipur'},
        {'date': '10-May-26', 'day': 'Sun', 'time': '3:30 PM', 'home': 'Lucknow Super Giants', 'away': 'Chennai Super Kings', 'venue': 'Chennai'},
        {'date': '10-May-26', 'day': 'Sun', 'time': '7:30 PM', 'home': 'Mumbai Indians', 'away': 'Royal Challengers Bengaluru', 'venue': 'Raipur'},
        {'date': '11-May-26', 'day': 'Mon', 'time': '7:30 PM', 'home': 'Delhi Capitals', 'away': 'Punjab Kings', 'venue': 'Dharamshala'},
        {'date': '12-May-26', 'day': 'Tue', 'time': '7:30 PM', 'home': 'Sunrisers Hyderabad', 'away': 'Gujarat Titans', 'venue': 'Ahmedabad'},
        {'date': '13-May-26', 'day': 'Wed', 'time': '7:30 PM', 'home': 'Kolkata Knight Riders', 'away': 'Royal Challengers Bengaluru', 'venue': 'Raipur'},
        {'date': '14-May-26', 'day': 'Thu', 'time': '7:30 PM', 'home': 'Mumbai Indians', 'away': 'Punjab Kings', 'venue': 'Dharamshala'},
        {'date': '15-May-26', 'day': 'Fri', 'time': '7:30 PM', 'home': 'Chennai Super Kings', 'away': 'Lucknow Super Giants', 'venue': 'Lucknow'},
        {'date': '16-May-26', 'day': 'Sat', 'time': '7:30 PM', 'home': 'Gujarat Titans', 'away': 'Kolkata Knight Riders', 'venue': 'Kolkata'},
        {'date': '17-May-26', 'day': 'Sun', 'time': '3:30 PM', 'home': 'Royal Challengers Bengaluru', 'away': 'Punjab Kings', 'venue': 'Dharamshala'},
        {'date': '17-May-26', 'day': 'Sun', 'time': '7:30 PM', 'home': 'Rajasthan Royals', 'away': 'Delhi Capitals', 'venue': 'Delhi'},
        {'date': '18-May-26', 'day': 'Mon', 'time': '7:30 PM', 'home': 'Sunrisers Hyderabad', 'away': 'Chennai Super Kings', 'venue': 'Chennai'},
        {'date': '19-May-26', 'day': 'Tue', 'time': '7:30 PM', 'home': 'Lucknow Super Giants', 'away': 'Rajasthan Royals', 'venue': 'Jaipur'},
        {'date': '20-May-26', 'day': 'Wed', 'time': '7:30 PM', 'home': 'Mumbai Indians', 'away': 'Kolkata Knight Riders', 'venue': 'Kolkata'},
        {'date': '21-May-26', 'day': 'Thu', 'time': '7:30 PM', 'home': 'Gujarat Titans', 'away': 'Chennai Super Kings', 'venue': 'Chennai'},
        {'date': '22-May-26', 'day': 'Fri', 'time': '7:30 PM', 'home': 'Royal Challengers Bengaluru', 'away': 'Sunrisers Hyderabad', 'venue': 'Hyderabad'},
        {'date': '23-May-26', 'day': 'Sat', 'time': '7:30 PM', 'home': 'Punjab Kings', 'away': 'Lucknow Super Giants', 'venue': 'Lucknow'},
        {'date': '24-May-26', 'day': 'Sun', 'time': '3:30 PM', 'home': 'Rajasthan Royals', 'away': 'Mumbai Indians', 'venue': 'Mumbai'},
        {'date': '24-May-26', 'day': 'Sun', 'time': '7:30 PM', 'home': 'Delhi Capitals', 'away': 'Kolkata Knight Riders', 'venue': 'Kolkata'},
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    for match in matches_data:
        cursor.execute('''
            INSERT OR IGNORE INTO matches (match_date, day, time, home_team, away_team, venue)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (match['date'], match['day'], match['time'], match['home'], match['away'], match['venue']))
    conn.commit()
    conn.close()

def get_all_member_names():
    """Return list of all member usernames."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE role = ?', ('member',))
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return names

def add_user(username, password, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role, balance FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

def get_matches():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM matches ORDER BY id')
    matches = cursor.fetchall()
    conn.close()
    return matches

def add_prediction(user_id, match_id, predicted_team):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT OR REPLACE INTO predictions (user_id, match_id, predicted_team) VALUES (?, ?, ?)', (user_id, match_id, predicted_team))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def remove_prediction(user_id, match_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM predictions WHERE user_id = ? AND match_id = ?', (user_id, match_id))
    conn.commit()
    conn.close()

def get_predictions_for_match(match_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT u.username, p.predicted_team FROM predictions p JOIN users u ON p.user_id = u.id WHERE p.match_id = ?', (match_id,))
    predictions = cursor.fetchall()
    conn.close()
    return predictions

def get_user_predictions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT m.id, m.home_team, m.away_team, p.predicted_team FROM predictions p JOIN matches m ON p.match_id = m.id WHERE p.user_id = ?', (user_id,))
    predictions = cursor.fetchall()
    conn.close()
    return predictions

def undo_match_winner(match_id):
    """Revert a finished match back to predictions_closed and delete its transactions."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE matches SET winner = NULL, status = 'predictions_closed' WHERE id = ?", (match_id,))
    cursor.execute("DELETE FROM transactions WHERE match_id = ?", (match_id,))
    conn.commit()
    conn.close()

def auto_close_predictions():
    """Auto-close predictions for matches whose start time has passed."""
    from datetime import datetime
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, match_date, time FROM matches WHERE status = 'upcoming'")
    upcoming = cursor.fetchall()
    conn.close()
    now = datetime.now()
    for match_id, match_date, match_time in upcoming:
        try:
            match_dt = datetime.strptime(f"{match_date} {match_time}", '%d-%b-%y %I:%M %p')
        except ValueError:
            continue
        if now >= match_dt:
            close_predictions(match_id)

def update_match_winner(match_id, winner):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE matches SET winner = ?, status = ? WHERE id = ?', (winner, 'finished', match_id))
    conn.commit()
    conn.close()

def add_transaction(user_id, match_id, type_, amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO transactions (user_id, match_id, type, amount) VALUES (?, ?, ?, ?)', (user_id, match_id, type_, amount))
    conn.commit()
    conn.close()

def get_user_balance_sheet(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT type, SUM(amount) FROM transactions WHERE user_id = ? GROUP BY type', (user_id,))
    data = cursor.fetchall()
    conn.close()
    balance = {}
    for type_, amount in data:
        balance[type_] = amount
    invested = balance.get('investment', 0)
    winnings = balance.get('winning', 0)
    # settlement is a corrective entry (can be positive or negative)
    settlement = balance.get('settlement', 0)
    profit = winnings - invested + settlement
    debt = -profit if profit < 0 else 0
    return {'invested': invested, 'winnings': winnings, 'profit': profit, 'debt': debt}

def get_setting(key):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def set_setting(key, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

def get_match_predictions(match_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT predicted_team, COUNT(*) as count FROM predictions WHERE match_id = ? GROUP BY predicted_team', (match_id,))
    predictions = cursor.fetchall()
    conn.close()
    return predictions

def get_team_counts_for_match(match_id):
    """Return {team_name: count} of current predictions for a match."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT predicted_team, COUNT(*) FROM predictions WHERE match_id = ? GROUP BY predicted_team', (match_id,))
    result = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return result

def get_total_members():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = ?', ('member',))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_max_per_team(total_members):
    """Return max allowed members per team based on total member count."""
    table = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 5, 8: 6, 9: 7, 10: 7}
    if total_members in table:
        return table[total_members]
    # For >10: allow up to ceil(total/2) - 1 or total-1 as fallback
    return total_members - 1

def split_money(match_id, winner):
    import random
    invest_amount = float(get_setting('invest_amount'))
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all members
    cursor.execute('SELECT id FROM users WHERE role = ?', ('member',))
    all_members = [row[0] for row in cursor.fetchall()]
    total_members = len(all_members)

    if total_members == 0:
        conn.close()
        return

    pool_amount = total_members * invest_amount

    # Get the two teams for this match
    cursor.execute('SELECT home_team, away_team FROM matches WHERE id = ?', (match_id,))
    home, away = cursor.fetchone()
    teams = [home, away]

    # Collect existing predictions
    predictions = {}
    for user_id in all_members:
        cursor.execute('SELECT predicted_team FROM predictions WHERE user_id = ? AND match_id = ?', (user_id, match_id))
        pred = cursor.fetchone()
        predictions[user_id] = pred[0] if pred else None

    # Randomly assign members who did not predict
    unpredicted = [uid for uid, team in predictions.items() if team is None]
    random.shuffle(unpredicted)
    for uid in unpredicted:
        # Assign to the team with fewer members so far, with randomness as tiebreaker
        counts = {t: sum(1 for p in predictions.values() if p == t) for t in teams}
        assigned = min(teams, key=lambda t: counts[t])
        predictions[uid] = assigned

    # Enforce max-per-team cap: move excess members to the other team randomly
    max_per_team = get_max_per_team(total_members)
    for team in teams:
        other_team = [t for t in teams if t != team][0]
        members_on_team = [uid for uid, p in predictions.items() if p == team]
        if len(members_on_team) > max_per_team:
            random.shuffle(members_on_team)
            excess = members_on_team[max_per_team:]
            for uid in excess:
                predictions[uid] = other_team

    # Winners = members assigned to the winning team
    winners = [uid for uid, team in predictions.items() if team == winner]

    if winners:
        share = pool_amount / len(winners)
        for uid in winners:
            add_transaction(uid, match_id, 'winning', share)

    # Record investment for all members
    for uid in all_members:
        add_transaction(uid, match_id, 'investment', invest_amount)

    conn.close()

def get_match_winners(match_id):
    """Return list of (username, amount) who won in a finished match."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.username, t.amount
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        WHERE t.match_id = ? AND t.type = 'winning'
        ORDER BY u.username
    ''', (match_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def reset_db():
    """Clear all predictions, transactions, and reset match statuses. Keep users and match schedule."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM predictions')
    cursor.execute('DELETE FROM transactions')
    cursor.execute("UPDATE matches SET status = 'upcoming', winner = NULL")
    conn.commit()
    conn.close()

def get_all_balances():
    """Return net balance for every member. Positive = admin owes them. Negative = they owe admin."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users WHERE role = ?', ('member',))
    members = cursor.fetchall()
    conn.close()
    result = []
    for uid, username in members:
        b = get_user_balance_sheet(uid)
        result.append({'id': uid, 'username': username, **b})
    return result

def settle_user(user_id):
    """Zero out a user's balance by inserting a settlement transaction."""
    b = get_user_balance_sheet(user_id)
    net = b['profit']  # positive = admin owes them, negative = they owe admin
    conn = get_db_connection()
    cursor = conn.cursor()
    # A settlement wipes the slate — record it as a settlement type
    cursor.execute(
        'INSERT INTO transactions (user_id, match_id, type, amount) VALUES (?, NULL, ?, ?)',
        (user_id, 'settlement', -net)
    )
    conn.commit()
    conn.close()

def close_predictions(match_id):
    """Mark match predictions as closed without setting a winner yet."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE matches SET status = 'predictions_closed' WHERE id = ? AND status = 'upcoming'", (match_id,))
    conn.commit()
    conn.close()

def get_match_assigned_teams(match_id):
    """Get the final team assignments for a match (after random assignment)."""
    import random
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE role = ?', ('member',))
    all_members = [row[0] for row in cursor.fetchall()]
    total_members = len(all_members)
    if total_members == 0:
        conn.close()
        return {}
    cursor.execute('SELECT home_team, away_team FROM matches WHERE id = ?', (match_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {}
    home, away = row
    teams = [home, away]
    conn = get_db_connection()
    cursor = conn.cursor()
    predictions = {}
    for uid in all_members:
        cursor.execute('SELECT predicted_team FROM predictions WHERE user_id = ? AND match_id = ?', (uid, match_id))
        pred = cursor.fetchone()
        predictions[uid] = pred[0] if pred else None
    conn.close()
    unpredicted = [uid for uid, t in predictions.items() if t is None]
    random.shuffle(unpredicted)
    for uid in unpredicted:
        counts = {t: sum(1 for p in predictions.values() if p == t) for t in teams}
        predictions[uid] = min(teams, key=lambda t: counts[t])
    max_per_team = get_max_per_team(total_members)
    for team in teams:
        other = [t for t in teams if t != team][0]
        on_team = [uid for uid, p in predictions.items() if p == team]
        if len(on_team) > max_per_team:
            random.shuffle(on_team)
            for uid in on_team[max_per_team:]:
                predictions[uid] = other
    return predictions