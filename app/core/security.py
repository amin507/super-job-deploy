from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth import verify_token
from app.schemas.models import OdooUser

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token_data = verify_token(credentials.credentials)
    
    # Verify user still exists in Odoo
    from app.services.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT u.id as user_id, u.login as email, p.name as name, p.id as partner_id
    FROM res_users u
    JOIN res_partner p ON u.partner_id = p.id
    WHERE u.id = %s AND u.active = true
    """
    
    cursor.execute(query, (token_data.user_id,))
    user_data = cursor.fetchone()
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return OdooUser(
        id=user_data['user_id'],
        name=user_data['name'],
        email=user_data['email'],
        partner_id=user_data['partner_id']
    )