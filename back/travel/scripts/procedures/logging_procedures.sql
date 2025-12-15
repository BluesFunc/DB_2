-- Audit Logging Procedures
-- Includes: 1 procedure for comprehensive audit logging

CREATE OR REPLACE FUNCTION booking.log_action(
    p_user_id BIGINT,
    p_action TEXT,
    p_resource_type TEXT,
    p_resource_id BIGINT,
    p_method TEXT,
    p_status_code INT,
    p_details_json JSONB DEFAULT NULL,
    p_ip_address TEXT DEFAULT NULL
)
RETURNS BIGINT AS $$
DECLARE
    v_log_id BIGINT;
BEGIN
    INSERT INTO booking.audit_logs 
        (user_id, action, resource_type, resource_id, method, status_code, details_json, ip_address)
    VALUES (p_user_id, p_action, p_resource_type, p_resource_id, p_method, p_status_code, p_details_json, p_ip_address)
    RETURNING id INTO v_log_id;
    
    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql;
