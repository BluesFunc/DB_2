CREATE OR REPLACE PROCEDURE insert_my_table(p_val NUMBER) IS
BEGIN
    INSERT INTO MyTable (id, val)
    VALUES (MY_SEQUENCE.NEXTVAL, p_val);

    COMMIT; 
END insert_my_table;
/

CREATE OR REPLACE PROCEDURE update_my_table(p_id NUMBER, p_new_val NUMBER) IS
BEGIN
    UPDATE MyTable
    SET val = p_new_val
    WHERE id = p_id;

    IF SQL%ROWCOUNT = 0 THEN
        DBMS_OUTPUT.PUT_LINE('Строка с id ' || p_id || ' не найдена.');
    ELSE
        COMMIT; 
    END IF;
END update_my_table;
/

CREATE OR REPLACE PROCEDURE delete_my_table(p_id NUMBER) IS
BEGIN
    DELETE FROM MyTable
    WHERE id = p_id;

    IF SQL%ROWCOUNT = 0 THEN
        DBMS_OUTPUT.PUT_LINE('Строка с id ' || p_id || ' не найдена для удаления.');
    ELSE
        COMMIT;  
    END IF;
END delete_my_table;
/

EXEC insert_my_table(200);

EXEC update_my_table(1, 200);


EXEC delete_my_table(1);

SELECT * FROM MYTABLE;
