# Motorturbine

[![CircleCI](https://circleci.com/gh/BFriedrichs/motorturbine.svg?style=shield)](https://circleci.com/gh/BFriedrichs/motorturbine)
[![RTD](https://readthedocs.org/projects/motorturbine/badge/?version=latest)](https://motorturbine.readthedocs.io/en/latest/)


Motorturbine is an adapted version of the [Motorengine ORM](https://motorengine.readthedocs.io/en/latest/). The main goals are proper asyncio integration as well as a way to have more control over safe updates. Many ORMs suffer from parallelism issues and one big part of this package is to introduce transactions with retry capabilities when updating the fields of a document.

Please read the documentation for further information.
https://motorturbine.readthedocs.io/en/latest/
