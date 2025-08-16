import json
import os
from typing import List, Dict, Optional
import sqlite3
from datetime import datetime
from core.avatar_manager import AvatarManager

class CharacterManager:
    def __init__(self, db_path="characters.db", test_mode=True):
        self.db_path = db_path
        self.avatar_manager = AvatarManager(test_mode=test_mode)
        self._init_database()
    
    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                voice_style TEXT,
                gender TEXT,
                avatar_path TEXT,
                created_at TIMESTAMP,
                usage_count INTEGER DEFAULT 0
            )
        """)
        
        # Check if avatar_path column exists, if not add it (for migration)
        cursor.execute("PRAGMA table_info(characters)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'avatar_path' not in columns:
            cursor.execute("ALTER TABLE characters ADD COLUMN avatar_path TEXT")
            print("Added avatar_path column to characters table")
        
        conn.commit()
        conn.close()
    
    def add_character(self, character: Dict, generate_avatar: bool = True) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generate avatar if requested
        avatar_path = None
        if generate_avatar:
            avatar_path = self.avatar_manager.generate_avatar(
                character['name'],
                character
            )
        
        try:
            cursor.execute("""
                INSERT INTO characters (name, description, voice_style, gender, avatar_path, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                character['name'],
                character['description'],
                character['voice_style'],
                character['gender'],
                avatar_path,
                datetime.now()
            ))
            
            conn.commit()
            character_id = cursor.lastrowid
            return character_id
        except sqlite3.IntegrityError:
            return -1  # Character already exists
        finally:
            conn.close()
    
    def get_character(self, name: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Select columns explicitly to avoid issues with legacy column ordering
        cursor.execute(
            """
            SELECT id, name, description, voice_style, gender, avatar_path, created_at, usage_count
            FROM characters
            WHERE name = ?
            """,
            (name,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'voice_style': row[3],
                'gender': row[4],
                'avatar_path': row[5],
                'created_at': row[6],
                'usage_count': row[7]
            }
        return None
    
    def get_all_characters(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Select columns explicitly to avoid issues with legacy column ordering
        cursor.execute(
            """
            SELECT id, name, description, voice_style, gender, avatar_path, created_at, usage_count
            FROM characters
            ORDER BY usage_count DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()
        
        characters = []
        for row in rows:
            characters.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'voice_style': row[3],
                'gender': row[4],
                'avatar_path': row[5],
                'created_at': row[6],
                'usage_count': row[7]
            })
        
        return characters
    
    def update_usage(self, name: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE characters 
            SET usage_count = usage_count + 1 
            WHERE name = ?
        """, (name,))
        
        conn.commit()
        conn.close()
    
    def update_avatar_path(self, name: str, avatar_path: str) -> bool:
        """
        Update the avatar path for an existing character
        
        Args:
            name: Character name
            avatar_path: New avatar path
            
        Returns:
            True if updated successfully
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE characters 
                SET avatar_path = ? 
                WHERE name = ?
            """, (avatar_path, name))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def delete_character(self, name: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM characters WHERE name = ?", (name,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()