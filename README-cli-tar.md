# The command line interface of moto_tar

## Synopsis

```
python3 -m moto_tar --create [--verbose] [--into <path>] <archive.k7> [<source-files>...]
```

Assemble the designated files into a tape archive readable by MO5 emulators. The resulting file is padded to reach 21 kiB. When there is no source files, a blank tape archive is created.

```
python3 -m moto_tar --list [--verbose] <archive.k7>
```

List all the files contained inside a tape archive readable by MO5 emulators.

```
python3 -m moto_tar --extract [--verbose] [--into <path>] <archive.k7>
```

Extract all the files contained inside a tape archive readable by MO5 emulators.

## Mandatory arguments

* `--create <archive.k7>` or `--list <archive.k7>` or `--extract <archive.k7>` : the operation to perform.

* `<archive.k7>` : the specified tape archive, usually a file with the `k7` extension.

## Optional arguments

* `source files` : one or more files of any type.

* `--verbose` : each processed files is displayed in a tabulated format, showing

  * the type of file (tokenized **B**asic, Ascii **L**isting, **D**ata) ; binary files have no type indication
  * the name and extension
  * the size in bytes, and the number of data blocks it takes

  Without `--verbose`, the `--list` command will only list the file names.

* `--into [path]` : directory where the created tape archive or the extracted files will be stored ; when not specified, they are stored in the current directory.

## File handling

### Archive creation

* Files with the extension `bas` will be added as BASIC, tokenized files, unless they are suffixed with `,a` to be added as BASIC, ascii listing files.
* Files with the extension `csv` will be added as DATA files
* Other files will be added as BINARY files.

### Archive extraction

* Files will be extracted as they are. **If a file already exist, it is overwritten.**

### Archive listing

* The type of files is inferred from the content of the leader block.
