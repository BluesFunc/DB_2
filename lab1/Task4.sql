
CREATE OR REPLACE FUNCTION generate_insert_command(p_id NUMBER) RETURN VARCHAR2 IS
    v_val NUMBER;
    v_insert_command VARCHAR2(4000);
BEGIN
   
    SELECT val INTO v_val
    FROM MyTable
    WHERE id = p_id;

    v_insert_command := 'INSERT INTO MyTable (id, val) VALUES (' || p_id || ', ' || v_val || ');';

    DBMS_OUTPUT.PUT_LINE(v_insert_command);

    RETURN v_insert_command;
END;
/


SELECT GENERATE_INSERT_COMMAND(2) FROM dual;
