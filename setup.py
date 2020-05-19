from setuptools import setup, find_packages


setup(
    name="aiocells",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    license="Not Open Source",
    install_requires=[
        "click==7.0",
    ],
    entry_points={
        "console_scripts": [
            "aiocells = aiocells.cli:main",
        ]
    },
)
