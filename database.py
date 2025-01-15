import sqlite3
from datetime import datetime
import json

def init_db():
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    
    # Chat-Sessions Tabelle
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            theme TEXT DEFAULT 'light'
        )
    ''')
    
    # Nachrichten Tabelle
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_session(title="Neue Chat-Session"):
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    c.execute('INSERT INTO chat_sessions (title) VALUES (?)', (title,))
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return session_id

def get_sessions():
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    c.execute('''
        SELECT id, title, created_at, theme 
        FROM chat_sessions 
        ORDER BY updated_at DESC
    ''')
    sessions = [
        {
            'id': row[0],
            'title': row[1],
            'created_at': row[2],
            'theme': row[3]
        }
        for row in c.fetchall()
    ]
    conn.close()
    return sessions

def get_session_messages(session_id):
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    c.execute('SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at', (session_id,))
    messages = [
        {
            'role': row[0],
            'content': row[1]
        }
        for row in c.fetchall()
    ]
    conn.close()
    return messages

def add_message(session_id, role, content):
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)',
              (session_id, role, content))
    c.execute('UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
              (session_id,))
    conn.commit()
    conn.close()

def update_session_theme(session_id, theme):
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    c.execute('UPDATE chat_sessions SET theme = ? WHERE id = ?', (theme, session_id))
    conn.commit()
    conn.close()

def export_session(session_id, format='json'):
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    
    # Session-Details abrufen
    c.execute('SELECT title, created_at FROM chat_sessions WHERE id = ?', (session_id,))
    session_data = c.fetchone()
    
    if not session_data:
        conn.close()
        return None
    
    # Nachrichten abrufen
    messages = get_session_messages(session_id)
    
    export_data = {
        'session_id': session_id,
        'title': session_data[0],
        'created_at': session_data[1],
        'messages': messages
    }
    
    conn.close()
    
    if format == 'json':
        return json.dumps(export_data, indent=2)
    else:
        # Hier können weitere Exportformate implementiert werden
        return None

def delete_session(session_id):
    conn = sqlite3.connect('chats.db')
    c = conn.cursor()
    c.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
    c.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
    conn.commit()
    conn.close() 