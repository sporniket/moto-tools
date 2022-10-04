# The command line interface of moto_nl

## Synopsis

```
python3 -m moto_nl [--line-increment <increment>] [--starting-line-number <start>] [--number-width <width>] [<source-files>...]
```

Add a line number to any unumbered line of a text file that should be a BASIC listing. When a line is numbered, the number serves as a starting point to number the following lines. A minimum of one space will be inserted after the number.

## Mandatory arguments

_None_

## Optional arguments

* `source files` : one or more files to process. Without any file or with `-`, it will use the standard input as source. When there are more than one source file, the numbering is done as if the input was a single file being the concatenation of all those file.

* `--line-increment <increment>` : the specified line increment will be added to the current line number in order to number the next line. _Default increment is 10._

* `--starting-line-number <start>` : The very first line of the first input will use this number if not already numbered. _Default starting line number is 10_

* `--number-width <width>` : The line number will be padded with enough space to have at least the specified width in characers, before writing the actual line. _Default line number minimal width is 1_

## Exemples

### Typical use

**When** the source file `in.bas` is :

```basic
cls
print "hello"
```

**Then** `python3 -m moto_nl in.bas` will output :

```basic
10 cls
20 print "hello"
```

**When** the source file `in.bas` is :

```basic
'a test program
5 cls
print "hello"
```

**Then** `python3 -m moto_nl in.bas` will output :

```basic
10 'a test program
5 cls
15 print "hello"
```

### Numbering several programs


**When** the source file `in1.bas` is :

```basic
screen 2,4
print "before hello"
```

**When** the source file `in2.bas` is :

```basic
cls
print "hello"
```

**Then** `python3 -m moto_nl in1.bas in2.bas` will output :

```basic
10 screen 2,4
20 print "before hello"
30 cls
40 print "hello"
```
