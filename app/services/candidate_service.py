# import logging
# from typing import List, Dict, Any, Optional
# from uuid import uuid4
# from datetime import datetime

# from app.core.config import settings
# from app.schemas.candidate import CandidateScoreCreate, CandidateScoreUpdate

# logger = logging.getLogger(__name__)

# class CandidateService:
#     def __init__(self):
#         self.connection = None
    
#     def _get_connection(self):
#         """Get database connection"""
#         import psycopg2
#         from psycopg2.extras import RealDictCursor
        
#         if self.connection is None or self.connection.closed:
#             self.connection = psycopg2.connect(
#                 host=settings.ODOO_DB_HOST,
#                 port=settings.ODOO_DB_PORT,
#                 database=settings.ODOO_DB_NAME,
#                 user=settings.ODOO_DB_USER,
#                 password=settings.ODOO_DB_PASSWORD,
#                 cursor_factory=RealDictCursor
#             )
#             self.connection.autocommit = True
#         return self.connection

#     # def create_candidate_score_table(self):
#     #     """Create candidate_score table if not exists"""
#     #     try:
#     #         conn = self._get_connection()
#     #         cursor = conn.cursor()
            
#     #         create_table_query = """
#     #         CREATE TABLE IF NOT EXISTS candidate_score (
#     #             id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
#     #             application_id INTEGER NOT NULL,
#     #             fit_score DECIMAL(5,2) CHECK (fit_score >= 0 AND fit_score <= 100),
#     #             skill_score DECIMAL(5,2),
#     #             experience_score DECIMAL(5,2),
#     #             education_score DECIMAL(5,2),
#     #             reasons JSONB,
#     #             updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     #             CONSTRAINT fk_application 
#     #                 FOREIGN KEY (application_id) 
#     #                 REFERENCES hr_job_application(id) 
#     #                 ON DELETE CASCADE
#     #         );
            
#     #         CREATE INDEX IF NOT EXISTS idx_application_id ON candidate_score(application_id);
#     #         CREATE INDEX IF NOT EXISTS idx_fit_score ON candidate_score(fit_score);
#     #         CREATE INDEX IF NOT EXISTS idx_updated_at ON candidate_score(updated_at);
#     #         """
            
#     #         cursor.execute(create_table_query)
#     #         logger.info("Candidate score table created or already exists")
            
#     #     except Exception as e:
#     #         logger.error(f"Error creating candidate score table: {e}")
#     #         raise

#     def create_candidate_score_table(self):
#         """Create candidate_score table - pakai SERIAL instead of UUID"""
#         try:
#             conn = self._get_connection()
#             cursor = conn.cursor()
            
#             create_table_query = """
#             CREATE TABLE IF NOT EXISTS candidate_score (
#                 id SERIAL PRIMARY KEY,
#                 application_id INTEGER NOT NULL UNIQUE,
#                 job_id INTEGER NOT NULL,
#                 candidate_name VARCHAR(255),
#                 fit_score DECIMAL(5,2) CHECK (fit_score >= 0 AND fit_score <= 100),
#                 skill_score DECIMAL(5,2),
#                 experience_score DECIMAL(5,2),
#                 education_score DECIMAL(5,2),
#                 reasons JSONB,
#                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             );
            
#             CREATE INDEX IF NOT EXISTS idx_cs_application ON candidate_score(application_id);
#             CREATE INDEX IF NOT EXISTS idx_cs_job ON candidate_score(job_id);
#             CREATE INDEX IF NOT EXISTS idx_cs_score ON candidate_score(fit_score);
#             """
            
#             cursor.execute(create_table_query)
#             logger.info("Candidate score table created successfully")
            
#         except Exception as e:
#             logger.error(f"Error creating candidate score table: {e}")
#             raise
    
#     # def save_candidate_score(self, score_data: CandidateScoreCreate) -> Optional[str]:
#     #     """Save candidate score to database"""
#     #     try:
#     #         conn = self._get_connection()
#     #         cursor = conn.cursor()
            
#     #         insert_query = """
#     #         INSERT INTO candidate_score 
#     #         (id, application_id, fit_score, skill_score, experience_score, education_score, reasons, updated_at)
#     #         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#     #         ON CONFLICT (application_id) 
#     #         DO UPDATE SET 
#     #             fit_score = EXCLUDED.fit_score,
#     #             skill_score = EXCLUDED.skill_score,
#     #             experience_score = EXCLUDED.experience_score,
#     #             education_score = EXCLUDED.education_score,
#     #             reasons = EXCLUDED.reasons,
#     #             updated_at = EXCLUDED.updated_at
#     #         RETURNING id
#     #         """
            
#     #         score_id = str(uuid4())
#     #         cursor.execute(insert_query, (
#     #             score_id,
#     #             score_data.application_id,
#     #             score_data.fit_score,
#     #             score_data.skill_score,
#     #             score_data.experience_score,
#     #             score_data.education_score,
#     #             score_data.reasons,
#     #             datetime.now()
#     #         ))
            
#     #         result = cursor.fetchone()
#     #         return result['id'] if result else None
            
#     #     except Exception as e:
#     #         logger.error(f"Error saving candidate score: {e}")
#     #         return None

#     def save_candidate_score(self, score_data: CandidateScoreCreate, job_id: int, candidate_name: str = "Test Candidate") -> Optional[str]:
#         """Save candidate score dengan job_id"""
#         try:
#             conn = self._get_connection()
#             cursor = conn.cursor()
            
#             # Convert reasons to JSON string safely
#             reasons_json = None
#             if score_data.reasons:
#                 import json
#                 reasons_json = json.dumps(score_data.reasons)
            
#             insert_query = """
#             INSERT INTO candidate_score 
#             (application_id, job_id, candidate_name, fit_score, skill_score, experience_score, education_score, reasons, updated_at)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#             ON CONFLICT (application_id) 
#             DO UPDATE SET 
#                 fit_score = EXCLUDED.fit_score,
#                 skill_score = EXCLUDED.skill_score,
#                 experience_score = EXCLUDED.experience_score,
#                 education_score = EXCLUDED.education_score,
#                 reasons = EXCLUDED.reasons,
#                 updated_at = EXCLUDED.updated_at
#             RETURNING id
#             """
            
#             cursor.execute(insert_query, (
#                 score_data.application_id,
#                 job_id,
#                 candidate_name,
#                 float(score_data.fit_score),
#                 float(score_data.skill_score) if score_data.skill_score else None,
#                 float(score_data.experience_score) if score_data.experience_score else None,
#                 float(score_data.education_score) if score_data.education_score else None,
#                 reasons_json,  # Use the converted JSON
#                 datetime.now()
#             ))
            
#             result = cursor.fetchone()
#             print(f"DEBUG: Saved candidate score for application {score_data.application_id}, result: {result}")
#             return result['id'] if result else None
            
#         except Exception as e:
#             logger.error(f"Error saving candidate score: {e}")
#             print(f"DEBUG ERROR: {e}")  # Add debug print
#             return None

    

#     # def get_candidate_ranking(self, job_id: int, limit: int = 50, offset: int = 0, 
#     #                         sort_order: str = "desc") -> List[Dict[str, Any]]:
#     #     """Get candidate ranking for a job"""
#     #     try:
#     #         conn = self._get_connection()
#     #         cursor = conn.cursor()
            
#     #         # Validate sort order
#     #         sort_order = "DESC" if sort_order.lower() == "desc" else "ASC"
            
#     #         query = f"""
#     #         SELECT 
#     #             cs.application_id,
#     #             cs.fit_score,
#     #             cs.skill_score,
#     #             cs.experience_score,
#     #             cs.education_score,
#     #             cs.reasons,
#     #             cs.updated_at,
#     #             hja.partner_name as candidate_name,
#     #             rp.email,
#     #             rp.phone
#     #         FROM candidate_score cs
#     #         JOIN hr_job_application hja ON cs.application_id = hja.id
#     #         JOIN hr_applicant ha ON hja.applicant_id = ha.id
#     #         JOIN res_partner rp ON ha.partner_id = rp.id
#     #         WHERE hja.job_id = %s
#     #         ORDER BY cs.fit_score {sort_order}
#     #         LIMIT %s OFFSET %s
#     #         """
            
#     #         cursor.execute(query, (job_id, limit, offset))
#     #         results = cursor.fetchall()
            
#     #         return results
            
#     #     except Exception as e:
#     #         logger.error(f"Error getting candidate ranking: {e}")
#     #         return []

#     def get_candidate_ranking(self, job_id: int, limit: int = 50, offset: int = 0, 
#                         sort_order: str = "desc") -> List[Dict[str, Any]]:
#         """Get candidate ranking - STANDALONE tanpa join Odoo"""
#         try:
#             conn = self._get_connection()
#             cursor = conn.cursor()
            
#             # Validate sort order
#             sort_order = "DESC" if sort_order.lower() == "desc" else "ASC"
            
#             query = f"""
#             SELECT 
#                 application_id,
#                 job_id,
#                 candidate_name,
#                 fit_score,
#                 skill_score,
#                 experience_score,
#                 education_score,
#                 reasons,
#                 updated_at
#             FROM candidate_score 
#             WHERE job_id = %s
#             ORDER BY fit_score {sort_order}
#             LIMIT %s OFFSET %s
#             """
            
#             cursor.execute(query, (job_id, limit, offset))
#             results = cursor.fetchall()
            
#             return results
            
#         except Exception as e:
#             logger.error(f"Error getting candidate ranking: {e}")
#             return []

#     def get_candidate_score(self, application_id: int) -> Optional[Dict[str, Any]]:
#         """Get candidate score by application ID"""
#         try:
#             conn = self._get_connection()
#             cursor = conn.cursor()
            
#             query = """
#             SELECT * FROM candidate_score 
#             WHERE application_id = %s
#             """
            
#             cursor.execute(query, (application_id,))
#             result = cursor.fetchone()
            
#             return result
            
#         except Exception as e:
#             logger.error(f"Error getting candidate score: {e}")
#             return None

#     # def candidate_has_score(self, job_id: int) -> bool:
#     #     """Check if any candidate has score for a job"""
#     #     try:
#     #         conn = self._get_connection()
#     #         cursor = conn.cursor()
            
#     #         query = """
#     #         SELECT COUNT(*) as count
#     #         FROM candidate_score cs
#     #         JOIN hr_job_application hja ON cs.application_id = hja.id
#     #         WHERE hja.job_id = %s
#     #         """
            
#     #         cursor.execute(query, (job_id,))
#     #         result = cursor.fetchone()
            
#     #         return result['count'] > 0 if result else False
            
#     #     except Exception as e:
#     #         logger.error(f"Error checking candidate scores: {e}")
#     #         return False

#     def candidate_has_score(self, job_id: int) -> bool:
#         """Check if any candidate has score for a job - STANDALONE"""
#         try:
#             conn = self._get_connection()
#             cursor = conn.cursor()
            
#             query = """
#             SELECT COUNT(*) as count
#             FROM candidate_score 
#             WHERE job_id = %s
#             """
            
#             cursor.execute(query, (job_id,))
#             result = cursor.fetchone()
            
#             return result['count'] > 0 if result else False
            
#         except Exception as e:
#             logger.error(f"Error checking candidate scores: {e}")
#             return False


import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.config import settings
from app.schemas.candidate import CandidateScoreCreate
from app.services.database import get_db_connection  # ← UPDATE IMPORT

logger = logging.getLogger(__name__)

class CandidateService:
    def __init__(self):
        pass
    
    def create_candidate_score_table(self):
        """Create candidate_score table - using standalone database"""
        try:
            conn = get_db_connection()  # ← Use standalone connection
            cursor = conn.cursor()
            
            create_table_query = """
            CREATE TABLE IF NOT EXISTS candidate_score (
                id SERIAL PRIMARY KEY,
                application_id INTEGER NOT NULL UNIQUE,
                job_id INTEGER NOT NULL,
                candidate_name VARCHAR(255),
                fit_score DECIMAL(5,2) CHECK (fit_score >= 0 AND fit_score <= 100),
                skill_score DECIMAL(5,2),
                experience_score DECIMAL(5,2),
                education_score DECIMAL(5,2),
                reasons JSONB,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_cs_application ON candidate_score(application_id);
            CREATE INDEX IF NOT EXISTS idx_cs_job ON candidate_score(job_id);
            CREATE INDEX IF NOT EXISTS idx_cs_score ON candidate_score(fit_score);
            """
            
            cursor.execute(create_table_query)
            logger.info("Candidate score table created successfully")
            
        except Exception as e:
            logger.error(f"Error creating candidate score table: {e}")
            raise
    
    def save_candidate_score(self, score_data: CandidateScoreCreate, job_id: int, candidate_name: str = "Test Candidate") -> Optional[str]:
        """Save candidate score menggunakan standalone database"""
        try:
            conn = get_db_connection()  # ← Use standalone connection
            cursor = conn.cursor()
            
            # Convert reasons to JSON string
            import json
            reasons_json = json.dumps(score_data.reasons) if score_data.reasons else None
            
            insert_query = """
            INSERT INTO candidate_score 
            (application_id, job_id, candidate_name, fit_score, skill_score, experience_score, education_score, reasons, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (application_id) 
            DO UPDATE SET 
                fit_score = EXCLUDED.fit_score,
                skill_score = EXCLUDED.skill_score,
                experience_score = EXCLUDED.experience_score,
                education_score = EXCLUDED.education_score,
                reasons = EXCLUDED.reasons,
                updated_at = EXCLUDED.updated_at
            RETURNING id
            """
            
            cursor.execute(insert_query, (
                score_data.application_id,
                job_id,
                candidate_name,
                float(score_data.fit_score),
                float(score_data.skill_score) if score_data.skill_score else None,
                float(score_data.experience_score) if score_data.experience_score else None,
                float(score_data.education_score) if score_data.education_score else None,
                reasons_json,
                datetime.now()
            ))
            
            result = cursor.fetchone()
            return result['id'] if result else None
            
        except Exception as e:
            logger.error(f"Error saving candidate score: {e}")
            return None
    

    def get_candidate_ranking(self, job_id: int, limit: int = 50, offset: int = 0, 
                        sort_order: str = "desc") -> List[Dict[str, Any]]:
        """Get candidate ranking - STANDALONE tanpa join Odoo"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Validate sort order
            sort_order = "DESC" if sort_order.lower() == "desc" else "ASC"
            
            query = f"""
            SELECT 
                application_id,
                job_id,
                candidate_name,
                fit_score,
                skill_score,
                experience_score,
                education_score,
                reasons,
                updated_at
            FROM candidate_score 
            WHERE job_id = %s
            ORDER BY fit_score {sort_order}
            LIMIT %s OFFSET %s
            """
            
            cursor.execute(query, (job_id, limit, offset))
            results = cursor.fetchall()
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting candidate ranking: {e}")
            return []

    def get_candidate_score(self, application_id: int) -> Optional[Dict[str, Any]]:
        """Get candidate score by application ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT * FROM candidate_score 
            WHERE application_id = %s
            """
            
            cursor.execute(query, (application_id,))
            result = cursor.fetchone()
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting candidate score: {e}")
            return None


    def candidate_has_score(self, job_id: int) -> bool:
        """Check if any candidate has score for a job - STANDALONE"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT COUNT(*) as count
            FROM candidate_score 
            WHERE job_id = %s
            """
            
            cursor.execute(query, (job_id,))
            result = cursor.fetchone()
            
            return result['count'] > 0 if result else False
            
        except Exception as e:
            logger.error(f"Error checking candidate scores: {e}")
            return False