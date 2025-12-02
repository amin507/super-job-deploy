# from fastapi import FastAPI, Depends, HTTPException, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from fastapi.middleware.cors import CORSMiddleware
# from datetime import timedelta
# import logging

# from app.services.auth import odoo_auth, create_access_token, verify_token
# from app.schemas.models import UserLogin, Token, OdooUser, ProjectCreate, TimesheetCreate
# from app.core.config import settings

# from app.routes import candidate

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = FastAPI(title="Super Job Backend", version="1.0.0")

# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(candidate.router, prefix=settings.API_V1_STR, tags=["candidates"])

# # Security
# security = HTTPBearer()

# async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     token_data = verify_token(credentials.credentials)
    
#     # Verify user still exists in Odoo
#     from app.services.database import get_db_connection
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     query = """
#     SELECT u.id as user_id, u.login as email, p.name as name, p.id as partner_id
#     FROM res_users u
#     JOIN res_partner p ON u.partner_id = p.id
#     WHERE u.id = %s AND u.active = true
#     """
    
#     cursor.execute(query, (token_data.user_id,))
#     user_data = cursor.fetchone()
    
#     if not user_data:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="User not found or inactive"
#         )
    
#     return OdooUser(
#         id=user_data['user_id'],
#         name=user_data['name'],
#         email=user_data['email'],
#         partner_id=user_data['partner_id']
#     )

# @app.post("/token", response_model=Token)
# async def login_for_access_token(user_data: UserLogin):
#     # Authenticate user
#     user = odoo_auth.authenticate_user(user_data.email, user_data.password)
#     if not user:
#         # Try API authentication as fallback
#         user = odoo_auth.authenticate_via_odoo_api(user_data.email, user_data.password)
    
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     # Create access token
#     access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.email, "user_id": user.id},
#         expires_delta=access_token_expires
#     )
    
#     return Token(access_token=access_token, token_type="bearer")

# @app.get("/users/me", response_model=OdooUser)
# async def read_users_me(current_user: OdooUser = Depends(get_current_user)):
#     return current_user


# @app.get("/health")
# async def health_check():
#     """
#     Health check endpoint
#     """
#     try:
#         from app.services.database import get_db_connection
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT 1")
#         return {"status": "healthy", "database": "connected"}
#     except Exception as e:
#         return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
import logging

from app.services.database import init_database
from app.services.auth import auth, create_access_token, verify_token
from app.schemas.models import UserLogin, Token
from app.schemas.user import UserCreate, UserResponse  # ← UPDATE IMPORT
from app.core.config import settings
from app.core.security import get_current_user
from app.routes import candidate

import os
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_database()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(candidate.router, prefix=settings.API_V1_STR, tags=["candidates"])

# Security
security = HTTPBearer()

@app.post("/token", response_model=Token)
async def login_for_access_token(user_data: UserLogin):
    """Login and get JWT token"""
    # Authenticate user against standalone database
    user = auth.authenticate_user(user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user["id"]},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

@app.post("/register")
async def register_user(user_data: UserCreate):  # ← UPDATE: Gunakan Pydantic model
    """Register new user"""
    logger.info(f"Registration attempt for: {user_data.email}")
    
    result = auth.create_user(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User registration failed. Email or username may already exist."
        )
    
    return {
        "message": "User created successfully",
        "user": {
            "id": result["id"],
            "email": result["email"],
            "username": result["username"],
            "full_name": result["full_name"],
            "is_active": result["is_active"]
        }
    }

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        from app.services.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.execute("SELECT COUNT(*) as user_count FROM users")
        user_count = cursor.fetchone()['user_count']
        cursor.close()
        
        return {
            "status": "healthy", 
            "database": "connected",
            "users_count": user_count
        }
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)