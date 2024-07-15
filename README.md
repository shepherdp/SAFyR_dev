# SAFyR_dev

Author: Patrick Shepherd
Credit: [CodePulse](https://www.youtube.com/@CodePulse)

This repo houses the source code for SAFyR, my brand new programming language!  It is not ready for release yet, so expect bugs.  A new repo will be linked as soon as the production version is ready.  Feel free to reach out if you would like to contribute or have questions about the language.  This is my first attempt at creating a programming language in full, so be kind!

My main goal for SAFyR is to learn how to create a programming language.  That being said, I don't see why I can't explore the implementation of a wide range of features while I'm at it.  At its core, I would like SAFyR to be a fairly simple and lightweight language.  At the moment, I don't see implementing large projects in it.  It may evolve into something completely capable of that, though.  My second goal with this language is to be concise.  On the one hand, I want simple and easily readable syntax like is seen in Python (which incidentally is the language that SAFyR is being written in).

## Some Planned Features of SAFyR
* Static and dynamic typing
* A range of different operators for objects that are not available in other languages, or rely on functions
* Able to be interpreted or compiled (right now I plan to compile to LLVM bytecode)
* Multiple return values (definitely)
* Errors as values (possibly)
* Native streamlined control flows for error handling
* Interchangeable keywords (e.g. 'if' can always be replaced with '?')
* A mashup of struct and class ideas.  All objects will be represented as structs, and can have their behavior relative to a given function defined, but there will not be 'methods' per se.  I am not sure if I will stick with this one or not...

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
