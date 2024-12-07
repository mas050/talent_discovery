import sqlite3
from datetime import datetime
from models import Usage
import streamlit as st

class UsageTracker:
    def __init__(self):
        self.conn = sqlite3.connect('usage.db')
        self.create_tables()
        self.pricing = {
            'gemini-1.5-flash': {
                'prompt': 0.00025,  # per 1K tokens
                'completion': 0.0005
            },
            'text-embedding-004': {
                'prompt': 0.0001,
                'completion': 0.0001
            }
        }

    def create_tables(self):
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS llm_usage (
            id INTEGER PRIMARY KEY,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            operation_type TEXT NOT NULL,
            prompt_tokens INTEGER NOT NULL,
            completion_tokens INTEGER NOT NULL,
            model TEXT NOT NULL,
            cost REAL NOT NULL
        )''')
        self.conn.commit()

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        if model not in self.pricing:
            return 0.0
        
        rates = self.pricing[model]
        prompt_cost = (prompt_tokens / 1000) * rates['prompt']
        completion_cost = (completion_tokens / 1000) * rates['completion']
        return prompt_cost + completion_cost

    def log_usage(self, usage: Usage):
        try:
            self.conn.execute('''
            INSERT INTO llm_usage 
            (user_id, timestamp, operation_type, prompt_tokens, completion_tokens, model, cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                usage.user_id,
                usage.timestamp.isoformat(),
                usage.operation_type,
                usage.prompt_tokens,
                usage.completion_tokens,
                usage.model,
                usage.cost
            ))
            self.conn.commit()
            print(f"Logged usage for {usage.user_id}: {usage.operation_type}")  # Debug print
        except Exception as e:
            print(f"Error logging usage: {e}")  # Debug print

    def get_user_usage(self, user_id: str, start_date=None, end_date=None):
        try:
            query = 'SELECT * FROM llm_usage WHERE user_id = ?'
            params = [user_id]
            
            if start_date:
                query += ' AND date(timestamp) >= date(?)'
                params.append(start_date.isoformat())
            if end_date:
                query += ' AND date(timestamp) <= date(?)'
                params.append(end_date.isoformat())
                
            print(f"Executing query: {query} with params: {params}")  # Debug print
            cursor = self.conn.execute(query, params)
            results = cursor.fetchall()
            print(f"Found {len(results)} records")  # Debug print
            return results
        except Exception as e:
            print(f"Error getting usage: {e}")  # Debug print
            return []
        
    def get_all_usage(self, start_date=None, end_date=None):
        try:
            query = 'SELECT * FROM llm_usage'
            params = []
            
            if start_date:
                query += ' WHERE date(timestamp) >= date(?)'
                params.append(start_date.isoformat())
            if end_date:
                query += ' AND date(timestamp) <= date(?)' if start_date else ' WHERE date(timestamp) <= date(?)'
                params.append(end_date.isoformat())
                
            cursor = self.conn.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting all usage: {e}")
            return []
        
    def get_total_cost(self, user_id: str):
        cursor = self.conn.execute(
            'SELECT SUM(cost) FROM llm_usage WHERE user_id = ?',
            (user_id,)
        )
        return cursor.fetchone()[0] or 0.0

    def get_all_users(self):
        cursor = self.conn.execute('SELECT DISTINCT user_id FROM llm_usage')
        return [row[0] for row in cursor.fetchall()]