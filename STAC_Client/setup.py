from setuptools import setup, find_packages

setup(
    name="stac_cli",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "click"
    ],
    entry_points={
        "console_scripts": [
            "stac_cli=stac_cli.cli:stac_cli"
        ]
    },
)