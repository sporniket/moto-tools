# The command line interface of moto_bas2lst

## Synopsis

```
python3 -m moto_bas2lst [--dos] <source-files>...
```

Convert any BASIC file saved by MO/TO BASIC into plain text. The converted files have the extension `lst`.

## Mandatory arguments

* `source files` : one or more files to process. Each file MUST have a "BAS" extension, case insensitive, e.g. `myprog.bas`. A basic file in ASCII format MUST be marked with `,a` after the file extension, e.g. `myprog.bas,a`.

## Optional arguments

* `--dos` : Use the MS-DOS sequence of characters `CR` `LF` (`0x0d0a`) to end a line, instead of the Linux sequence `LF` (`0x0a`)
