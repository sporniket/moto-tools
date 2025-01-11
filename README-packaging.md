# How to build and publish a python package

_See https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives_

> `pipx` is required

## Pre-checking

```shell
pipx install pdm
```

## Build and install locally

> This is what is done by the `retest` shell script.

```shell
pdm run make
```

Run test suites with coverage tracking and reporting :

```shell
python run ci
```

Run test suites only :

```shell
python run test
```

## Publish on pypi

Check list
- [ ] Code complete and passing tests
- [ ] setup.cfg has the right version
- [ ] Readme up to date (MUST include release notes for the release to publish)
- [ ] Tagged with git using matching version ('v' + version)

Display the token so that a copy/paste is prepared. Then use the login `__token__`, and paste the token as the password.

```shell
python3 -m twine upload --repository pypi dist/*
```
