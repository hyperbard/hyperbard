# hyperbard
All the world's a (hyper)graph: drama data for data drama

[![codecov](https://codecov.io/gh/dataspider/hyperbard/branch/main/graph/badge.svg?token=D5QIXPFRB2)](https://codecov.io/gh/dataspider/hyperbard)

- [Folger Shakespeare](https://shakespeare.folger.edu/download-the-folger-shakespeare-complete-set/) (our data source)
- [Oxford Shakespeare](https://oll.libertyfund.org/title/shakespeare-the-complete-works-of-william-shakespeare-part-1-the-oxford-shakespeare)

## Requirements

Our code has been tested with Python 3.8 and Python 3.9 under Mac OS
X and Linux. Other Python versions *may* not support all dependencies,
whereas Windows is *not* a support operating system.

## Quickstart

We recommend using [`poetry`](https://python-poetry.org) for package and
dependency management. Our main pipeline also supports standard virtual
environments, as created via the `venv` package. To run the pipeline and
create all figures run the following command:

```bash
$ make
```

Alternative, if you wish to use `venv` instead of `poetry`, run the
following command:

```bash
$ make SETUP=venv
```

## Installation and overview

We recommend using the [`poetry`](https://python-poetry.org) package and
dependency manager to install this work:

```bash
$ poetry install
```

Here is an overview of the directory structure after running the
subsequent pre-processing steps:

```
├── data                # Will contain processed data in CSV format
├── graphdata           # Will contain graphs and hypergraphs
├── graphics            # Will contain graphics
├── metadata            # Metadata information about plays
├── notebooks           # Notebooks for analysis tasks
├── rawdata             # Raw data in XML format
├── rawdata_statistics  # Statistics about raw data
├── src                 # Code and scripts
└── tests               # Unit tests
```

## Extracting the raw data

Create a folder `rawdata` in the root directory of this repository and
extract the `rawdata.zip` into it:

```bash
$ unzip rawdata.zip -d rawdata/
```

## Usage

Prior to analysing the (hyper)graphs, we first need to pre-process the
data. This requires running the `run_preprocessing.py` script:

```bash
$ cd src/hyperbard
$ poetry run python run_preprocessing.py
```

This will create CSV files and store them in the `data` folder of the
repository. This script is idempotent; it will refresh all files upon
a new run.

## Creating summary statistics of the raw data

This will enable you to reproduce Fig. 1 in the paper, which depicts the
statistics of our data set *prior* to converting plays into different
representations:

```bash
$ cd src/hyperbard
$ python summary_statistics_raw.py
```
