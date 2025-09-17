#!/usr/bin/env python3
"""
Setup script for Touch Bar Coding Assistant
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open("requirements.txt", "r") as f:
    requirements = [
        line.strip() for line in f if line.strip() and not line.startswith("#")
    ]

setup(
    name="touch-bar-coding-assistant",
    version="1.0.0",
    author="Touch Bar Coding Assistant Team",
    author_email="support@example.com",
    description="A Python application that uses the Apple Touch Bar to search for coding interview questions using Azure OpenAI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/touch-bar-coding-assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Education",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "flake8>=5.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "touch-bar-assistant=main:main",
            "tbca=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "app": ["*.py", "*.md"],
    },
    keywords="touch-bar, coding, interview, azure, openai, python, macos",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/touch-bar-coding-assistant/issues",
        "Source": "https://github.com/yourusername/touch-bar-coding-assistant",
        "Documentation": "https://github.com/yourusername/touch-bar-coding-assistant#readme",
    },
)
