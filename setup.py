"""
Setup configuration for Our Family Wizard Python Client
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ofw-client",
    version="0.3.1",
    author="kherry",
    author_email="kherry@zamore.net",
    description="Python client for Our Family Wizard co-parenting app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kherry/ofw-client",
    py_modules=["ofw_client"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
	"selenium>=4.15.0",
	"webdriver-manager>=4.0.0",
    ],
)
