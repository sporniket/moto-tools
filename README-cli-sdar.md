# The command line interface of moto_sdar

_moto_sdar (SDAR : **SD**drive **AR**chive) works on disk image archives suitable for [the SDDrive by Daniel Coulom](http://dcmoto.free.fr/bricolage/sddrive/index.html)_

## Synopsis

```
python3 -m moto_sdar --add [--verbose] [--into <path>] <archive.sd> [<source-files>...]
```

Add the designated files **into an already existing** disk image archives.

```
python3 -m moto_sdar --create [--verbose] [--into <path>] <archive.sd> [<source-files>...]
```

Assemble the designated files **into a NEW disk image archives**. **If the archive file already exists, it is overwritten.**

```
python3 -m moto_sdar --list [--verbose] <archive.sd>
```

List all the files contained inside a disk image archives.

```
python3 -m moto_sdar --extract [--verbose] [--into <path>] <archive.sd>
```

Extract all the files contained inside a disk image archives.

## Mandatory arguments

* `--add <archive.sd>` or`--create <archive.sd>` or `--list <archive.sd>` or `--extract <archive.sd>` : the operation to perform.

* `<archive.sd>` : the specified disk image archives, with the `fd` extension.

## Optional arguments

* `source files` : one or more files of any type. Only used with `--add` and `--create`. Between source files, an `--eos` (_End Of Side_) will instruct the tool to save the next files into the next disk side of the archive.

* `--verbose` : each processed files is displayed in a tabulated format, showing

  * the name and extension of the file
  * the type of file (BASIC program, data, binary module or text) and data (binary or ascii)
  * the size in bytes and blocks

  Without `--verbose`, the command will only list the file names.

* `--into [path]` : directory where the created disk image archives OR the extracted files will be stored ; when not specified, they are stored in the current directory.

## File handling

### Archive creation

* A file with the name `auto.bat` will be added as BASIC, tokenized files.
* Files with the extension `bas` will be added as BASIC, tokenized files, unless they are suffixed with `,a` to be added as BASIC, ascii listing files.
* Files with the extension `bin` will be added as binany module files.
* Files with the extension `txt` will be added as ascii text files.
* Other files will be added as BINARY data files.

### Archive extraction

* Each side is extracted in a separated folder `sideX` where `X` is the index of the side starting with zero.
* **If a file already exist, it is overwritten without warning.**

### Archive listing

* In verbose mode, the type of each files are listed, along its size in bytes and the number of blocks it occupies.

## File format of a disk image archives

### Remainder : physical layout of a disk

Source : [_Le basic DOS du TO7, TO7-70 et du MO5_, by Christine Blondel and François-Marie Blondel](http://dcmoto.free.fr/documentation/basicdos/index.html) ; [Floppy disk at Wikipedia](https://en.wikipedia.org/wiki/Floppy_disk).

* A disk has either one or two _sides_, starting from _side #0_. Each side is seen as a separate _unit_.
* A side contains 40 _tracks_ (5¼-inch double density disks) or 80 _tracks_ (5¼-inch high density disks and 3½-inch double density disks), starting from _track #0_.
* A track contains 16 _logical sectors_, starting from _sector #1_. (On the )

> On a physical disk, sectors are usually not stored in order, but are intertwined, to create a delay before the start of the next sector read/write. The computer's disk routines leverage this delay to perform some data book-keeping.

### SDDrive disk image archives

> Source : [SDDRIVE homepage](http://dcmoto.free.fr/bricolage/sddrive/index.html)

_SDDrive assume 80 tracks per sides_

Essentially, the SDDrive disk image archives is structured like an emulator disk image archives, with the following differences :

* `*.sd` files are made of blocks of **512** bytes.
* The first 256 bytes of each block contains the data of a disk sector.
* The last 256 bytes of each block are filled with `$FF`.
* Sectors are laid out in logical order, from sector #1 to sector #16, starting with track #0 of side #0. 
* All the tracks of the same side are laid out in order, from track #0 to track #79. 
* An image WILL ALWAYS contains 4 disks sides, with a total size of 2621440 bytes.