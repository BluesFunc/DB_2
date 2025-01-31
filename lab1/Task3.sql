CREATE OR REPLACE FUNCTION check_even_odd_count RETURN VARCHAR2 IS
    even_count NUMBER := 0;
    odd_count NUMBER := 0;
BEGIN
    -- Подсчитываем количество четных и нечетных значений в таблице MyTable
    FOR rec IN (SELECT val FROM MyTable) LOOP
        IF MOD(rec.val, 2) = 0 THEN
            even_count := even_count + 1; -- Четное число
        ELSE
            odd_count := odd_count + 1;  -- Нечетное число
        END IF;
    END LOOP;

    -- Определяем результат
    IF even_count > odd_count THEN
        RETURN 'TRUE';  -- Четных больше
    ELSIF even_count < odd_count THEN
        RETURN 'FALSE'; -- Нечетных больше
    ELSE
        RETURN 'EQUAL'; -- Количество одинаково
    END IF;
END;
/
SELECT check_even_odd_count FROM dual;