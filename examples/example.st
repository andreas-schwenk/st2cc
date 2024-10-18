PROGRAM Main
    VAR
        sensor0 AT %IX0.0: BOOL;
        sensor1 AT %IX0.1: BOOL;
        sensor2 AT %IX0.2: BOOL;
        actuator0 AT %QX0.0: BOOL;
        actuator1 AT %QX0.1: BOOL;
    END_VAR
    IF sensor0 OR (sensor1 AND sensor2) THEN
        actuator0 := TRUE;
        actuator1 := TRUE;
    ELSE
        actuator0 := FALSE;
        actuator1 := FALSE;
    END_IF
END_PROGRAM
