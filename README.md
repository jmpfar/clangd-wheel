# clangd Python distribution

[![PyPI Release](https://img.shields.io/pypi/v/clangd.svg)](https://pypi.org/project/clangd)

This project packages the `clangd` utility as a Python package. It allows you to install `clangd` directly from PyPI:

```
python -m pip install clangd
```

This projects intends to release a new PyPI package for each major and minor release of `clangd`.

## Use with pipx

You can use `pipx` to run clangd, as well. For example, `pipx run clangd <args>` will run clangd without any previous install required on any machine with pipx (including all default GitHub Actions / Azure runners, avoiding requiring a pre-install step or even `actions/setup-python`).

## Building new releases

The [clangd-wheel repository](https://github.com/jmpfar/clangd-wheel) provides the logic to build and publish binary wheels of the `clangd` utility.

In order to add a new release, the following steps are necessary:

* Edit the [version file](https://github.com/jmpfar/clangd-wheel/blob/main/clangd_version.cmake) to reflect the new version.
* Make a GitHub release to trigger the [GitHub Actions release workflow](https://github.com/jmpfar/clangd-wheel/actions/workflows/release.yml). Alternatively, the workflow can be triggered manually.

On manual triggers, the following input variables are available:
* `llvm_version`: Override the LLVM version (default: `""`)
* `wheel_version`: Override the wheel packaging version (default `"0"`)
* `deploy_to_testpypi`: Whether to deploy to TestPyPI instead of PyPI (default: `false`)

The repository with the precommit hook is automatically updated using a scheduled Github Actions workflow.

## Acknowledgments

This repository extends the great work of several other projects:

* This is a fork of the [clang-tidy-wheel](https://github.com/ssciwr/clang-tidy-wheel) project, 
  and their original work was used to create a wheel for clangd.
* `clangd` itself is [provided by the LLVM project](https://github.com/llvm/llvm-project) under the Apache 2.0 License with LLVM exceptions.
* The build logic is based on [scikit-build](https://github.com/scikit-build/scikit-build) which greatly reduces the amount of low level code necessary to package `clangd`.
* The `scikit-build` packaging examples of [CMake](https://github.com/scikit-build/cmake-python-distributions) and [Ninja](https://github.com/scikit-build/ninja-python-distributions) were very helpful in packaging `clangd`.
* The CI build process is controlled by [cibuildwheel](https://github.com/pypa/cibuildwheel) which makes building wheels across a number of platforms a pleasant experience (!)

We are grateful for the generous provisioning with CI resources that GitHub currently offers to Open Source projects.

## Troubleshooting

To see which clangd binary the package is using
you can set `CLANGD_WHEEL_VERBOSE` to `1` in your environment.
