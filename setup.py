#!/usr/bin/env python3
# vim: set filetype=python sts=4 ts=4 sw=4 expandtab tw=100 cc=+1:

# https://docs.python.org/2/distutils/sourcedist.html
# https://docs.python.org/2/distutils/configfile.html
# https://docs.python.org/2/distutils/setupscript.html#additional-meta-data

# https://docs.python.org/3/distutils/sourcedist.html
# https://docs.python.org/3/distutils/introduction.html#distutils-simple-example
# https://docs.python.org/3/distutils/setupscript.html#additional-meta-data

# https://setuptools.readthedocs.io/en/latest/
# https://setuptools.readthedocs.io/en/latest/setuptools.html#new-and-changed-setup-keywords

import os
import setuptools
import versioneer

SCRIPT_DIRNAME = os.path.dirname(__file__)
SCRIPT_DIRNAMEA = os.path.abspath(SCRIPT_DIRNAME)
SCRIPT_BASENAME = os.path.basename(__file__)

DESCRIPTION_CONTENT = "..."
#with open(os.path.join(SCRIPT_DIRNAME, "DESCRIPTION.md"), encoding="utf-8") as fstream:
#    DESCRIPTION_CONTENT = fstream.read()

setuptools.setup(
    name="laicheil.force2019",
    url="https://example.com/",
    description="...",
    long_description=DESCRIPTION_CONTENT,
    long_description_content_type="text/markdown",
    license="MIT",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    package_dir={"":"src"},
    packages=setuptools.find_namespace_packages(where="src", exclude=["contrib", "docs", "tests"]),
    #packages=setuptools.find_packages(where="src", exclude=["contrib", "docs", "tests"]),
    py_modules=[],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "laicheil.force2019.cli=laicheil.force2019.cli:main",
        ],
    },
    install_requires=[
    ],
    setup_requires=["pytest-runner", "pytest-pylint"],
    tests_require=["pytest", "pylint"],
    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage", "pytest", "pytest-pylint", "pylint"],
    },
    zip_safe=False,
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
    ],
    keywords="",
    python_requires=">=3, <4",
)
