# SAFyR_dev

Author: Patrick Shepherd

Credit: [CodePulse](https://www.youtube.com/@CodePulse)

This repo houses the source code for SAFyR, my brand new programming language!  It is not ready for release yet, so expect bugs.  A new repo will be linked as soon as the production version is ready.  As of this moment I have no code in this repository, but I will within the next few days.  At the moment, I am busy: a) implementing the last of the BASIC features I want in the language (those being structs and when-triggers), and completing testing on the basic functionality.  I am not going for 100% on the testing, but I do want to test all the absolute core functionality down to the bone to make sure the language has a rock solid foundation with its building blocks.  From that point on, I will be treating the repo as any other open source project, and will be continuing development in branches into the future.  Feel free to reach out if you would like to contribute or have questions about the language.  This is my first attempt at creating a programming language in full, so be kind!

My main goal for SAFyR is to learn how to create a programming language.  That being said, I don't see why I can't explore the implementation of a wide range of features while I'm at it.  At its core, I would like SAFyR to be a fairly simple and lightweight language.  At the moment, I don't see implementing large projects in it.  It may evolve into something completely capable of that, though.  My second goal with this language is to be concise.  On the one hand, I want simple and easily readable syntax like is seen in Python (which incidentally is the language that SAFyR is being written in).

## Some Planned Features of SAFyR
* Able to be interpreted or compiled (right now I plan to compile to LLVM bytecode)
* Errors as values (possibly)
* Native streamlined control flows for error handling
* Multiple return values
* Calling functions as methods

## Coding in SAFyR
Here is some basic functionality for SAFyR.  This part of the document will be continually updated as new features are implemented and tested.

### Comments
Single-line comments in SAFyR start with `;`.  Anything from a single semicolon to a newline character will be entirely ignored at the level of the lexer.  Multi-line comments are also supported, but are enclosed at the beginning and end by `;;`.  Here is a quick example:

    ; this is a comment that ends as soon as I go to the next line
    ;; this is a comment that can just go on and on
       and on and on
       and on and on

       and on until I close it with these two semicolons ;;

### Variables
Variables come in all the typical flavors:

* Integer    (INT)
* Float      (FLT)
* String     (STR)
* List       (LST)
* Map        (MAP)

Variables can also be instances of functions or custom structs.  Initializing a variable works very similarly to other languages:
    
    a = 5              ; a is an integer with value 5
    b = 10.            ; b is a float with value 10.0
    c = "a string"     ; c is a string with the text "a string"
    d = [1 2]          ;; d is a list containing the values 1 and 2.
                          note that values are whitespace-separated, NOT comma-separated ;;

SAFyR is a dynamically typed language by default.  This means any variable can take on any value.  Even if you initialize a variable to an integer value, for instance, you can reassign it to a string on the next line.  This default can be toggled on and off.  Using a statement at the top of your main file will instead set the environment to be statically-typed by default.  Within either of these conditions, variables can be explicitly initialized as either statically or dynamically typed.  Here are some examples:

    ;; no keyword at top, so file is dynamically typed by default ;;
    
    a = 5              ; a is a dynamically typed integer 
    int b = 5          ; b is a statically typed integer
    a = "Hello"        ; a changes to a string
    b = "Hello"        ; b throws an error because "Hello" is not an int
    b = 5.75           ; b will now equal the integer 5 due to truncation as a result of static typing

In the example above, no keyword was provided at the top of the file for static typing, so variables are assumed to be dynamic unless specified otherwise with the type enclosed in `<>` preceding the variable name.

    ;; static keyword invoked at top, so file is statically typed by default ;;
    
    use static

    a = 5              ; a is a statically typed integer 
    var b = 5          ; b is a dynamically typed integer
    a = "Hello"        ; a throws an error because "Hello" is not an int
    b = "Hello"        ; b changes to a string

In this example, including the line `use static` at the top of the file enforces automatic static typing for all variables.  If you do want a dynamically typed variable, then you initialize it with `var` before the name.  The same will be true of container data structures -- lists, maps, etc. can hold any collection of elements of any type by default, but you can also enforce lists containing only elements of a single type, or that maps can only accept keys and values of certain types.

Variables can also be defined as constant with the `const` keyword preceding the optional variable type.  Doing so will cause any and all attempts to assign a value to that variable to throw an error, even if you are only assigning the exact same value to that variable.

    const int a = 5    ; a is a constant integer equal to 5
    a = 10             ; a throws an error because it is constant
    a = 5              ; a will still throw an error, even if its value would not change

A variable type keyword and/or constant keyword can only be used at initialization.  Any attempt to prefix an existing identifier with one of these specifiers results in an error.  Using a specifier that does not match any inferred type of the literal value will also result in an error.  For example:

    int a = "a string" ; a throws an error because the string value will not automatically cast to int
    int a = 5.75       ; a is an integer with the value 5 due to truncation

A variable initialization preceded by the `global` keyword are added to the interpreter's list of global variables, and thus are available from within any scope in the program.

    global a = 12      ; the value of a can be accessed from all scopes

### Operators
SAFyR provides all the typical operators for a programming language (+, -, *, /, %, and ^ for exponentiation, as well as the same operators followed by '=') as well as a few others.  The '@' operator is used for element access (equivalent to the `[idx]` in `mylist[idx]`), and can be used on any data type.  Lists and strings also have access to the 'sliceleft' and 'sliceright' (`</` and `/>`)operators, which allow you to grab the leftmost or rightmost portions of the value.  Lists and strings also have specific behaviors relative to many of the basic operators.

    # operator examples
    a = 5
    b = a + 6          ; b = 11; all basic operators work as expected on numbers
    b += 9             ; b = 20; accumulation operators also work as expected

    a = [1 2 3]        ; a is a list of ints
    a = a + 4          ; a = [1 2 3 4]; + appends an element to a list
    a = a + [7 8]      ; a = [1 2 3 4 [7 8]]; any element can be appended to a list

    a = [1 2 3]
    a -= 2             ; a = [1 3]; subraction removes an element from a list
    a = [1 2 2 2 3]
    a = a - 2          ; a = [1 3]; subtraction removes all instances of an element from a list

    a = [1 2]
    b = [3 4]
    c = a * b          ; c = [[1 3] [2 4]]; multiplication zips two lists (must be the same size)

    a = [1 2 3 2 4]
    b = a / 2          ; b = [[1 2] [3 2] [4]]; division splits list based on operand value

    a = [1 2 3 4 5]
    b = a </ 2         ; b = [1 2]; splits off the specified amount of elements from the left of a list

    a = [1 2 3 4 5]
    b = a /> 2         ; b = [4 5]; splits off the specified amount of elements from the right of a list

    a = [1 2]
    b = [3 4]
    c = a ^ b          ; c = [[1 3] [1 4] [2 3] [2 4]]; exponentiation returns the cartesian product of two lists

    a = [1 2 3]
    b = a @ 1          ; @ is the index operator, so b = 2

    a = {1: "a"        ; a is a dictionary with keys 1 and "b", and values "a" and 2
         "b": 2}
    b = a + {"3": "c"} ; b = {1: "a"
                              "b": 2
                              "3": "c"} because addition adds a new key-value pair to a map

    a = "abc"          ; a is string
    a = a + "de"       ; addition concatenates strings, so a = "abcde"

    a = "abaca"
    a = a - "a"        ; subtraction removes substrings, so a = "bc"

    a = "ab"
    a = a * 3          ; multiplication multiplies strings, so a = "ababab"

    a = "bbabcabd"
    a = a / "a"        ; division splits on substrings, so a = ["bb" "bc" "bd"]

    a = "bbaf"
    b = a @ 3          ; @ is the index operator, so b = "f"
    b = a @ (-2)       ; indexing also works with negative integers, so b = "a"

### Basic Control Flow

#### Conditionals

SAFyR supports traditional keywords for branching: `if`, `elif`, and `else`.  However, there is also a shorthand method of using these operators: `?`, `!?`, and `!`.  Any or all of these statements can occupy one or more lines, and an entire set of conditionals can be placed on the same line.  For instance:

    ; Implementation 1
    a = 5
    if a < 5: a = "less" elif a > 7: a = "more" else a = "good"
    print(a)

    ; Implementation 2
    a = 5
    if a < 5 {
        a = "less" }
    elif a > 7 {
        a = "more" }
    else {
        a = "good" }
    print(a)

    ; Implementation 3
    a = 5
    ? a < 5: a = "less" !? a > 7: a = "more" ! a = "good"
    print(a)

    ; All of the above implementations provide the following output:
    >>> "good"

*NOTE: multi-statement bodies are placed inside curly braces.  The opening brace must be on the same line as the corresponding keyword and condition and then followed by a newline.*

#### While Loops

Basic while syntax:

    while CONDITION : STATEMENT

or

    while CONDITION {
        STATEMENTS
    }

While loops behave in the typical fashion: the statements inside the body of the loop execute repeatedly until the condition becomes true.  For example:

    a = 5
    while a < 10: a += 1
    print(a)
    >>> 10

    a = 5
    while a < 10 {
        a += 1
        print(a)
    }
    
    >>> 6
    >>> 7
    >>> 8
    >>> 9
    >>> 10

#### For Loops

Basic for loop syntax:

    for VARNAME = INT .. INT [.. INT] : STATEMENT

or

    for VARNAME = INT .. INT [.. INT] {
        STATEMENTS
    }

Each `for` keywword is followed by a variable name to use as the index of iteration, and then an integer starting index, a double-dot operator, an integer (exclusive) ending index, and then an optional double-dot operator followed by an integer step value.

The body of the for loop follows a colon if it is a single statement, and inside curly braces if more.

    for i == 0 .. 3: print(i)
    
    >>> 0
    >>> 1
    >>> 2

    for i = 10 .. 15 .. 2 {
        a += 1
        print(a)
    }
    
    >>> 10
    >>> 12
    >>> 14

*NOTE: determination of numerical types (e.g. integer and float) are performed IN THE LEXER.  If you write your for loop declaration as 'for i = 0..2', then SAFyR will interpret that line of code as '`for i = 0.0 2.0`' and will throw an error. Dots MUST be separated from numerical characters by whitespace.*

#### Foreach Loops

Foreach is the iterator loop in SAFyR.  Syntactically, this is implemented the same as in Python.  Currently there is only support for iterating over containers (lists, maps, strings), but support for iterating structs will be implemented in the near future.  Each `foreach` keywword is followed by a variable name to use as the object of iteration, then the keyword `in`, and finally a container for that variable to take on values from.  The body of the foreach loop follows a colon if it is a single statement, and inside curly braces if more.

Basic foreach loop syntax:

    foreach VARNAME in CONTAINER : STATEMENT

or

    foreach VARNAME in CONTAINER {
        STATEMENTS
    }

Example:

    a = [1 2 3]
    foreach num in a: print(num)

    >>> 1
    >>> 2
    >>> 3

    a = {"a": 123
         "b": 456
         "c": 789}
    foreach key in a {
        print(key)
    }

    >>> "a"
    >>> "b"
    >>> "c"

    foreach key in a {
        print(a @ key)
    }

    >>> 123
    >>> 456
    >>> 789

#### When Triggers

When triggers are used like event-based callbacks.  Many times in programming, if you need something to happen until a certain condition is met, you use a while loop that ends upon the satisfaction of that condition.  Other times, there is only a single task you want to execute at the moment some condition becomes true, and possibly never again.  This is the purpose of the when trigger.

Basic when syntax:

    when CONDITION : STATEMENT

or

    when CONDITION {
        STATEMENTS
    }

Example:

    a = b = 0
    when a == 10: b = 50

    while b < 50: a += 1

    print(a)
    print(b)

    >>> 10
    >>> 50

In the example above, both `a` and `b` are initialized to zero, and then a loop is started that will continually add one to `a` until `b` becomes at least 50.  The loop would run for 10 iterations, adding one to `a` each time, until the `when` condition is met.  As soon as it is, its body of statements is called, in this case simply setting `b` to 50.  As soon as `a` takes on the value 10, `b` takes on the value 50, and the loop is terminated.

By default, any `when` trigger will persist, and will fire every time the condition becomes true.  Adding the `once` keyword inside the body of your trigger deletes it after it executes the first time.

    ; when trigger without the once keyword
    
    a = b = 0
    when a == 10: b = 50
    while b < 50: a += 1
    print(a)
    print(b)

    >>> 10
    >>> 50

    a = b = 0                ; reset a and b
    while b < 50: a += 1     ; run the while loop again
    print(a)
    print(b)

    >>> 10                   ; same result as before
    >>> 50

    ; when trigger with the once keyword

    a = b = 0
    when a == 10 {
        b = 50
        once
    }
    while b < 50: a += 1
    print(a)
    print(b)

    >>> 10
    >>> 50

    a = b = 0                ; reset a and b
    while b < 50: a += 1     ; this loop will run forever because 'b = 50' does not happen again

### Functions

Basic function syntax:

    . optional FUNCNAME [ optional ARGS ] <~ STATEMENT

or

    . optional FUNCNAME [ optional ARGS ] <~ {
        STATEMENTS
    }

Functions can be defined with names, or as anonymous functions that can be stored as elements in a container or properties in a struct.  All functions can take zero or more arguments.  Single-line function definitions automatically return the statement on the right side of the `<~` operator, so no `return` keyword is necessary.  Multiline functions MUST have a return keyword in order to return a value.

    : addTwoNumbers [a b] <~ a + b

    myvar = addTwoNumbers(1 2)
    print(myvar)

    >>> 3

    : addTwoNumbers [a b] <~ {
        a = a + b
    }

    myvar = addTwoNumbers(1 2)
    print(myvar)

    >>> 0                            ; default null value is 0

    : addTwoNumbers [a b] <~ {
        a = a + b
        return a
    }

    myvar = addTwoNumbers(1 2)
    print(myvar)

    >>> 3

#### Defer

In SAFyR, the `defer` keyword can be invoked at any time within a function definition, and followed either by a color and a single statement on one line, or multiple statements surrounded by curly braces.  Any statements within a `defer` block will execute immediately prior to the function's `return` statement.  For example:

    : doThings [] <~ {
    
        defer: del first                ; this statement will not execute here...
        first = 1 + 2
        second = 2 + 3
        third = 3 + 4

        ; ...it will execute here instead

        return "success"
    }

or

    : doThings [] <~ {
    
        defer {
            del first
            del second
            del third
        }
        
        first = 1 + 2
        second = 2 + 3
        third = 3 + 4

        return "success"
    }

### Structs

Structs in SAFyR are, in their simplest form, collections of variables just like you would find in traditional C.  The syntax for creating a struct is the following:

    :: optional TYPENAME \[ optional arguments \] {
        prop1 = arg1
        prop2 = arg2
        ...
    }

    ;; here is defined a new type called 'Fraction' that takes two parameters, a and b, and sets the
       instance properties, num and den, to those respective values.  I then create a variable
       called 'myfrac' of that type, and initialize it with the values 7 and 4. ;;
       
    :: Fraction [a b] {
        num = a
        den = b
    }

    myfrac = Fraction(7 4)
    print(myfrac)

    >>> <struct Fraction> {'num': 7, 'den': 4}

#### Struct Function Proxies

SAFyR implements only a light natural melding of structs and functions.  For instance, structs cannot have dedicated methods.  Instead, SAFyR provides a way to control the inputs a struct gives to a function when it is passed as an argument.  For example, we might want to define a `printall` function that will iterate through a container object and print out each value on its own line.  That function would look like this:

    : printall [ mylist ] <~ {
        foreach i in mylist: print(i)
    }

This function takes a list or other iterable container as input, and prints each element on its own line.  We might also have a struct type `mytype` that has three attributes: `x`, `y`, `z`.  For this example, say we want `x` and `y` to be simple integers, but we want `z` to be a list.  That struct definition would look like this:

    :: mytype [a b c] {
        x = a
        y = b
        z = c
    }

Perhaps we want a quick shorthand to pass the `z` property of any `mytype` variable we have into the `printall` function instead of having to refer to `mytype.z` directly.  This can be implemented with function proxies in the following way:

    : printall [ mylist ] <~ {
        foreach i in mylist: print(i)
    }

    :: mytype [a b c] {
        x = a
        y = b
        z = c

        .printall <~ z            ;; we add the proxy here, and tell the printall function that any time it sees a mytype
    }                                object as input, take its z property as input instead ;;

    myvar = mytype( 1 2 [7 8 9] )
    printall(myvar)

    >>> 7
    >>> 8
    >>> 9

This behavior can also be used to override the functionality of built in operators (+, *, etc.).  For example, say that when we want to "add" an instance of `mytype` to something else, we really just want to add its `x` value.  The only operator that cannot be overridden in this way is '='.

    :: mytype [a b c] {
        x = a
        y = b
        z = c

        .+ <~ z            ; we add the proxy here, and tell the + operator that any time it sees a mytype
    }                         object an operand, take its x property as input instead ;;

    a = mytype(1 2 3)
    print(a + 6)           ; a's x property is equal to 1, so that is what 6 gets added to
    >>> 7

    c = mtype(4 5 6)
    print(a + c)           ; a's x property is equal to 1, and c's is equal to 4, resulting in 5
    >>> 5

## Grammar

* capitalized string: production
* lowercase string: keyword, operator, or object
* "*": zero or more
* "?": optional
* "|": multiple possible syntaxes

.SAFyR OFFICIAL GRAMMAR

    STATEMENTS  : newline* STATEMENT (newline STATEMENT)* newline*

    STATEMENT   : use IDENTIFIER
                : continue
                : break
                : return EXPR?
                : del IDENTIFIER
                : once            
                : EXPR

    EXPR        : FUNCDEF
                : STRUCTDEF
                : PROXY
                : const? static? global? TYPE? IDENTIFIER ASG EXPR
                : COMP ((LOGICAL) COMP)* (ASG EXPR)?

    COMP        : not COMP
                : ARITH (COMPARE ARITH)*

    ARITH       : TERM ((pls | mns) TERM)*

    TERM        : FACTOR ((mul | div | mod) FACTOR)*

    FACTOR      : (pls | mns) FACTOR
                : POWER

    POWER       : INDEX (pow FACTOR)*

    INDEX       : PROPERTY ((IDXOP) PROPERTY)*

    PROPERTY    : CALL (dot ATOM)*

    CALLL        : ATOM (lpar (EXPR (EXPR)*)? rpar)?

    ATOM        : lit | IDENTIFIER
                : lpar EXPR rpar
                : LIST
                : MAP
                : IFEXPR
                : FOREXPR
                : FOREACHEXPR
                : WHILEEXPR
                : WHENEXPR
                : TRYEXPR
                : FUNC
                : STRUCT
                : DEFER

    LIST        : lbr ((EXPR)*)? rbr

    MAP         : lcr ((EXPR cln EXPR)*)? rcr

    IFEXPR      : (if | ?) EXPR
                    cln STATEMENT (IFEXPRB | IFEXPRC)?
                    | (if | ?) EXPR lcr NEWLINE STATEMENTS rcr (IFEXPRB | IFEXPRC)?

    IFEXPRB     : (elif | !?) EXPR
                    cln STATEMENT (IFEXPRB | IFEXPRC)?
                    | (if | ?) EXPR lcr NEWLINE STATEMENTS rcr IFEXPRB* (IFEXPRC)?

    IFEXPRC     : (else | !)
                    cln STATEMENT
                    | NEWLINE STATEMENTS rcr

    FOREXPR     : for IDENTIFIER eq EXPR ddot EXPR (ddot EXPR)? 
                    cln STATEMENT
                    | lcr NEWLINE STATEMENTS rcr

    FOREACHEXPR : for IDENTIFIER in EXPR
                    cln STATEMENT
                    | lcr NEWLINE STATEMENTS rcr

    WHILEEXPR   : while EXPR
                  cln statement
                  | lcr NEWLINE STATEMENTS rcr

    WHILEEXPR   : when EXPR
                    cln statement
                    | lcr NEWLINE STATEMENTS rcr

    FUNCDEF     : cln IDENTIFIER? lbr (IDENTIFIER*)? inj lcr NEWLINE STATEMENTS rcr

    STRUCTDEF   : dcln IDENTIFIER lbr (IDENTIFIER*)? rbr lcr NEWLINE STATEMENTS rcr

    DEFER       : defer
                    cln statement
                    | lcr NEWLINE STATEMENTS rcr

    PROXY       : dot IDENTIFIER inj EXPR

    TRYEXPR     : try
                    cln STATEMENT NEWLINE CATCHEXPR
                    | lcr NEWLINE STATEMENTS rcr CATCHEXPR

    CATCHEXPR   : catch
                    cln STATEMENT
                    | lcr NEWLINE STATEMENTS rcr
    

    Tokens / Keywords
                : Name   : Token
    ASG         : asg    : =       ; basic assignment
                : xpls   : +=      ; augmented addition
                : xmns   : -=      ; augmented subtraction
                : xmul   : *=      ; augmented multiplication
                : xdiv   : /=      ; augmented division
                : xmod   : %=      ; augmented modulus
                : xpow   : ^=      ; augmented exponent

    LOGICAL     : and    : &
                : or     : |
                : not    : ~
                : nand   : ~&
                : nor    : ~|
                : xor    : ><
                
    COMPARE     : eq     : ==
                : ne     : !=
                : lt     : <
                : le     : <=
                : gt     : >
                : ge     : >=

    IDXOP       : lslc   : </
                : rslc   : />
                : at     : @

    IF          : if
                : ?

    ELIF        : elif
                : !?

    ELSE        : else
                : !

    TYPE        : var
                : int
                : flt
                : str
                : lst
                : map

    OTHERS      : dot    : .        ; properties are accessed with dot
                : ddot   : ..       ; double dot operators are used in for loop declarations
                : dcln   : ::       ; struct definitions begin with double colon
                : cln    : :
                : inj    : <~
                : lpar   : (
                : rpar   : )
                : lbr    : \[
                : rbr    : \]
                : lcr    : {
                : rcr    : }
                : lit               ; a literal value like an integer or string

## Acknowledgements
My biggest thank you needs to go to the great mind behind [CodePulse](https://www.youtube.com/@CodePulse).  Before taking on this project, I had never built a programming language at all.  I had written some scripts that could parse and emulate Assembly, but that is a far stretch from a full high level language.  I found his series on YouTube about building your own programming language, and I followed it step by step so I could learn how the whole process works, so basically the entire skeleton of the language is his code.  Once I got done with his tutorial and I saw how everything fits together, I wanted to completely build out the language with many new features.  I have already learned a great deal about language design, and have come across some surprising facts in doing so (e.g. static vs. dynamic typing can literally be implemented with one single line of code).  I have also gotten the chance to get creative with parts of the implementation -- for one, I completely rewrote the lexer to be a finite state machine programmable via text file, so you can change the definitions of tokens at will.  I appreciate anyone who takes the time to learn my language, and accepts it for the learning journey it is.  Again, all credit for the foundations of this language belongs exclusively to CodePulse.  Thank you so much to him for helping me learn how all of this works, and I hope I can do his code justice by building something awesome on top of it!
