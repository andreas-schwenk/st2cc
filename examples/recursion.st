PROGRAM Main
    VAR
        n AT %IW0: INT;
        result AT %QW0: INT;
    END_VAR
    result := Factorial(n);
END_PROGRAM

FUNCTION Factorial: INT
    VAR_INPUT
        num: INT;
    END_VAR
    IF num <= 1 THEN
        Factorial := 1;
    ELSE
        Factorial := num * Factorial(num - 1);
    END_IF
END_FUNCTION
