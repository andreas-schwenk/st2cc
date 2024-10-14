PROGRAM Main
    VAR
        start_button_a AT %IX0.0: BOOL;
        start_button_b AT %IX0.1: BOOL;
        motor_output AT %QX1.0: BOOL;
    END_VAR
    IF start_button_b OR start_button_b THEN
        motor_output := TRUE;
    ELSE
        motor_output := FALSE;
    END_IF
END_PROGRAM
