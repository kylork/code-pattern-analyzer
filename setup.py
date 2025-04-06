from setuptools import setup, find_packages

setup(
    name="code-pattern-analyzer",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "code-pattern=src.cli:main",
        ],
    },
    install_requires=[
        "tree-sitter",
        "pyyaml",
        "click",
    ],
    python_requires=">=3.8",
)