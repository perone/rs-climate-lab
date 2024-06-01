from typing import List

import setuptools

development_requires: List[str] = [
    "pytest>=8.2.1",
    "mypy>=1.10.0",
    "flake8>=7.0.0",
    "pytest-cov>=5.0.0",
    "Sphinx>=7.3.7",
    "furo>=2024.5.6",
    "isort>=5.13.2",
    "twine>=5.1.0",
    "sphinx-autobuild>=2024.4.16",
]

setuptools.setup(
    name="rsclimatelab",
    version="0.1.0",
    author="Christian S. Perone",
    author_email="christian.perone@gmail.com",
    description="A project focused on climate data and tooling for "
                "Rio Grande do Sul in Brazil.",
    url="https://github.com/perone/rs-climate-lab",
    install_requires=[
        "rich>=13.7.0",
        "dask[complete]>=2024.5.2",
    ],
    extras_require={
        'dev': development_requires,
    },
    project_urls={
        "Bug Tracker": "https://github.com/perone/rs-climate-lab/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.10",
    include_package_data=True,
)