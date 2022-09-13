# Sporniket's MO/TO tools

[![Latest version](https://img.shields.io/pypi/v/moto-tools-by-sporniket)](https://pypi.org/project/moto-tools-by-sporniket/releases)
[![Workflow status](https://img.shields.io/github/workflow/status/sporniket/moto-tools/Python%20package)](https://github.com/sporniket/moto-tools/actions/workflows/python-package.yml)
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


### Licence

**Sporniket's MO/TO tools** is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

**Sporniket's MO/TO tools** is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

### Release notes

> No release yet.

## 2. What should you know before using **Sporniket's MO/TO tools** ?

**Sporniket's MO/TO tools** is written using python version 3.8, and should work with python version to 3.10.

It relies on the following packages to build and test :

* build
* pytest
* coverage

It also relies on the following package to enforce source formatting :

* black

see [README packaging](https://github.com/sporniket/moto-tools/blob/main/README-packaging.md) for further details.

> Do not use **Sporniket's MO/TO tools** if this project is not suitable for your project.

## 3. How to use **Sporniket's MO/TO tools** ?

### From sources

To get the latest available models, one must clone the git repository, build and install the package.

	git clone https://github.com/sporniket/moto-tools.git
	cd moto-tools
	./retest

Then, invoke one of the command line interfaces :

```
python3 -m moto_tools_tar [option] input_file
```

### Using pip

> Not available yet

```
pip install moto-tools-by-sporniket
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
* [README cli tar](https://github.com/sporniket/moto-tools/blob/main/README-cli-tar.md) : the manual of the command line interface `moto_tools_tar`.
* [Tape archive format](http://pulkomandy.tk/wiki/doku.php?id=documentations:monitor:tape.format) : the description of the format.

### Report issues
Use the [project issues](https://github.com/sporniket/moto-tools/issues) page.