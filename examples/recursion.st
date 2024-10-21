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


(* SYMBOL TABLE

@program
    # IDENTIFIER SCOPE BASE DIM ADDRESS
    n local int None IW0
    result local int None QW0
    Factorial function int None None

@Factorial:
    num param int None None

 *)



(*
file
    program
        variables
            variable
                n
                base
                    int
                addr
                    IW0
            variable
                result
                base
                    int
                addr
                    QW0
        statements
            assign
                variable
                    result
                call
                    Factorial
                    args
                        var
                            n
    function
        Factorial
            variables
                input_variable
                    num
                    base
                        int
        if
            less_equal
                variable
                    num
                int
                    1
            assign
                ...
 *)
