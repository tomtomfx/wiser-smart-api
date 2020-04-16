import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wiser-smart-api",
    version="1.0.0",
    author="Thomas Fayoux",
    author_email="thomas.fayoux@gmail.com",
    description="A simple API for accessing data on the Schneider Wiser Smart system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tomtomfx/wiser-smart-api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
