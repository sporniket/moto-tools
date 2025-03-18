# The command line interface of moto_fdar

> **NOTICE : moto_fdar only supports disk image archives with 4 sides, and 80 tracks per side.**

_moto_fdar_ (FDAR : **F**loppy **D**isk **AR**chive) works on disk image archives suitable for emulators of the Thomson MO/TO line of computers, like : 
* [the DCMOTO by Daniel COULOM](http://dcmoto.free.fr/emulateur/index.html), 
* the [Libretro core 'Theodore' by Thomas Lorblanchès based on Daniel Coulom's DCTO8D/DCTO9P/DCMO5 emulators](https://docs.libretro.com/library/theodore/) 
* [Teo-ng by sam-itt](https://github.com/sam-itt/teo-ng).
* [Teo by Gilles Fétis, Éric Botcazou, Alexandre Pukall, Jérémie Guillaume, François Mouret, Samuel Devulder](https://sourceforge.net/projects/teoemulator/)

## Synopsis

```
python3 -m moto_fdar --add [--verbose] [--into <path>] <archive.sd> [<source-files>...]
```

Add the designated files **into an already existing** disk image archives.

```
python3 -m moto_fdar --create [--verbose] [--into <path>] <archive.sd> [<source-files>...]
```

Assemble the designated files **into a NEW disk image archives**. **If the archive file already exists, it is overwritten.**

```
python3 -m moto_fdar --list [--verbose] <archive.sd>
```

List all the files contained inside a disk image archives.

```
python3 -m moto_fdar --extract [--verbose] [--into <path>] <archive.sd>
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

### Emulator disk image archives

> Source : [this post by Daniel Coulom on 'forum.system-cfg.com, Forum des collectionneurs et utilisateurs d'ordinateurs anciens'](https://forum.system-cfg.com/viewtopic.php?p=121069#p121069)

> En fait je n'ai rien inventé : le format .fd est le format "raw". Je l'ai simplement baptisé .fd pour ne pas confondre les images de disquettes Thomson avec les images .raw de disquettes MS-DOS. Notez que le format .fd est plus général que .sap, puisqu'il permet de faire des images de disquettes simple face, double face ou quadruple face (2 disquettes double face), et ceci aussi bien en simple densité qu'en double densité, et en 40 pistes comme en 80 pistes.
>
> Le seul avantage du format SAP est de prévoir des informations supplémentaires pour contourner certains types de protections (mais pas toutes). Dans la pratique je n'ai jamais vu de fichier .sap contenant de telles informations.
>
> L'avantage décisif du fichier .fd est de ne pas être crypté. Il permet aussi d'avoir un seul fichier pour une disquette double face, alors qu'une image .sap nécessite deux fichiers. Le format .fd est le seul reconnu par le driver Omniflop, pour les transferts de disquettes Thomson avec un PC Windows 32 bits ou 64 bits. Les autres utilitaires de transfert de disquettes Thomson, dctransferts et sdtransfert utilisent exclusivement le format .fd. L'utilitaire FD2SD de création de fichiers .sd (pour simulation de disquettes Thomson avec une carte SD) nécessite aussi le format .fd.
>
> Le format .fd étant un format "raw", il n'est pas limité aux disquettes Thomson. On peut l'utiliser pour tous types de disquettes : par exemple l'émulateur dcalice utilise les fichiers .fd pour des images de disquettes au format Alice (MS-DOS 1,44Mo). L'émulateur dcsquale (non diffusé) utilise le format .fd pour les disquettes au format Squale. L'émulateur dcexel utilise le format .fd pour des disquettes au format Exeldisk.
> http://alice32.free.fr/index.html
> http://dcsquale.free.fr/
> http://dcexel.free.fr/index.html
