CREATE OR REPLACE FUNCTION generate_insert_command(p_id NUMBER) RETURN VARCHAR2 IS
    v_val NUMBER;
    v_insert_command VARCHAR2(4000);
BEGIN
    -- Получаем значение val для указанного id из таблицы
    SELECT val INTO v_val
    FROM MyTable
    WHERE id = p_id;

    -- Формируем строку команды INSERT
    v_insert_command := 'INSERT INTO MyTable (id, val) VALUES (' || p_id || ', ' || v_val || ');';

    -- Выводим команду INSERT в консоль
    DBMS_OUTPUT.PUT_LINE(v_insert_command);

    -- Возвращаем сформированную команду
    RETURN v_insert_command;
END;
/

SET SERVEROUTPUT ON;  -- Включаем вывод на консоль

-- Вызов функции для id = 1
SELECT generate_insert_command(1) FROM dual;
