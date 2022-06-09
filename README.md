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

### Extracting the raw data

Normally, this step is performed by the pipeline script. In case you
want to run this step manually, create a folder `rawdata` in the root
directory of this repository and extract the `rawdata.zip` into it:

```bash
$ unzip rawdata.zip -d rawdata/
```

### Pre-processing

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

#### Output

This script will place pre-processed CSVs in `data`. Three
files will be created for each play. For instance:

```
romeo-and-juliet.agg.csv
romeo-and-juliet.cast.csv
romeo-and-juliet.raw.csv
```

The `raw` file contains a representation of the full play, including
individual comments on which tokens are being uttered by which
character. The `agg` file contains an aggregated representation of the
data, following the granularity dimensions outlined in the paper. We
build all our (hyper)graph representations from such data. Finally, the
`cast` file contains information about the cast present in a play.

### Creating summary statistics of the raw data

This will enable you to reproduce the raw statistics of Fig. 1 in the
paper, which depicts the statistics of our data set *prior* to
converting plays into different representations:

```bash
$ poetry run python src/hyperbard/raw_summary_statistics.py
```

#### Output

This step does *not* entail creating the actual figure but only a CSV
file containing the summary statistics. You can find this CSV file under
`metadata/summary_statistics_raw.csv`.

### Creating (hyper)graph representations

From the pre-processed CSV files, various (hyper)graph representations
can be created and stored in `graphdata`. To create the graphs, call the
script `create_graph_representations.py`:

```bash
$ poetry run python src/hyperbard/create_graph_representations.py
Found 37 files to process.
a-midsummer-nights-dream
alls-well-that-ends-well
antony-and-cleopatra
as-you-like-it
[...]
twelfth-night
```

The script iterates over all 37 plays and stores its various outputs in
`graphdata`. Next, let's create hypergraphs as well:

```bash
$ poetry run python src/hyperbard/create_hypergraph_representations.py
Found 37 files to process.
a-midsummer-nights-dream
alls-well-that-ends-well
antony-and-cleopatra
as-you-like-it
[...]
twelfth-night
```

#### Output

The `graphdata` folder will now contain a set of files containing edges
and nodes of the various representations. Here is an excerpt of the
files you will get:

```
romeo-and-juliet_ce-group-mw.edges.csv
romeo-and-juliet_ce-group-w.edges.csv
romeo-and-juliet_ce.nodes.csv
romeo-and-juliet_ce-scene-mw.edges.csv
romeo-and-juliet_ce-scene-w.edges.csv
romeo-and-juliet_hg-group-mw.edges.csv
romeo-and-juliet_hg-group-mw.node-weights.csv
romeo-and-juliet_hg.nodes.csv
romeo-and-juliet_hg-scene-mw.edges.csv
romeo-and-juliet_hg-scene-mw.node-weights.csv
romeo-and-juliet_hg-speech-mwd.edges.csv
romeo-and-juliet_hg-speech-wd.edges.csv
romeo-and-juliet_se-group.nodes.csv
romeo-and-juliet_se-group-w.edges.csv
romeo-and-juliet_se-scene.nodes.csv
romeo-and-juliet_se-scene-w.edges.csv
romeo-and-juliet_se-speech-mwd.edges.csv
romeo-and-juliet_se-speech.nodes.csv
romeo-and-juliet_se-speech-wd.edges.csv
```
