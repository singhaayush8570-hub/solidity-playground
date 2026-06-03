import sqlite3
from datetime import datetime

class CalculatorDatabase:
    def __init__(self, db_path="calculator_history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expression TEXT NOT NULL,
                result TEXT NOT NULL,
                operation_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'success'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_history(self, expression, result, operation_type="general", status="success"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO history (expression, result, operation_type, status)
                VALUES (?, ?, ?, ?)
            ''', (expression, str(result), operation_type, status))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            conn.close()
    
    def get_history(self, limit=100, operation_type=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if operation_type:
            cursor.execute('''
                SELECT id, expression, result, operation_type, timestamp, status
                FROM history
                WHERE operation_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (operation_type, limit))
        else:
            cursor.execute('''
                SELECT id, expression, result, operation_type, timestamp, status
                FROM history
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'id': r[0],
            'expression': r[1],
            'result': r[2],
            'operation_type': r[3],
            'timestamp': r[4],
            'status': r[5]
        } for r in results]
    
    def search_history(self, query):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, expression, result, operation_type, timestamp, status
            FROM history
            WHERE expression LIKE ? OR result LIKE ?
            ORDER BY timestamp DESC
            LIMIT 50
        ''', (f'%{query}%', f'%{query}%'))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'id': r[0],
            'expression': r[1],
            'result': r[2],
            'operation_type': r[3],
            'timestamp': r[4],
            'status': r[5]
        } for r in results]
    
    def get_statistics(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM history WHERE status = "success"')
        total = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT operation_type, COUNT(*) as count
            FROM history
            WHERE status = "success"
            GROUP BY operation_type
            ORDER BY count DESC
            LIMIT 1
        ''')
        most_used = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_calculations': total,
            'most_used_operation': most_used[0] if most_used else 'none'
        }
    
    def clear_history(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM history')
        conn.commit()
        conn.close()
    
    def delete_history_item(self, item_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM history WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
