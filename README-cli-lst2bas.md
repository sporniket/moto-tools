# The command line interface of moto_lst2bas

## Synopsis

```
python3 -m moto_lst2bas <source-files>...
```

Convert any plain text file into a BASIC file loadable by MO/TO BASIC. The converted files have the extension `bas`.

## Mandatory arguments

* `source files` : one or more files to process. Each file MUST have a "lst" extension, case insensitive, e.g. `myprog.lst`. A file to convert into basic ASCII format MUST be marked with `,a` after the file extension, e.g. `myprog.lst,a`.

## Optional arguments

_None_