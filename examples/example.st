PROGRAM Main
    VAR
        start_button: BOOL;
        motor_on: BOOL;
        temp_sensor: INT;
        valve_ctrl: INT;
    END_VAR
    IF start_button THEN
        motor_on := TRUE;
    ELSE
        motor_on := FALSE;
    END_IF
    valve_ctrl := temp_sensor * 2;
END_PROGRAM

// TODO
// StartButton AT %I0.0: BOOL;
// MotorOn AT %Q0.0: BOOL;
// TempSensor AT %IW2: REAL;
// ValveCtrl AT %QW4: REAL;
