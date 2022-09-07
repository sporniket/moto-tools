# The command line interface of moto_tools_tar

## Synopsis

```
python3 -m moto_tools_tar --create --file <archive.k7> [--verbose] [--into <path>] <source-files>...
```

Assemble the designated files into a tape archive readable by MO5 emulators. The resulting file is padded to reach 21 kiB.

```
python3 -m moto_tools_tar --list --file <archive.k7> [--verbose]
```

List all the files contained inside a tape archive readable by MO5 emulators.

```
python3 -m moto_tools_tar --extract --file <archive.k7> [--verbose] [--into <path>]
```

Extract all the files contained inside a tape archive readable by MO5 emulators.

## Mandatory arguments

* `--create` or `--list` or `--extract` : the operation to perform.

* `source files` : one or more files of any type.

## Optional arguments

* `--verbose` : each processed files is displayed in a tabulated format, showing

  * the type of file (tokenized **B**asic, Ascii **L**isting, **D**ata) ; binary files have no type indication
  * the name and extension
  * the size in bytes, and the number of data blocks it takes

  Without `--verbose`, the `--list` command will only list the file names.

* `--into [path]` : directory where the created tape archive or the extracted files will be stored ; when not specified, they are stored in the current directory.

## File handling

### Archive creation

* Files with the extension `bas` will be added as BASIC, tokenized files, unless they are suffixed with `,a` to be added as BASIC, ascii listing files.
* Files with the extension `lst` will be added with the `bas` extension instead, as BASIC, ascii listing files.
* Files with the extension `csv` will be added as DATA files
* Other files will be added as BINARY files.

### Archive extraction

* ASCII listing with the extension `bas` will be extracted with the `lst` extension.
* Other files will be extracted as expected. If a file already exist, it is overwritten.

### Archive listing

* The type of files is inferred from the content of the leader block.
