from setuptools import setup, find_packages

setup(
    name="code-pattern-analyzer",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "code-pattern=src.cli:main",
            "code-pattern-web=src.web.cli:main",
        ],
    },
    install_requires=[
        "tree-sitter>=0.20.0",
        "pyyaml>=6.0",
        "click>=8.0.0",
    ],
    extras_require={
        "web": [
            "fastapi>=0.78.0",
            "uvicorn>=0.17.0",
            "pydantic>=1.9.0",
            "python-multipart>=0.0.5",
            "aiofiles>=0.8.0",
            "requests>=2.27.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
        ],
    },
    python_requires=">=3.8",
)