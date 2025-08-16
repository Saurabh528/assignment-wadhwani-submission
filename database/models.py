import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

class DatabaseModels:
    def __init__(self, db_path="content_factory.db"):
        self.db_path = db_path
        self.init_all_tables()
    
    def init_all_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Characters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                voice_style TEXT,
                gender TEXT,
                created_at TIMESTAMP,
                usage_count INTEGER DEFAULT 0
            )
        """)
        
        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                topic TEXT,
                num_lessons INTEGER,
                video_length INTEGER,
                language TEXT,
                created_at TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        # Videos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                lesson_number INTEGER,
                title TEXT,
                script TEXT,
                video_path TEXT,
                duration REAL,
                created_at TIMESTAMP,
                qa_score REAL,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        
        # QA Reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS qa_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER,
                audio_sync_score REAL,
                character_consistency_score REAL,
                caption_alignment_score REAL,
                issues TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos (id)
            )
        """)
        
        conn.commit()
        conn.close()

class ProjectModel:
    def __init__(self, db_path="content_factory.db"):
        self.db_path = db_path
    
    def create_project(self, project_data: Dict) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO projects (name, topic, num_lessons, video_length, language, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            project_data['name'],
            project_data['topic'],
            project_data['num_lessons'],
            project_data['video_length'],
            project_data['language'],
            datetime.now()
        ))
        
        conn.commit()
        project_id = cursor.lastrowid
        conn.close()
        return project_id
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'topic': row[2],
                'num_lessons': row[3],
                'video_length': row[4],
                'language': row[5],
                'created_at': row[6],
                'status': row[7]
            }
        return None
    
    def update_project_status(self, project_id: int, status: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE projects SET status = ? WHERE id = ?
        """, (status, project_id))
        
        conn.commit()
        conn.close()

class VideoModel:
    def __init__(self, db_path="content_factory.db"):
        self.db_path = db_path
    
    def create_video(self, video_data: Dict) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO videos (project_id, lesson_number, title, script, video_path, duration, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            video_data['project_id'],
            video_data['lesson_number'],
            video_data['title'],
            video_data['script'],
            video_data['video_path'],
            video_data['duration'],
            datetime.now()
        ))
        
        conn.commit()
        video_id = cursor.lastrowid
        conn.close()
        return video_id
    
    def get_videos_by_project(self, project_id: int) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM videos WHERE project_id = ? ORDER BY lesson_number", (project_id,))
        rows = cursor.fetchall()
        conn.close()
        
        videos = []
        for row in rows:
            videos.append({
                'id': row[0],
                'project_id': row[1],
                'lesson_number': row[2],
                'title': row[3],
                'script': row[4],
                'video_path': row[5],
                'duration': row[6],
                'created_at': row[7],
                'qa_score': row[8]
            })
        
        return videos

class QAModel:
    def __init__(self, db_path="content_factory.db"):
        self.db_path = db_path
    
    def create_qa_report(self, qa_data: Dict) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO qa_reports (video_id, audio_sync_score, character_consistency_score, 
                                  caption_alignment_score, issues, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            qa_data['video_id'],
            qa_data['audio_sync_score'],
            qa_data['character_consistency_score'],
            qa_data['caption_alignment_score'],
            qa_data['issues'],
            datetime.now()
        ))
        
        conn.commit()
        report_id = cursor.lastrowid
        conn.close()
        return report_id
    
    def get_qa_report(self, video_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM qa_reports WHERE video_id = ? ORDER BY created_at DESC LIMIT 1", (video_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'video_id': row[1],
                'audio_sync_score': row[2],
                'character_consistency_score': row[3],
                'caption_alignment_score': row[4],
                'issues': row[5],
                'created_at': row[6]
            }
        return None