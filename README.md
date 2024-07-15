# SAFyR_dev

Author: Patrick Shepherd

Credit: [CodePulse](https://www.youtube.com/@CodePulse)

This repo houses the source code for SAFyR, my brand new programming language!  It is not ready for release yet, so expect bugs.  A new repo will be linked as soon as the production version is ready.  Feel free to reach out if you would like to contribute or have questions about the language.  This is my first attempt at creating a programming language in full, so be kind!

My main goal for SAFyR is to learn how to create a programming language.  That being said, I don't see why I can't explore the implementation of a wide range of features while I'm at it.  At its core, I would like SAFyR to be a fairly simple and lightweight language.  At the moment, I don't see implementing large projects in it.  It may evolve into something completely capable of that, though.  My second goal with this language is to be concise.  On the one hand, I want simple and easily readable syntax like is seen in Python (which incidentally is the language that SAFyR is being written in).

## List of Features to Implement Before Initial Release
* Programs include variable-specific static and and dynamic typing
* New operators (ex. mylist </ 3 returns the first 3 elements of mylist, and mylist </ 3returns the last 3 elements)
* Multiple return values
* All keywords have full versions as well as shorthand versions (e.g. if, elif, and else can be replaced with ?, !?, and ! at will)
* Middle ground between classes and structs; user-defined objects are structs by default, and you can attach any function you like to them without having to define those functions as class methods specifically, and then define how they interact with that function

## Some Planned Features of SAFyR
* Able to be interpreted or compiled (right now I plan to compile to LLVM bytecode)
* Errors as values (possibly)
* Native streamlined control flows for error handling

## Coding in SAFyR
Here is some basic functionality for SAFyR.  This part of the document will be continually updated as new features are implemented and tested.

### Variables
Right now, variables are all dynamically typed, and types are assumed from values.
    
    a = 5              # a is an integer with value 5
    a = 10.            # now a is a float with value 10.0

In the future, variable assignment will look the same, but also different.  By default, the language will assume that everything is to be dynamically typed, but you can use a keyword to change that default to static typing.  You will still be able to create dynamically typed variables under the static-type setting, and you will be able to create statically typed variables in the dynamic-type setting.  Here is how that might look:

    a = 5              # a is a dynamically typed integer 
    <int> b = 5        # b is a statically typed integer
    a = "Hello"        # a changes to a string
    b = "Hello"        # b throws an error because "Hello" is not an int

In the example above, no keyword was provided at the top of the file for static typing, so variables are assumed to be dynamic unless specified otherwise with the type enclosed in `<>` preceding the variable name.

    use static

    a = 5              # a is a statically typed integer 
    <var> b = 5        # b is a dynamically typed integer
    a = "Hello"        # a throws an error because "Hello" is not an int
    b = "Hello"        # b changes to a string

In this example, including the line `use static` at the top of the file enforces automatic static typing for all variables.  If you do want a dynamically typed variable, then you initialize it with `<var>` before the name.  The same will be true of container data structures -- lists, maps, etc. can hold any collection of elements of any type by default, but you can also enforce lists containing only elements of a single type, or that maps can only accept keys and values of certain types.  I believe this will be convenient because, in many applications, there are variables that you expect to have a specific structure and/or format, and it is nice to be able to enforce that structure, but other times you just need variables that can be whatever for a while.  I believe that creating a language that incorporates both will be advantageous, and time will tell if I am correct.

### Builtin Types

SAFyR has typical builtin types:
* Integer    (INT)
* Float      (FLT)
* String     (STR)
* List       (LST)
* Map        (MAP)

### Operators
SAFyR provides all the typical operators for a programming language (+, -, *, /, %, and ^ for exponentiation, as well as the same operators followed by '=') as well as a few others.  The '@' operator is used for element access (equivalent to the `[idx]` in `mylist[idx]`), and can be used on any data type.  Lists and strings also have access to the 'sliceleft' and 'sliceright' (`</` and `/>`)operators, which allow you to grab the leftmost or rightmost portions of the value.  Lists and strings also have specific behaviors relative to many of the basic operators.

    # operator examples
    a = 5
    b = a + 6          # b = 11; all basic operators work as expected on numbers
    b += 9             # b = 20; accumulation operators also work as expected

    a = [1 2 3]        # a is a list of ints
    a = a + 4          # a = [1 2 3 4]; + appends an element to a list
    a = a + [7 8]      # a = [1 2 3 4 [7 8]]; any element can be appended to a list

    a = [1 2 3]
    a -= 2             # a = [1 3]; subraction removes an element from a list
    a = [1 2 2 2 3]
    a = a - 2          # a = [1 3]; subtraction removes all instances of an element from a list

    a = [1 2]
    b = [3 4]
    c = a * b          # c = [[1 3] [2 4]]; multiplication zips two lists (must be the same size)

    a = [1 2 3 2 4]
    b = a / 2          # b = [[1] [3] [4]]; division splits list based on operand value

    c = a ^ b          # c = [[1 3] [1 4] [2 3] [2 4]]; exponentiation returns the cartesian product of two lists


## Acknowledgements
My biggest thank you needs to go to the great mind behind [CodePulse](https://www.youtube.com/@CodePulse).  Before taking on this project, I had never built a programming language at all.  I had written some scripts that could parse and emulate Assembly, but that is a far stretch from a full high level language.  I found his series on YouTube about building your own programming language, and I followed it step by step so I could learn how the whole process works, so basically the entire skeleton of the language is his code.  Once I got done with his tutorial and I saw how everything fits together, I wanted to completely build out the language with many new features.  I have already learned a great deal about language design, and have come across some surprising facts in doing so (e.g. static vs. dynamic typing can literally be implemented with one single line of code).  I have also gotten the chance to get creative with parts of the implementation -- for one, I completely rewrote the lexer to be a finite state machine programmable via text file, so you can change the definitions of tokens at will.  I appreciate anyone who takes the time to learn my language, and accepts it for the learning journey it is.  Again, all credit for the foundations of this language belongs exclusively to CodePulse.  Thank you so much to him for helping me learn how all of this works, and I hope I can do his code justice by building something awesome on top of it!
