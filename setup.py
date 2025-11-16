"""
Setup configuration for MirrorDNA.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="mirrordna",
    version="1.0.0",
    author="MirrorDNA-Reflection-Protocol",
    description="Identity and continuity protocol layer for AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MirrorDNA-Reflection-Protocol/MirrorDNA",
    project_urls={
        "Bug Tracker": "https://github.com/MirrorDNA-Reflection-Protocol/MirrorDNA/issues",
        "Documentation": "https://github.com/MirrorDNA-Reflection-Protocol/MirrorDNA/tree/main/docs",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "jsonschema>=4.0.0",
        "cryptography>=40.0.0",
        "pyyaml>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "mirrordna=mirrordna.cli:main",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
        ],
        "api": [
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
            "pydantic>=2.0.0",
        ],
        "postgresql": [
            "sqlalchemy>=2.0.0",
            "psycopg2-binary>=2.9.0",
        ],
        "mongodb": [
            "pymongo>=4.0.0",
        ],
        "all": [
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
            "pydantic>=2.0.0",
            "sqlalchemy>=2.0.0",
            "psycopg2-binary>=2.9.0",
            "pymongo>=4.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="ai agents identity continuity memory protocol mirrordna",
    license="MIT",
)
