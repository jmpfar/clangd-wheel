
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
from skbuild import setup

import re

class genericpy_bdist_wheel(_bdist_wheel):
    def finalize_options(self):
        _bdist_wheel.finalize_options(self)
        self.root_is_pure = False

    def get_tag(self):
        python, abi, plat = _bdist_wheel.get_tag(self)
        python, abi = "py2.py3", "none"
        return python, abi, plat

# Read the clangd version from the "single source of truth"
def get_version():
    with open("clangd_version.cmake", "r") as version_file:
        parsed = {}
        for line in version_file:
            match = re.match("set\((.*) (.*)\)", line)
            if len(match.groups()) != 2:
                raise ValueError("Version File not readable")
            parsed[match.groups()[0]] = match.groups()[1]
        if parsed["CLANGD_WHEEL_VERSION"] == "0":
            return f"{parsed['CLANGD_VERSION']}"
        else:
            return f"{parsed['CLANGD_VERSION']}.{parsed['CLANGD_WHEEL_VERSION']}"


# Parse the given README file
with open("README.md", "r") as readme_file:
    readme = readme_file.read()

cmdclass = {"bdist_wheel": genericpy_bdist_wheel}
setup(
    name="clangd",
    version=get_version(),
    cmdclass=cmdclass,
    author="Dan Ilan",
    packages=["clangd"],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "clangd=clangd:clangd",
        ]
    },
    description="binaries for clangd, a clang-based C++ language server (LSP)",
    long_description=readme,
    long_description_content_type="text/markdown",
    project_urls={
        "Documentation": "https://clangd.llvm.org/",
        "Source": "https://github.com/jmpfar/clangd-wheel",
    },
    keywords=["clangd", "lsp", "language-server", "llvm", "clang", "static-analysis"],
    classifiers=[
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: C",
        "Programming Language :: C++",
        "Topic :: Software Development",
    ],
    license="Apache 2.0",
)
