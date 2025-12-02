# from jose import JWTError, jwt
# from passlib.context import CryptContext
# from datetime import datetime, timedelta
# from fastapi import HTTPException, status

# import requests
# import json

# from typing import Optional
# import logging

# from app.core.config import settings
# from app.schemas.models import TokenData, OdooUser

# logger = logging.getLogger(__name__)

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# class OdooAuthenticator:
#     def __init__(self):
#         self.odoo_url = settings.ODOO_URL
    
#     def authenticate_user(self, email: str, password: str) -> Optional[OdooUser]:
#         """
#         Authenticate user against Odoo database directly
#         """
#         try:
#             # Connect to Odoo database
#             from app.services.database import get_db_connection
#             conn = get_db_connection()
#             cursor = conn.cursor()
            
#             # Query untuk mencari user berdasarkan email
#             query = """
#             SELECT 
#                 u.id as user_id,
#                 u.login as email,
#                 u.password as password_hash,
#                 p.name as name,
#                 p.id as partner_id
#             FROM res_users u
#             JOIN res_partner p ON u.partner_id = p.id
#             WHERE u.login = %s AND u.active = true
#             """
            
#             cursor.execute(query, (email,))
#             user_data = cursor.fetchone()
            
#             if not user_data:
#                 return None
            
#             # Verifikasi password (Odoo menggunakan crypt format)
#             if self.verify_odoo_password(password, user_data['password_hash']):
#                 return OdooUser(
#                     id=user_data['user_id'],
#                     name=user_data['name'],
#                     email=user_data['email'],
#                     partner_id=user_data['partner_id']
#                 )
            
#             return None
            
#         except Exception as e:
#             logger.error(f"Authentication error: {e}")
#             return None
    
#     def verify_odoo_password(self, plain_password: str, hashed_password: str) -> bool:
#         """
#         Verify Odoo password hash
#         Odoo menggunakan format crypt dengan salt
#         """
#         try:
#             # Odoo password format biasanya seperti: crypt$salt$hash
#             if hashed_password.startswith('crypt$'):
#                 parts = hashed_password.split('$')
#                 if len(parts) >= 3:
#                     import crypt
#                     return crypt.crypt(plain_password, parts[1]) == parts[1] + '$' + parts[2]
            
#             # Fallback: simple comparison (tidak disarankan untuk production)
#             return plain_password == hashed_password
#         except Exception as e:
#             logger.error(f"Password verification error: {e}")
#             return False
    
#     def authenticate_via_odoo_api(self, email: str, password: str) -> Optional[OdooUser]:
#         """
#         Alternative: Authenticate using Odoo XML-RPC API
#         """
#         try:
#             # Get common endpoint
#             common_endpoint = f"{self.odoo_url}/xmlrpc/2/common"
            
#             # Get uid
#             import xmlrpc.client
#             common = xmlrpc.client.ServerProxy(common_endpoint)
#             uid = common.authenticate(settings.ODOO_DB_NAME, email, password, {})
            
#             if uid:
#                 # Get user details
#                 models = xmlrpc.client.ServerProxy(f"{self.odoo_url}/xmlrpc/2/object")
#                 user_data = models.execute_kw(
#                     settings.ODOO_DB_NAME, uid, password,
#                     'res.users', 'read', [uid],
#                     {'fields': ['name', 'login', 'partner_id']}
#                 )
                
#                 if user_data:
#                     return OdooUser(
#                         id=uid,
#                         name=user_data[0]['name'],
#                         email=user_data[0]['login'],
#                         partner_id=user_data[0]['partner_id'][0]
#                     )
            
#             return None
            
#         except Exception as e:
#             logger.error(f"Odoo API authentication error: {e}")
#             return None

# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
#     return encoded_jwt

# def verify_token(token: str) -> TokenData:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
#         email: str = payload.get("sub")
#         user_id: int = payload.get("user_id")
        
#         if email is None or user_id is None:
#             raise credentials_exception
        
#         return TokenData(email=email, user_id=user_id)
#     except JWTError:
#         raise credentials_exception

# # Global authenticator instance
# odoo_auth = OdooAuthenticator()

from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.core.config import settings
import logging
import bcrypt  # ← Use bcrypt directly

logger = logging.getLogger(__name__)

class Authenticator:
    def __init__(self):
        pass
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt directly"""
        try:
            # Convert password to bytes and truncate to 72 bytes for bcrypt
            password_bytes = password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
                logger.warning("Password truncated to 72 bytes for bcrypt")
            
            # Generate salt and hash
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Password hashing error: {e}")
            raise
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password using bcrypt directly"""
        try:
            # Convert to bytes
            plain_bytes = plain_password.encode('utf-8')
            if len(plain_bytes) > 72:
                plain_bytes = plain_bytes[:72]
            
            hashed_bytes = hashed_password.encode('utf-8')
            
            return bcrypt.checkpw(plain_bytes, hashed_bytes)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def authenticate_user(self, email: str, password: str):
        """Authenticate user against standalone database"""
        try:
            from app.services.database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT id, email, username, full_name, password_hash, is_active, is_superuser
            FROM users 
            WHERE email = %s AND is_active = true
            """
            
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()
            cursor.close()
            
            if not user_data:
                logger.warning(f"User not found or inactive: {email}")
                return None
            
            logger.debug(f"Found user: {user_data['email']}")
            
            # Verify password
            if not self._verify_password(password, user_data['password_hash']):
                logger.warning(f"Invalid password for user: {email}")
                return None
            
            logger.info(f"User authenticated successfully: {email}")
            return {
                "id": user_data['id'],
                "email": user_data['email'],
                "username": user_data['username'],
                "full_name": user_data['full_name'],
                "is_superuser": user_data['is_superuser']
            }
            
        except Exception as e:
            logger.error(f"Authentication error for {email}: {e}")
            return None
    
    def create_user(self, email: str, username: str, password: str, full_name: str = None):
        """Create new user in standalone database"""
        try:
            from app.services.database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = %s OR username = %s", (email, username))
            if cursor.fetchone():
                logger.warning(f"User already exists: email={email}, username={username}")
                return None
            
            # Hash password
            hashed_password = self._hash_password(password)
            
            insert_query = """
            INSERT INTO users (email, username, full_name, password_hash)
            VALUES (%s, %s, %s, %s)
            RETURNING id, email, username, full_name, is_active, is_superuser
            """
            
            cursor.execute(insert_query, (email, username, full_name, hashed_password))
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            
            logger.info(f"User created successfully: {email}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating user {email}: {e}")
            return None
    
    def reset_password(self, email: str, new_password: str):
        """Reset user password"""
        try:
            from app.services.database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Hash new password
            hashed_password = self._hash_password(new_password)
            
            update_query = """
            UPDATE users 
            SET password_hash = %s, updated_at = CURRENT_TIMESTAMP
            WHERE email = %s
            RETURNING id, email
            """
            
            cursor.execute(update_query, (hashed_password, email))
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            
            if result:
                logger.info(f"Password reset successfully for: {email}")
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error resetting password for {email}: {e}")
            return None

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise

def verify_token(token: str):
    """Verify JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("user_id")
        email = payload.get("sub")
        
        if email is None or user_id is None:
            logger.warning("Token missing required fields")
            raise credentials_exception
        
        logger.debug(f"Token verified for user: {email}, id: {user_id}")
        return {"email": email, "user_id": user_id}
        
    except JWTError as jwt_error:
        logger.warning(f"JWT verification failed: {jwt_error}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise credentials_exception

# Helper function untuk hash password
def get_password_hash(password: str) -> str:
    """Get password hash using bcrypt directly"""
    auth = Authenticator()
    return auth._hash_password(password)

# Helper function untuk verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt directly"""
    auth = Authenticator()
    return auth._verify_password(plain_password, hashed_password)

# Global authenticator instance
auth = Authenticator()