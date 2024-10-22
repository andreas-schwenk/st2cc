TYPE
    Point: STRUCT
        x: REAL;
        y: REAL;
    END_STRUCT;
END_TYPE

PROGRAM Main
    VAR
        p1: Point;
        p2: Point;
        distance: REAL;
    END_VAR

    p1.x := 3.0;
    p1.y := 4.0;

    p2.x := 6.0;
    p2.y := 8.0;

    distance := SQRT(POW(p2.x - p1.x, 2) + POW(p2.y - p1.y, 2));

END_PROGRAM
