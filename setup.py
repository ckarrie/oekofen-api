from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="oekofen_api",
    version="0.0.3",
    author="Christian Karrié",
    author_email="ckarrie@gmail.com",
    description="A python library to retrieve statistics from your Oekofen Pelletronic",
    download_url='https://github.com/ckarrie/oekofen-api/archive/refs/tags/v0.0.3.tar.gz',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ckarrie/oekofen-api",
    packages=find_packages(),
    install_requires=[
        'aiohttp>=3.8.1',
        'voluptuous>=0.13.1'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
