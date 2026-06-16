# -*- coding: utf-8 -*-
import os
from setuptools import setup

current_path = os.path.abspath(os.path.dirname(__file__))

requirements = (
    "tracklib",
    "fiona",
    "shapely",
    "psutil"
)

setup (
    name="footprint2graph",
    version="1.1",
    description="footprint2graph is an open-source Python processing pipeline (MIT license) for generating outdoor activity footprint networks from GNSS trajectories, representing, for example, hikers’ or runners’ footprints within a defined spatial and temporal extent.",
    long_description="See ...",
    url="https://github.com/umrlastig/footprint2graph",
    download_url= 'https://github.com/umrlastig/footprint2graph/archive/refs/tags/v1.0.0.zip',
    author="Marie-Dominique Van Damme, Yann Méneroux",
    author_email="todo@ign.fr",
    keywords=[],
    license="MIT",
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
    ],
    packages = ['footprint2graph','footprint2graph.algo','footprint2graph.pipeline','footprint2graph.util'],
    install_requires=requirements,
    test_suite="tests",
    extras_require={
    },
)
