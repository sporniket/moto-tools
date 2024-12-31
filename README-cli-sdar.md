# The command line interface of moto_sdar

## Synopsis

```
python3 -m moto_sdar --create [--verbose] [--into <path>] [--reference <ref_archive.sd>] <archive.sd> [<source-files>...]
```

Assemble the designated files into a floppy disk archive suitable for the SDDrive. The disk archive MAY be created by starting from a reference disk archive, e.g. [an image with the DOS Basic](http://dcmoto.free.fr/programmes/dos-3.5/index.html) that would make the resulting image into a bootable disk.

```
python3 -m moto_sdar --list [--verbose] <archive.sd>
```

List all the files contained inside a floppy disk archive readable by MO5 emulators.

```
python3 -m moto_sdar --extract [--verbose] [--into <path>] <archive.sd>
```

Extract all the files contained inside a floppy disk archive readable by MO5 emulators.

## Mandatory arguments

* `--create <archive.sd>` or `--list <archive.sd>` or `--extract <archive.sd>` : the operation to perform.

* `<archive.sd>` : the specified floppy disk archive, with the `fd` extension.

## Optional arguments

* `source files` : one or more files of any type.

* `--verbose` : each processed files is displayed in a tabulated format, showing

> TODO update actual format

  * the type of file (tokenized **B**asic, Ascii **L**isting, **D**ata) ; binary files have no type indication
  * the name and extension
  * the size in bytes, and the number of data blocks it takes

  Without `--verbose`, the `--list` command will only list the file names.

* `--into [path]` : directory where the created floppy disk archive or the extracted files will be stored ; when not specified, they are stored in the current directory.

* `--reference <ref_archive.sd>` : references an archive that will serve as a basis for the created archive (the reference archive is left untouched). This allow the creation of _bootable_ disk images : by default `moto_sdar` will create an archive looking like a blank formatted floppy disk into which all the source files have been written, thus a _non bootable_ disk. To create a _bootable_ disk image, one must have e.g. [an image with the DOS Basic](http://dcmoto.free.fr/programmes/dos-3.5/index.html), and use it as reference.

## File handling

### Archive creation

> draft ; to update with actual behavior

* Files with the extension `bas` will be added as BASIC, tokenized files, unless they are suffixed with `,a` to be added as BASIC, ascii listing files.
* Files with the extension `lst` will be added with the `bas` extension instead, as BASIC, ascii listing files.
* Files with the extension `csv` will be added as DATA files
* Other files will be added as BINARY files.

### Archive extraction

* ASCII listing with the extension `bas` will be extracted with the `lst` extension.
* Other files will be extracted as expected. If a file already exist, it is overwritten.

### Archive listing

* The type of files is inferred from the content of the leader block.

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