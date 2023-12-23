# The command line interface of moto_fdar

## Synopsis

```
python3 -m moto_fdar --create [--verbose] [--into <path>] [--reference <ref_archive.xx>] <archive.xx> [<source-files>...]
```

Assemble the designated files into a floppy disk archive suitable for MO5 emulators or the SDDrive, depending on the archive extension. The disk archive MAY be created by starting from a reference disk archive, e.g. [an image with the DOS Basic](http://dcmoto.free.fr/programmes/dos-3.5/index.html) that would make the resulting image into a bootable disk.

```
python3 -m moto_fdar --list [--verbose] <archive.xx>
```

List all the files contained inside a floppy disk archive readable by MO5 emulators.

```
python3 -m moto_fdar --extract [--verbose] [--into <path>] <archive.xx>
```

Extract all the files contained inside a floppy disk archive readable by MO5 emulators.

## Mandatory arguments

* `--create <archive.xx>` or `--list <archive.xx>` or `--extract <archive.xx>` : the operation to perform.

* `<archive.xx>` : the specified floppy disk archive, with either the `fd` or `sd` extension ; the extension will specify the expected format of the floppy archive.
  * `fd` : disk archive for an emulator.
  * `sd` : disk archive for the SDDrive.

## Optional arguments

* `source files` : one or more files of any type.

* `--verbose` : each processed files is displayed in a tabulated format, showing

  * the type of file (tokenized **B**asic, Ascii **L**isting, **D**ata) ; binary files have no type indication
  * the name and extension
  * the size in bytes, and the number of data blocks it takes

  Without `--verbose`, the `--list` command will only list the file names.

* `--into [path]` : directory where the created floppy disk archive or the extracted files will be stored ; when not specified, they are stored in the current directory.

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

### Emulator disk archive

> Source : [Transferts Thomson <-> PC](http://dcmoto.free.fr/forum/messages/644139_0.html)

_Emulators assume 3½-inch double density disks with 80 tracks per sides_

* `*.fd` files are made of blocks of 256 bytes. 
* Each block contains the data of a floppy disk sector.
* Sectors are laid out in logical order, from sector #1 to sector #16, starting with track #0 of side #0. 
* All the tracks of the same side are laid out in order, from track #0 to track #79. 
* All the sides of a disk are stored in order, from side #0 to side #1
* An image MAY concatenate 2 disks to simulate unit #0 to #3.
* The size of an image of a single-sided disk is 327680 bytes.
* The size of an image of a double-sided disk is 655360 bytes.

> `moto_fdar` will only create a single disk archive, with either one or two sides. 


### SDDrive disk archive

> Source : [SDDRIVE homepage](http://dcmoto.free.fr/bricolage/sddrive/index.html)

_SDDrive assume 80 tracks per sides_

Essentially, the SDDrive disk archive is structured like an emulator disk archive, with the following differences :

* `*.sd` files are made of blocks of **512** bytes.
* The first 256 bytes of each block contains the data of a floppy disk _sector_.
* The last 256 bytes of each block are filled with `$FF`.
* An image WILL ALWAYS contains 4 disks sides, with a total size of 2621440 bytes.