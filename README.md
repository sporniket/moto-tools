# Sporniket's MO/TO tools

[![Latest version](https://img.shields.io/pypi/v/moto-tools-by-sporniket)](https://pypi.org/project/moto-tools-by-sporniket/releases)
[![Workflow status](https://img.shields.io/github/actions/workflow/status/sporniket/moto-tools/python-app.yml)](https://github.com/sporniket/moto-tools/actions/workflows/python-app.yml)
[![Download status](https://img.shields.io/pypi/dm/moto-tools-by-sporniket)](https://pypi.org/project/moto-tools-by-sporniket/)

> [WARNING] Please read carefully this note before using this project. It contains important facts.

Content

1. What is **Sporniket's MO/TO tools**, and when to use it ?
2. What should you know before using **Sporniket's MO/TO tools** ?
3. How to use **Sporniket's MO/TO tools** ?
4. Known issues
5. Miscellanous

## 1. What is **Sporniket's MO/TO tools**, and when to use it ?

**Sporniket's MO/TO tools** is a python library with a set of command line interfaces that will assist a developper of software running on emulators of the family of computers made by Thomson during the 1980s, models "MO" and models "TO".

The current list of tools : 

* Tools for basic language
  * `moto_nl` : number the lines of a basic source that have line unnumbered ; the command line interface is designed after the command `nl`.
  * `moto_prettier` : consistently format the provided utf-8 encoded basic source file
  * `moto_bas2lst` : convert tokenized or ASCII basic program into an utf-8 encoded basic source file
  * `moto_lst2bas` : convert an utf-8 encoded source file into tokenized or ASCII basic program
* Tools for manipulating media images (tape, floppy disks) for emulation and exchange
  * `moto_tar` : list, create or extract `*.k7` tape images ; the command line interface is designed after the command `tar` (_Tape ARchives_)
  * `moto_sdar` : list, create or extract `*.sd` SDDrive disk images (a.k.a. _SD ARchives_) ; the command line interface is also designed after the command `tar`

### Licence

**Sporniket's MO/TO tools** is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

**Sporniket's MO/TO tools** is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

### Release notes

#### V0.0.5

Interim version, `moto_sdar` is now usable, but archives created with it need to be tested on emulators and real hardware.

* Fixes #35 : [bug][moto_bas2lst] It should not emit empty lines
* Resolves #30 : [moto_sdar][moto_fdar] put content as a new catalog entry
* Resolves #38 : [moto_lib] DiskSector allows to change the data
* Resolves #41 : [moto_sdar][moto_fdar] Create a disk image
* Resolves #42 : [moto_sdar][moto_fdar] display pre- or post- processing of a file 
* Resolves #46 : [moto_sdar][moto_fdar] Update a disk image

#### v0.0.4

Interim version, work has progressed tremendously after a year of hiatus. Tools have limited implementation but are not complete.

**Support for python 3.8 and 3.9 is removed ; support for python 3.11, 3.12, and 3.13 is added**

* Resolves #12 : [moto_lst2bas][mo5] Convert to tokenized format
* Resolves #14 : [moto_sdar] list the content of a disk archive
* Resolves #15 : [moto_sdar][moto_fdar] A library to handle the data layout of a disk image
* Resolves #17 : [moto_sdar][moto_fdar] A library to handle the file system of the drive operating system
* Resolves #20 : [moto_sdar][moto_fdar] A library to display the content being processed
* Resolves #28 : [moto_sdar][moto_fdar] extract the content of a catalog entry
* Fixes #31 : [bug] block allocation numbering and reserved track
* Resolves #33 : [moto_sdar] extract the content of a disk archive

#### v0.0.3

* Resolves #6 [moto_prettier] force upper case outside litteral string

#### v0.0.2

* Resolves #4 : [moto_tar][mo5] adjust the minimal sequence to spot the start of a bloc
* Resolves #5 : [moto_bas2lst] Convert basic ascii file to plain text utf-8 file (#9)
* Resolves #7 : [moto_lst2bas] Convert plain text files into ASCII basic

#### v0.0.1

The target platform is Thomson MO5. 

Provides the following tools :

* `moto_tar` : create, list or extract files to or from a tape archive format ; the command line interface is designed after the command `tar`.
* `moto_nl` : number the lines of a basic source that have line numbers ; the command line interface is designed after the command `nl`.

## 2. What should you know before using **Sporniket's MO/TO tools** ?

**Sporniket's MO/TO tools** is written in python and supports python 3.10 up to 3.13

It uses the `pdm` utility to manage its dependencies and management tasks

see [README packaging](https://github.com/sporniket/moto-tools/blob/main/README-packaging.md) for further details.

> Do not use **Sporniket's MO/TO tools** if this project is not suitable for your project.

## 3. How to use **Sporniket's MO/TO tools** ?

### From sources

To get the latest available models, one must clone the git repository, build and install the package.

	git clone https://github.com/sporniket/moto-tools.git
	cd moto-tools
	pdm run test
	pdm build
	pipx install $(ls ./dist/*.whl)

Then, invoke one of the command line interfaces :

```
python3 -m moto_tools_tar [option] input_file
```

### Using pip

```
pipx install moto-tools-by-sporniket
```

Then, invoke the command line interface :

```
python3 -m moto_tools_tar [option] input_file
```

## 4. Known issues
See the [project issues](https://github.com/sporniket/moto-tools/issues) page.

## 5. Miscellanous

Supplemental documentation :

* [README packaging](https://github.com/sporniket/moto-tools/blob/main/README-packaging.md) : some technical details about packaging this project.
* [README cli tar](https://github.com/sporniket/moto-tools/blob/main/README-cli-tar.md) : the manual of the command line interface `moto_tar`.
* [README cli nl](https://github.com/sporniket/moto-tools/blob/main/README-cli-nl.md) : the manual of the command line interface `moto_nl`.
* [README cli bas2lst](https://github.com/sporniket/moto-tools/blob/main/README-cli-bas2lst.md) : the manual of the command line interface `moto_bas2lst`.
* [README cli lst2bas](https://github.com/sporniket/moto-tools/blob/main/README-cli-lst2bas.md) : the manual of the command line interface `moto_lst2bas`.
* [README cli prettier](https://github.com/sporniket/moto-tools/blob/main/README-cli-prettier.md) : the manual of the command line interface `moto_prettier`.
* [Tape archive format](http://pulkomandy.tk/wiki/doku.php?id=documentations:monitor:tape.format) : the description of the format.

### Report issues
Use the [project issues](https://github.com/sporniket/moto-tools/issues) page.
