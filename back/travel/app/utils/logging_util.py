"""
Logging utility for audit trail functionality
Logs all operations to the audit_logs table
"""
from typing import Optional
from sqlalchemy import text
from app.core.database import engine
import json
import logging

logger = logging.getLogger(__name__)


async def log_operation(
    user_id: Optional[int],
    action: str,           # 'CREATE', 'READ', 'UPDATE', 'DELETE'
    resource_type: str,    # 'user', 'booking', 'payment', 'ticket'
    resource_id: Optional[int],
    method: str,           # 'GET', 'POST', 'PUT', 'DELETE', 'PATCH'
    status_code: int,
    details_json: Optional[dict] = None,
    ip_address: Optional[str] = None
) -> Optional[int]:
    """
    Log an operation to the audit_logs table via stored procedure
    
    Args:
        user_id: ID of the user performing the action (optional)
        action: Type of action (CREATE, READ, UPDATE, DELETE)
        resource_type: Type of resource being accessed
        resource_id: ID of the resource
        method: HTTP method (GET, POST, PUT, DELETE, PATCH)
        status_code: HTTP response status code
        details_json: Optional additional details (errors, metadata)
        ip_address: Client IP address (optional)
    
    Returns:
        Log entry ID if successful, None if error
    """
    try:
        with engine.connect() as conn:
            # Convert dict to JSON string if needed
            details_str = json.dumps(details_json) if details_json else None
            
            query = text("""
                SELECT booking.log_action(
                    :user_id, :action, :resource_type, :resource_id,
                    :method, :status_code, :details_json::jsonb, :ip_address
                )
            """)
            result = conn.execute(query, {
                'user_id': user_id,
                'action': action,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'method': method,
                'status_code': status_code,
                'details_json': details_str,
                'ip_address': ip_address
            })
            conn.commit()
            log_id = result.scalar()
            return log_id
    except Exception as e:
        # Log error but don't raise - logging failure shouldn't break the app
        logger.error(f"Failed to log operation: {str(e)}", exc_info=True)
        return None


def map_http_method_to_action(http_method: str) -> str:
    """
    Map HTTP method to audit action type
    
    Args:
        http_method: HTTP method (GET, POST, PUT, DELETE, PATCH)
    
    Returns:
        Action type (CREATE, READ, UPDATE, DELETE)
    """
    mapping = {
        'POST': 'CREATE',
        'GET': 'READ',
        'PUT': 'UPDATE',
        'PATCH': 'UPDATE',
        'DELETE': 'DELETE'
    }
    return mapping.get(http_method, 'READ')
