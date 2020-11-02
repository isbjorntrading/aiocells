import pathlib

from setuptools import setup, find_packages

THIS_DIR = pathlib.Path(__file__).parent
README = (THIS_DIR / "README.md").read_text()

setup(
    name="aiocells",
    version="0.3.3",
    python_requires=">=3.8",
    description="A package for synchronous and asynchronous"
                " dependency graph computation",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/isbjorntrading/aiocells",
    author="Anders Lindstrom",
    author_email="anders@isbjorn.com.au",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "click>=7.0",
    ],
    entry_points={
        "console_scripts": [
            "aiocells = aiocells.cli:main",
        ]
    },
)
