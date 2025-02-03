CREATE OR REPLACE FUNCTION 
    calculate_total_salary(
        p_monthly_salary NUMBER, 
        p_annual_bonus_percentage NUMBER
        ) RETURN NUMBER IS
    v_total_salary NUMBER;
BEGIN

    IF p_monthly_salary <= 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Месячная зарплата должна быть положительным числом.');
    ELSIF p_annual_bonus_percentage < 0 THEN
        RAISE_APPLICATION_ERROR(-20002, 'Процент годовых премиальных не может быть отрицательным.');
    END IF;

    v_total_salary := (1 + p_annual_bonus_percentage / 100) * 12 * p_monthly_salary;


    RETURN v_total_salary;
EXCEPTION
    WHEN OTHERS THEN

        DBMS_OUTPUT.PUT_LINE('Ошибка: ' || SQLERRM);
        RETURN NULL;
END calculate_total_salary;
/



DECLARE

    v_salary NUMBER;
BEGIN

    v_salary := calculate_total_salary(60000, 10);  


    DBMS_OUTPUT.PUT_LINE('Общее вознаграждение за год: ' || v_salary);
END;

/
