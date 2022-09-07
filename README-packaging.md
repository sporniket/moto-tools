# How to build and publish a python package

_See https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives_

## Pre-checking

```shell
python3 -m pip install --upgrade pip build pytest twine black coverage
```

## Build and install locally

> This is what is done by the `retest` shell script.

```shell
python3 -m black 
python3 -m build
python3 -m pip install --force-reinstall dist/xxx.whl
```

Run test suites with coverage tracking and reporting :

```shell
python3 -m coverage run --source=electronic_symbol_generator_for_cad --branch -m pytest
python3 -m coverage report -m
python3 -m coverage html 
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
