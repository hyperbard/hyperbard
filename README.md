# hyperbard
All the world's a (hyper)graph: drama data for data drama

<a href="https://codeclimate.com/repos/62a1a44d41bc7c32f8029bc8/maintainability"><img src="https://api.codeclimate.com/v1/badges/bf9e6df4ada06f51bd91/maintainability" /></a>
[![codecov](https://codecov.io/gh/hyperbard/hyperbard/branch/main/graph/badge.svg?token=D5QIXPFRB2)](https://codecov.io/gh/hyperbard/hyperbard)
[![Documentation Status](https://readthedocs.org/projects/hyperbard/badge/?version=latest)](https://hyperbard.readthedocs.io/en/latest/?badge=latest)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/hyperbard/sandbox/main?urlpath=git-pull%3Frepo%3Dhttps%253A%252F%252Fgithub.com%252Fhyperbard%252Ftutorials%26urlpath%3Dlab%252Ftree%252Ftutorials%252Fnotebooks%252Fwelcome.ipynb%26branch%3Dmain)

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
$ ./setup.sh venv
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

## Running the pipeline

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

**Using `make`**: If your virtual environment is activated and set up
correctly, you can always just use `make` to run *all* steps of the
pipeline:

```bash
$ make      # Run the pipeline
$ make all  # Also runs the pipeline but is a little bit more verbose
```

If you want to run an individual step only, use the `target` indicated
in each of the subsequent steps. For instance, to run only the
pre-processing step, you can run the following command:

```bash
$ make preprocess
```

We have set up our pipeline such that individual targets know their
prerequisites; it is therefore possible to run only a single step---for
instance the creation of plots---and `make` will ensure that all
required data is available.

### Extracting the raw data

Normally, this step is performed by the pipeline script. In case you
want to run this step manually, create a folder `rawdata` in the root
directory of this repository and extract the `rawdata.zip` into it:

```bash
$ unzip rawdata.zip -d rawdata/
```

### Pre-processing (`make preprocess`)

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

### Creating summary statistics of the raw data (`make raw_summary_statistics`)

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

### Creating (hyper)graph representations (`make representations`)

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

### Plotting different representations of "Romeo & Juliet" (`make plot_romeo`) 

To obtain the different representations depicted in Fig. 2, Fig. 3, and
Fig. 4, run the `plot_romeo.py` script:

```bash
$ python src/hyperbard/plot_romeo.py
```

#### Output

This script will generate new graphics in the `paper_graphics` folder,
depicting the individual representations:

```
romeo_and_juliet_ce-3-differences.pdf
romeo_and_juliet_ce-group-mw-3.pdf
romeo_and_juliet_ce-scene-b.pdf
romeo_and_juliet_ce-scene-mb.pdf
romeo_and_juliet_ce-scene-mw-3.pdf
romeo_and_juliet_ce-scene-mw.pdf
```

### Plotting the toy example from the paper (`make plot_toy`)

To plot the toy example of a network as depicted in Fig. 5 of the paper,
use the `plot_toy.py` script:

```bash
$ poetry run python src/hyperbard/plot_toy.py
```

#### Output

This will create three figures in the `paper_graphics` folder in the
root directory of the repository: 

```
toy_drama_ce.pdf
toy_drama_hg.pdf
toy_drama_se.pdf
```

The figures illustrate the clique expansion (`_ce`), the star expansion
(`_se`), and the hypergraph representation (`_hg`) of the scene,
respectively.

### Plotting rank correlations for different graph representations (`make plot_rank_correlations`)

One of the major points of our paper is that representations differ in
expressive power and in information flow. To see how the ranking for
"Romeo & Juliet" correlates over different representations and how these
correlations compare to the average correlation across the corpus, we
show a partitioned matrix in Fig. 7. This figure can be reproduced by
the following script:

```
$ poetry run python src/hyperbard/plot_rank_correlations.py
```

#### Output

The script will create a figure called `romeo-and-juliet_rank-correlations.pdf`
in `paper_graphics`, showing the correlation and its comparison to the
overall correlations in the corpus.

### Plotting rankings for different graph representations (`make plot_graph_rankings`)

To further illustrate our point about the differences in expressive
power for characters, we also show how the ranking of named characters
in the plays changes as a function of the selected representation. This
is depicted by Fig. 8, which can be reproduced by the following script:

```
$ poetry run python src/hyperbard/plot_graph_rankings.py
```

#### Output

This script will create parallel coordinate plots (similar in style to
Fig. 8)  for each of the plays, which are stored in the `graphics`
folder. Fig. 8 itself, for example, will be stored as
`romeo-and-juliet_ranking_parallel_coordinates.pdf`.

Note that these visualisations *only* incorporate named characters; the
rankings may potentially change if *all* characters, even those without
a speaking role, will be used.

In addition to the graphics, the folder `rankingdata` in the root
directory of the repository will contain CSV files that contain the
ranks of named characters (rows) according to different representations
(columns). Here's an example ranking file for "Romeo & Juliet":

```
$ cat rankingdata/romeo-and-juliet_ranking.csv
index,ce-scene-b,ce-scene-mb,ce-scene-mw,ce-group-b,ce-group-mb,ce-group-mw,se-scene-b,se-scene-w,se-group-b,se-group-w,se-speech-wd_in,se-speech-wd_out
Abram,14.0,15.0,15.0,12.0,13.0,18.0,17,16,14,20,20,20
Apothecary,22.0,22.0,22.0,22.0,22.0,22.0,17,22,23,22,22,19
Balthasar,17.0,15.0,14.0,16.0,10.0,11.0,14,15,10,10,9,15
```

### Plotting rankings for different hypergraph representations (`make plot_hypergraph_rankings`)

Expanding on the previous point, hypergraphs offer even more
opportunities for modelling! The usual graph properties typically
translate into equivalent concepts in the hypergraph domain, but the
increased expressivity also entails additional complexity. To showcase
this, we plot the ranking of characters as a function of various notions
of degree. Notice that hypergraphs permit a more granular analysis here;
essentially, every node can be characterised by the number of edges of
a specific cardinality $s$ it participates in. Treating $s$ as
a lower-level or an upper-level threshold, respectively, we obtain
a different set of rankings, all of which are depicted in Fig. 9.

Re-creating this figure requires running `plot_hypergraph_rankings.py`:

```
$ poetry run python src/hyperbard/plot_hypergraph_rankings.py
```

#### Output

This script will create parallel coordinate plots (similar in style to
Fig. 8, but depicting the ranking changes as a function of various
notions of hypergraph degrees) for each of the plays, which are stored
in the `graphics` folder. Fig. 9 itself, for example, will be stored as
`romeo-and-juliet_hg_ranking_parallel_coordinates.pdf`.

(Similar to the previous visualisations, all of these plots only
incorporate *named characters*.)
