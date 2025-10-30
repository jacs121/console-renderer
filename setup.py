from setuptools import setup, find_packages

setup(
    name="Term-gfx",
    version="1.0.0",
    author="Nitzan Soriano",
    license="MIT AND (Apache-2.0 OR BSD-2-Clause)",
    author_email="nitzansoriano1@example.com",
    url="https://github.com/jacs121/console-renderer",
    description="A terminal-based graphics library for Python",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.7",
    install_requires=[
        "colorama>=0.4.4",
        "pillow>=8.0.0",
        "numpy>=1.19.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
        ],
    }
)