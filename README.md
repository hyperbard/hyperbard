# hyperbard
All the world's a (hyper)graph: drama data for data drama

<a href="https://codeclimate.com/repos/62a1a44d41bc7c32f8029bc8/maintainability"><img src="https://api.codeclimate.com/v1/badges/bf9e6df4ada06f51bd91/maintainability" /></a>
[![codecov](https://codecov.io/gh/hyperbard/hyperbard/branch/main/graph/badge.svg?token=D5QIXPFRB2)](https://codecov.io/gh/hyperbard/hyperbard)

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
$ ./setup.sh poetry
```

Alternatively, if you wish to use `venv` instead of `poetry`, run the
following command:

```bash
$ ./setup venv
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

## Manual installation and overview

We recommend using the [`poetry`](https://python-poetry.org) package and
dependency manager to install this work:

```bash
$ poetry install
```

The following commands will thus be prefixed with `poetry run`. If you
want to use another package manager or another type of virtual
environment, just drop the prefix altogether and interact with the local
Python executable of your environment, i.e. the environment you get
after running `. .venv/bin/activate`, for instance.

## Extracting the raw data

Normally, this step is performed by the pipeline script. In case you
want to run this step manually, create a folder `rawdata` in the root
directory of this repository and extract the `rawdata.zip` into it:

```bash
$ unzip rawdata.zip -d rawdata/
```

## Pre-processing

Prior to analysing the (hyper)graphs, we first need to pre-process the
data. This requires running the `run_preprocessing.py` script:

```bash
$ poetry run python src/hyperbard/run_preprocessing.py
```

This will create CSV files and store them in the `data` folder of the
repository. This script will not overwrite files after running it
a second time. You can either delete the `data` folder or call the
pre-processing script with an additional parameter `-f` or `--force`:

```bash
$ poetry run python src/hyperbard/run_preprocessing.py --force
```

The rationale behind this decision is that pre-processing takes
a moderate amount of time and usually only has to be done once.

## Creating summary statistics of the raw data

This will enable you to reproduce Fig. 1 in the paper, which depicts the
statistics of our data set *prior* to converting plays into different
representations:

```bash
$ poetry run python src/hyperbard/raw_summary_statistics.py
```
