# SAFyR Changelog

## Release 0.9

The first public release of SAFyR is a proof-of-concept build.  Many of the basic ideas are laid out in this version, but much is left to be done.  In particular, the language needs several things before it can become a viable market product.  The major short-term top-priority work is:

- Refactor, reduce, and document everything implemented so far.
- Build a host of additional built-in functions and standard libraries.
- Increase testing.  Most basic functionality is tested right now, but many error conditions and edge cases still need to be checked specifically.
- Eliminate unnecessary inefficiencies in the current implementation (e.g. refactor if-elif*-else chains to switches).

Over time, I want to implement two major changes: I want the language to be compiled (possibly to LLVM, but maybe other formats), and I want to rewrite the interpreter in another language (Zig, Rust, Go, or Mojo most likely -- I've heard a lot about Odin though...).  For right now, though, the priority list above will be my main focus.  I still have to learn to make a compiler, so that could take a while to finish.  Also, a complete translation will take significant time, especially if working in a statically-typed language.  This puts Mojo toward the top of the list of candidates.

Since this is the first log, there are not any iterative changes to mention.  I will list an overview of features here, and then direct the reader to the 0.9 SAFyR Spec for complete implementation details.

