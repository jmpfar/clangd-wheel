# Clangd python wheel

[![PyPI Release](https://img.shields.io/pypi/v/clangd.svg)](https://pypi.org/project/clangd) [![License](https://img.shields.io/pypi/l/clangd)](https://github.com/jmpfar/clangd-wheel/blob/main/LICENSE.md)

This project packages the `clangd` utility as a Python wheel, supplying the `clangd` binaries for use of python projects or generally as cross-platform statically-linked packages of the utility. 

The wheel can be used when you need to interact with a C/C++ [LSP](https://en.wikipedia.org/wiki/Language_Server_Protocol) server. For example, in static analyzers such as [clangd-tidy](https://github.com/lljbash/clangd-tidy).

The binaries are built using the original [LLVM source releases](https://github.com/llvm/llvm-project/releases), and are uploaded to PyPI using verifiable build attestations.

The project is a fork of the [clang-tidy-wheel](https://github.com/ssciwr/clang-tidy-wheel) project, which is the source for the build and packaging scripts used here, and is based on their original work. 

`clangd` is part of the LLVM project and is licensed under the [Apache License v2.0 with LLVM Exceptions](https://github.com/llvm/llvm-project/blob/main/LICENSE.TXT).

## Usage

Install: 

```
python -m pip install clangd
```

Run:

```
clangd
```

## Builder platforms

| OS       | Version | Architecture | Platform                            |
|----------|---------|--------------|-------------------------------------|
| Ubuntu   | 24.04   | x86_64       | manylinux                           |
| Ubuntu   | 24.04   | x86_64       | [musllinux](https://musl.libc.org/) |
| Ubuntu   | 24.04   | arm64        | manylinux                           |
| Ubuntu   | 24.04   | arm64        | [musllinux](https://musl.libc.org/) |         
| macOS    | 15      | x86_64       |                                     |
| macOS    | 15      | arm64        |                                     |
| Windows  | 2025    | x86_64       |                                     |
| Windows  | 11      | arm64        |                                     |