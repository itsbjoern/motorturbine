# Motorturbine

[![CircleCI](https://circleci.com/gh/BFriedrichs/motorturbine.svg?style=shield)](https://circleci.com/gh/BFriedrichs/motorturbine)
[![RTD](https://readthedocs.org/projects/motorturbine/badge/?version=latest)](https://motorturbine.readthedocs.io/en/latest/)
[![PyPI](https://img.shields.io/pypi/v/motorturbine.svg?colorB=brightgreen)](https://pypi.org/project/motorturbine/)

Motorturbine is an adapted version of the [Motorengine ORM](https://motorengine.readthedocs.io/en/latest/). The main goals are proper asyncio integration as well as a way to have more control over safe updates. Many ORMs suffer from parallelism issues and one big part of this package is to introduce transactions with retry capabilities when updating the fields of a document.

## Installation
````
pip install motorturbine
````

## Documentation

Please read the documentation for further information.
https://motorturbine.readthedocs.io/en/latest/

## Todo List

* [ ] Date Field
* [ ] Unique Parameter
* [ ] Push / Pull Update Operators
* [ ] References

