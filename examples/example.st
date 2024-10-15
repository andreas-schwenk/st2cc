PROGRAM Main
    VAR
        start_button_a AT %IX0.0: BOOL;
        start_button_b AT %IX0.1: BOOL;
        motor_output_a AT %QX0.0: BOOL;
        motor_output_b AT %QX0.1: BOOL;
    END_VAR
    // TODO: IF start_button_a OR start_button_b THEN
    IF start_button_a THEN
        motor_output_a := TRUE;
    ELSE
        motor_output_b := FALSE;
    END_IF
END_PROGRAM
