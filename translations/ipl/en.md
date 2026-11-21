---
title: "An interpreter with customizable syntax"
summary: "Bachelor's project — a cross-platform interpreter whose keywords and grammar are configurable."
source: favorart/IPL@master:docs/ru/README.md
source_lang: ru
source_hash: 22e15939
translated: 2026-11-21
translator: Claude
reviewed: 2026-11-21
---
# An interpreter for an interpreted programming language with customizable syntax

[Kirill Anatolyevich Golikov](https://github.com/favorart)

Academic supervisor: [Pavel Aleksandrovich Aliseychik](http://intsys.msu.ru/staff/aliseychik/){: hreflang=ru }

Lomonosov Moscow State University

Faculty of Mechanics and Mathematics

Department of Mathematical Theory of Intelligent Systems (MaTIS)

2013

UDC: 004.432.2

*Keywords:* IPL, interpreted programming language, customizable syntax, 
interpreter, natural language, lexical analyzer, synonyms, reserved words.


## Abstract

A project for an interpreted programming language that makes a formal mathematical algorithm easier to understand 
and the development of a new algorithm more efficient, 
by simplifying the syntax and bringing the lexical forms of the programming language closer to those natural for the user. 
Relevance of the topic: the high complexity of software source code in practice.


## Introduction

The paper considers a prototype of a programming language that simplifies communication between a client and a programmer. 
Although the ways of such communication have long been established — there are flowcharts, UML diagrams, etc. — they are not ideal, and there is room for improvement. 
The goal of this work is to make complex program source code easier to read by bringing the programming language together with natural language. 
The idea of the work is to provide a human–computer interface without special characters like “}_$<<;”, 
i.e. to make the computer speak the human's language rather than the other way around. 
I believe we should strive for a world where anyone can solve an everyday programming task 
simply by giving commands in their native language, without needing any technical knowledge.

The idea implies a programming language whose code would seem clear and natural to the reader, 
requiring no additional documentation or comments 
(as it turned out, writing the code should still be done by a professional who understands how the syntax works). 
The language was named the *interpreted programming language*, or IPL.

The language pursues the following goals and objectives:

*	*The goal is the algorithm*: no need to spell out exhaustive details that obscure the algorithm. A high level of abstraction.
*	*Code is presented as formal mathematical text*: it gets that look from sequencing and summarizing words and from the ability to use nested numbered items and sub-items.
*	*Code that is clear at first glance*. The interpreter lets you change the reserved words and operations to suit the habits and preferences of the writer when writing and of the reader when reading.
*	*Code can be localized, and the syntax adapted to the localization*. The appearance of code can be changed, up to writing programs in your native language (obscure constructs may become clearer in context). The language encourages proper, descriptive names by supporting set phrases of natural language.
*	*Code is a kind of interface*. By analogy, the client could tweak the code themselves.
*	*Code does what it should and nothing it shouldn't*. The client can verify for themselves whether or not the program design meets their requirements.

Features of IPL:

*	a lexical analyzer that accounts for multi-word phrases in names; 
*	a changeable alphabet and set of reserved words; 
*	language syntax customizable to the user's preferences; 
*	simple and clear semantics; 
*	smart data storage types; 
*	built-in execution optimization.

IPL brings us closer to solving the following problems:

*	comfortable and fast study of the sources by a new programmer;
*	easier maintenance of software products;
*	user trust in the program;
*	better mutual understanding between the programmer and the client.

The paper consists of an introduction, which analyzes the main ideas and states the goal of the work; 
three parts, demonstrating the language's customizable syntax and the operation and implementation of the IPL interpreter; 
and a conclusion summing up the work on the project.

**Listing 1.1.**

![1](https://github.com/favorart/IPL/assets/9784285/09371315-ff99-499d-b85c-f48d39dc301b)

_____________________

## 1. Customizable syntax

The idea behind the interpreted programming language was to let users define the syntax 
based on their preferences and habits (Listing 1.1). 
Variable declaration blocks can appear anywhere in the program. Listing 1.2 shows syntax variants:

**Listing 1.2.**

![2](https://github.com/favorart/IPL/assets/9784285/805a65af-e821-4e13-b60d-33deb87c962a)

*Arithmetic expressions*. When code is written with a setting that has no explicit separators, 
expressions are logically separated according to intuitive understanding. 
An algebraic expression is considered complete when two consecutive tokens are not language operators: 

$$ a=1+2 \hspace{10pt} [;] \hspace{10pt} b=2+4 $$

`interpreter.Syntax` contains settings (Listing 1.3) that define variations in how language constructs are written. 

**Listing 1.3.**

![3](https://github.com/favorart/IPL/assets/9784285/70704cd9-32fc-41fc-bca1-c6f9d7ea21c9)


## 2. Operation

Interpretation consists of three phases:

*Lexical analysis* - extracting atoms from the text and building a list of atomic words, 
skipping unregistered characters and comments.

*Syntactic analysis* - extracting expressions from the list of atoms and 
converting arithmetic expressions to Polish notation, taking into account operator precedence, 
type compatibility and function availability.

*Execution* by recursive descent over the list; 
the return values of functions are used as parameters of functions higher up the recursion.

*Reading and writing pre-compiled bytecode*. 
When a script is launched, the interpreter checks the current folder for ready pre-compiled files. 
If they are found, the interpreter skips the lexical and syntactic analysis phases 
as well as syntax configuration and goes straight to execution. 
This is how performance is improved.


### 2.1. Pre-compilation to bytecode

The programmer writes an IPL script in a text file according to their interpreter configuration 
and gets an `.ipl` file (interpreted pre-compiled). 
When the file is executed, a pre-compiled version of the program's source code is created in the interpreter's memory, 
understandable only to the interpreter.
Pre-compilation creates three data files and a bytecode file:

		<script name>.ipc.constants.dat
		<script name>.ipc.variables.dat
		<script name>.<conf>.ipc.reg_words.dat
		<script name>.ipc

When the bytecode is created, all variable declaration blocks are dropped, 
and a separate hash table is created specifically to store the initial values of variables — 
it is written to `variables.dat`.

At the start of reading, the hashes `{1}` in the bytecode file and in the source of the program being executed are compared. 
The rest of the file consists of triples of four-byte numbers that define the code. 
The very first triple is the top-level list holding all expressions and code blocks. 
Then come its elements, and so on, with the program nested recursively (Table 2.1).

**Table 2.1.**

| file header [32 bytes]                        |
|:---------------------------------------------:|
| SHA-256 hash of the executable script file    |

| atom type                     | offset in the table | offset in the chain   |                   |
|:-----------------------------:|:-------------------:|:---------------------:|:------------------|
|which hash table to search in  |from the start of the hash table|at the hash table element|
| [ sizeof (int) ]              | [ sizeof (int) ]    | [ sizeof (int) ]      |
| PreComp                       | 0                   | number of elements    |language expression (list)
| Constant                      | 476                 | 0                     |constant value
| Variable                      | 165                 | 0                     |language variable
| RegWord                       | 634                 | 2                     |reserved word of the language
| ...                           | ...                 | ...                   |


### 2.2. Lexical analysis phase

As mentioned above, to make the algorithm clearer, IPL uses synonyms of reserved words and identifiers 
made up of several *word components* (that's what we'll call natural-language words, to avoid confusion), 
while unnatural prefixes and symbols are not allowed. As a result, the interpreter's lexical analysis mechanism 
was written with the need to guess from the word order in a language expression and from context. 
Text analysis happens in two stages: first, the bytes of the file on disk 
(`TODO: Unicode is not implemented yet; strings are handled as ASCII`) 
are grouped into simple word components, which are brought to a *normalized form*. 
Their list is passed to the stage above, where language *atoms* are constructed from them if there are enough of them; 
otherwise, the first-level analyzer is called again. 
The result of lexical analysis is a sequential list of atoms (Fig. 2.1):

**Fig. 2.1.** `ipl_list_pmv list_of_atoms`

![2 1](https://github.com/favorart/IPL/assets/9784285/5bf1d652-95df-426b-90d2-7b09e57d59d4)

The analyzer is configured through *configuration files*. 
All characters are defined in the alphabet settings file 
(`<conf>_charset.txt`, where `<conf>` is set by the user, e.g. `eng` or `rus`). 
In it, characters are divided into 5 disjoint classes: letters, signs, digits, the quote character and the decimal point character. 
The characters are defined by the user and can be arbitrary — the interpreter does not depend on specific letters and signs.

Another configuration file is the reserved words file (`<conf>.txt`). 
It looks like this: a unique identifier of the word's meaning (taken from `reg.word.id.txt`), 
followed by comma-separated synonyms denoting this reserved word, and finally an optional explanatory comment. 
Reserved words are known to the analyzer at run time.
 Synonyms are synchronized by the syntactic analyzer.


### 2.3. Syntactic analysis phase

The tasks of the syntactic analyzer are: 

1. correctly handling variations of the sources and reducing them to a single bytecode;
2. reordering instructions according to precedence.

This way, the executor only has to execute instructions sequentially. 

Task (1) is trivial: it consists of sequentially polling the lexical analyzer for the next batch of atoms, 
after which the meaning of the words is checked; if the next word is not allowed, the corresponding error is raised. 

Task (2) consists of extracting expressions from the list of atoms and converting arithmetic operations 
into *Polish (prefix) notation using a stack* `{3}`. 
Here the syntactic analyzer converts an expression from infix to prefix notation, i.e. $(1+2)$ into $(+,1,2)$.

In addition, if during its work the syntactic analyzer finds lines that are too long or nesting that is too deep, 
it issues warnings that the constructs written by the programmer may be too convoluted, 
and the user will have a hard time understanding this part of the algorithm. 
Figure 2.2 shows an example of a successfully completed syntactic analysis phase in the IPL interpreter for a branching operation.

**Fig. 2.2.** The branching operator in IPL.

![2 2](https://github.com/favorart/IPL/assets/9784285/430e7237-9c07-415f-a2d7-78b3b91fec57)

In sum, IPL *syntax* has the following features:

*	variables are declared in a separate block;
*	there are several alternative syntaxes for object methods and loops;
*	you can mark items in code blocks, which clarify the block's structure and guide the reader's eye more firmly;
*	the `resulted` directive, which lets any code block return a result.

IPL lacks the two kinds of *brackets* programmers are used to: *functional* and *structural*. 
This is done to implement the paradigm in which any code block can return a value, making it equivalent to an expression. 
A code block can even be used inside function parameters, as long as it returns a value and doesn't make the program harder to understand.


### 2.4. Execution phase

The interpreter executes the bytecode by *recursive descent* `{2}`; 
the bytecode, shown in Figure 2.2, consists of nested lists of atoms. 
As instructions are executed, the program *collapses*: 
the expression being processed is taken out of the list and its result is written in its place ($1+2 \to 3$). 
In the executor's structure, the extracted elements are not deleted 
but moved from the expression being executed to a preserving expression. 
Thus the pre-compiled bytecode, verified for correctness by execution, 
remains available for writing to a file or for use in loops and functions. 
The program terminates when no elements are left in the list of instructions to execute [1].


## 3. Implementation

The building blocks of the interpreter are `myvar` structures (Listing 3.1); depending on their values, 
an atomic element of the language can be a sign, a reserved word, a constant, a variable or even a whole expression. 
Enumerator fields indicate what the atom is.

**Listing 3.1.**

![3 1](https://github.com/favorart/IPL/assets/9784285/46fa5a6f-91e1-4ca1-b326-d95c5cc8e87b)

The interpreter's data is stored in a structure called the *name table* (`names_table`). 
The interpreter starts by initializing it and ends by clearing it. 
The table stores the data needed at various stages of script execution: 
for example, at the tokenization and syntax stages, as well as important data 
that is always needed — the dictionaries of variables, constants, reserved words and expressions.

Thus all dynamic memory is recorded in this registry one way or another, 
which guarantees that all allocated memory will be freed completely and on time. 
That is how the garbage collection problem is solved.


## 4. Typing

IPL deliberately does not use *implicit typing*, 
since it is hard to distinguish an implicit variable declaration from a reference to it, and hard to trace a variable's scope in the program text. 
At the same time, it does not give up *dynamic typing* [5], so as not to constrain the programmer with rigid static typing, 
offering the conveniences of an interpreted language while still being able to catch data type errors. 
*Mixed typing* was chosen: when creating a variable you must specify its type explicitly, but you can change that type when needed.

The language's built-in types are shown in Table 3.1.

**Table 3.1.**

| data type                | value range
|:-------------------------|:-----------------------------------:|
| integer                  | from -2,147,483,647 to 2,147,483,647
| floating-point number    | 1E-37 to 1E+37
| string                   | a sequence of ASCII characters
| function                 |
| container                | list or array
| dictionary               | a dynamic analogue of a struct

IPL supports modular programming using functions in separate files. 
All functions are global, all variables are local. 
Variables are passed to a function by value. 
The implementation of a function inside the `myvar` structure is a whole small interpreter: 
it has its own script file, its own lexical analyzer and its own pre-compiled code. 
A function declaration is required if its definition is in another file. 
If the file name is not specified in the declaration, the file will be looked up 
by a name identical to the function name + the `.ipl` file extension in the default folder. 

It is impossible to imagine a modern programming language without *enumerable data types*: 
dictionaries and containers. 
These types are built into the core and have familiar methods. 
A special feature of the IPL container, which can store elements of any type one after another, 
is that, depending on how often the user performs certain operations, 
the container itself decides how to store its elements 
(the storage type for a container can be specified up front) — it can be a doubly linked list or a contiguous array.

As is well known, an array is efficient for random-access reads but inefficient for random writes. 
It's the opposite for a list: insertion is a cheap operation, but indexing into the middle requires going through half the elements. 
If operations that are inconvenient for a particular storage method are performed systematically, 
it makes sense to switch to another storage method despite the cost of restructuring. 
The container keeps track of the total number, as well as the length of runs of consecutive insertions and accesses by address. 
With each action, counters inside the specific container instance are incremented or decremented. 
The threshold values were chosen experimentally.

The dictionary data type (`joint`) is a set of `key:value` pairs, 
where `key` and `value` are some data types. 
The `value` can be retrieved from the dictionary in constant time by `key`, if it is there. 
Otherwise a ‘failure’ is returned. 
Hash-table-based dictionaries {4} are used as an analogue of user-defined types (`struct` in C). 
This approach is common among interpreted languages, 
since it allows the structure of the aggregate to be defined dynamically while the program runs. 


## Conclusion

This paper presents the results of research work on creating an interpreter for the IPL language. 
The text in Listing 4.1 demonstrates the readability of the code and many of the language's capabilities. 
As you could see from the IPL sources presented, 
it brings us one step closer to using natural language in programming.

**Listing 4.1.** The knapsack problem

![4 1](https://github.com/favorart/IPL/assets/9784285/ee554a40-3c85-4684-b2ec-129a0da78021)

_____________________

**Listing 4.2.** A program with $O(n^2)$ complexity

![4 2](https://github.com/favorart/IPL/assets/9784285/80204cf2-5f07-492f-9add-cc38e3709e2b)

_____________________

**Listing 4.3.** A program in Uzbek

![4 3](https://github.com/favorart/IPL/assets/9784285/8e0f53e5-8e0a-47e4-9c01-8c3bd6e48849)

_____________________

## References

* [1]	Schildt H. Born to Code in C. – Osborne, 1989
* [2]	Kernighan B., Ritchie D. The C Programming Language. – Prentice Hall, 1988
* [3]	[An example of writing a simple interpreter](https://rsdn.org/forum/alg/5018812){: hreflang=ru }
* [4]	[Your own interpreter](https://web.archive.org/web/20090820050231/http://coderszone.info/339-sam-sebe-interpretator.html){: hreflang=ru }
* [5]	[Dynamic typing](http://ru.wikipedia.org/wiki/Динамическая_типизация){: hreflang=ru }


### Algorithms used

*	{1}	[SHA256 file hash computation (Ch. Devine, 2003)](https://web.archive.org/web/20120615070343/http://patux.net/crypto_programs/hash/sha-2/sha256.c.html)
*	{2}	[Recursive descent](http://en.wikipedia.org/wiki/Recursive_descent_parser)
*	{3}	[Building Polish (prefix) notation with a stack](https://web.archive.org/web/20240705142522/https://algolist.manual.ru/maths/misc/revpn.php){: hreflang=ru }
*	{4}	Building hash tables
*	Hash address equal to the remainder of division by a prime (A. Dumey, 1956)
*	Separate chaining (H. P. Luhn, 1953)
*	Open addressing (probing) (A. P. Ershov, 1953), (in Western literature — G. Amdahl, 1957)
*	{5}	Sorting
*	Quicksort (C. A. R. Hoare, 1960), implementation from <stdlib.h>
*	Merge sort for lists (J. von Neumann, 1945)
