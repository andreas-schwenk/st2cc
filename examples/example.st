PROGRAM Main
    VAR
        start_button AT %IX0.0: BOOL;
        motor_output AT %QX1.0: BOOL;
    END_VAR
    IF start_button THEN
        motor_output := TRUE;
    ELSE
        motor_output := FALSE;
    END_IF
END_PROGRAM
