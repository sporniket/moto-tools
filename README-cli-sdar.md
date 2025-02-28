# The command line interface of moto_sdar

## Synopsis

```
python3 -m moto_sdar --add [--verbose] [--into <path>] <archive.sd> [<source-files>...]
```

Add the designated files into an **already existing** floppy disk archive suitable for the SDDrive.

```
python3 -m moto_sdar --create [--verbose] [--into <path>] <archive.sd> [<source-files>...]
```

Assemble the designated files into a floppy disk archive suitable for the SDDrive. **If the archive file already exists, it is overwritten.**

```
python3 -m moto_sdar --list [--verbose] <archive.sd>
```

List all the files contained inside a floppy disk archive readable by MO5 emulators.

```
python3 -m moto_sdar --extract [--verbose] [--into <path>] <archive.sd>
```

Extract all the files contained inside a floppy disk archive readable by MO5 emulators.

## Mandatory arguments

* `--add <archive.sd>` or`--create <archive.sd>` or `--list <archive.sd>` or `--extract <archive.sd>` : the operation to perform.

* `<archive.sd>` : the specified floppy disk archive, with the `fd` extension.

## Optional arguments

* `source files` : one or more files of any type.

* `--verbose` : each processed files is displayed in a tabulated format, showing

  * the name and extension of the file
  * the type of file (BASIC program, data, binary module or text) and data (binary or ascii)
  * the size in bytes and blocks

  Without `--verbose`, the command will only list the file names.

* `--into [path]` : directory where the created floppy disk archive OR the extracted files will be stored ; when not specified, they are stored in the current directory.

## File handling

### Archive creation

* Files with the extension `bas` will be added as BASIC, tokenized files, unless they are suffixed with `,a` to be added as BASIC, ascii listing files.
* Files with the extension `bin` will be added as binany module files.
* Files with the extension `txt` will be added as ascii text files.
* Other files will be added as BINARY data files.

### Archive extraction

* Each side is extracted in a separated folder `sideX` where `X` is the index of the side starting with zero.
* Files will be extracted as expected. **If a file already exist, it is overwritten without warning.**

### Archive listing

* In verbose mode, the type of each files are listed, along its size in bytes and the number of blocks it occupies.

## File format of a disk archive

### Remainder : physical layout of a floppy disk

Source : [_Le basic DOS du TO7, TO7-70 et du MO5_, by Christine Blondel and François-Marie Blondel](http://dcmoto.free.fr/documentation/basicdos/index.html) ; [Floppy disk at Wikipedia](https://en.wikipedia.org/wiki/Floppy_disk).

* A floppy disk has either one or two _sides_, starting from _side #0_. Each side is seen as a separate _unit_.
* A side contains 40 _tracks_ (5¼-inch double density floppy disks) or 80 _tracks_ (5¼-inch high density disks and 3½-inch double density disks), starting from _track #0_.
* A track contains 16 _logical sectors_, starting from _sector #1_. (On the )

> On a physical disk, sectors are usually not stored in order, but are intertwined, to create a delay before the start of the next sector read/write. The computer's floppy disk routines leverage this delay to perform some data book-keeping.

### SDDrive disk archive

> Source : [SDDRIVE homepage](http://dcmoto.free.fr/bricolage/sddrive/index.html)

_SDDrive assume 80 tracks per sides_

Essentially, the SDDrive disk archive is structured like an emulator disk archive, with the following differences :

* `*.sd` files are made of blocks of **512** bytes.
* The first 256 bytes of each block contains the data of a floppy disk sector.
* The last 256 bytes of each block are filled with `$FF`.
* Sectors are laid out in logical order, from sector #1 to sector #16, starting with track #0 of side #0. 
* All the tracks of the same side are laid out in order, from track #0 to track #79. 
* An image WILL ALWAYS contains 4 disks sides, with a total size of 2621440 bytes.