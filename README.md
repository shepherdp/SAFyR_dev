# SAFyR_dev

Author: Patrick Shepherd

Credit: [CodePulse](https://www.youtube.com/@CodePulse)

This repo houses the source code for SAFyR, my brand new programming language!  It is not ready for release yet, so expect bugs.  A new repo will be linked as soon as the production version is ready.  As of this moment I have no code in this repository, but I will within the next few days.  At the moment, I am busy: a) implementing the last of the BASIC features I want in the language (those being structs and when-triggers), and completing testing on the basic functionality.  I am not going for 100% on the testing, but I do want to test all the absolute core functionality down to the bone to make sure the language has a rock solid foundation with its building blocks.  From that point on, I will be treating the repo as any other open source project, and will be continuing development in branches into the future.  Feel free to reach out if you would like to contribute or have questions about the language.  This is my first attempt at creating a programming language in full, so be kind!

My main goal for SAFyR is to learn how to create a programming language.  That being said, I don't see why I can't explore the implementation of a wide range of features while I'm at it.  At its core, I would like SAFyR to be a fairly simple and lightweight language.  At the moment, I don't see implementing large projects in it.  It may evolve into something completely capable of that, though.  My second goal with this language is to be concise.  On the one hand, I want simple and easily readable syntax like is seen in Python (which incidentally is the language that SAFyR is being written in).

## List of Features to Implement Before Initial Release
* New operators (ex. `mylist </ 3` returns the first 3 elements of mylist, and `mylist /> 3` returns the last 3 elements)
* Multiple return values
* Middle ground between classes and structs; user-defined objects are structs by default, and you can attach any function you like to them without having to define those functions as class methods specifically, and then define how they interact with that function

## Some Planned Features of SAFyR
* Able to be interpreted or compiled (right now I plan to compile to LLVM bytecode)
* Errors as values (possibly)
* Native streamlined control flows for error handling

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

### Structs

Structs in SAFyR are, in their simplest form, collections of variables just like you would find in traditional C.  The syntax for creating a struct is the following:

    : optional TYPENAME \[ optional arguments \] {
        prop1 = arg1
        prop2 = arg2
        ...
    }

    ;; here is defined a new type called 'Fraction' that takes two parameters, a and b, and sets the
       instance properties, num and den, to those respective values.  I then create a variable
       called 'myfrac' of that type, and initialize it with the values 7 and 4. ;;
       
    :Fraction [a b] {
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

This behavior can also be used to override the functionality of built in operators (+, *, etc.).  For example, say that when we want to "add" an instance of `mytype` to something else, we really just want to add its `x` value.

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

#### When Triggers

Basic when syntax:

    when CONDITION : STATEMENT

or

    when CONDITION {
        STATEMENTS
    }

#### Functions

Basic function syntax:

    . FUNCNAME [ ARGS ] <~ STATEMENT

or

    . FUNCNAME [ ARGS ] <~ {
        STATEMENTS
    }

## Acknowledgements
My biggest thank you needs to go to the great mind behind [CodePulse](https://www.youtube.com/@CodePulse).  Before taking on this project, I had never built a programming language at all.  I had written some scripts that could parse and emulate Assembly, but that is a far stretch from a full high level language.  I found his series on YouTube about building your own programming language, and I followed it step by step so I could learn how the whole process works, so basically the entire skeleton of the language is his code.  Once I got done with his tutorial and I saw how everything fits together, I wanted to completely build out the language with many new features.  I have already learned a great deal about language design, and have come across some surprising facts in doing so (e.g. static vs. dynamic typing can literally be implemented with one single line of code).  I have also gotten the chance to get creative with parts of the implementation -- for one, I completely rewrote the lexer to be a finite state machine programmable via text file, so you can change the definitions of tokens at will.  I appreciate anyone who takes the time to learn my language, and accepts it for the learning journey it is.  Again, all credit for the foundations of this language belongs exclusively to CodePulse.  Thank you so much to him for helping me learn how all of this works, and I hope I can do his code justice by building something awesome on top of it!
