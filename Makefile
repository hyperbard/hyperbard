.ONESHELL:

# Specifies setup type to use for creating hyperbard's environment. By
# default, we prefer an existing `poetry` installation. You can change
# this by calling `make` accordingly:
#
# 		make SETUP=venv
#
# Other options are not supported at the moment.
SETUP := "poetry"

# Sets the data set source to use for processing the raw data. If set to
# "local", uses `rawdata.zip` that is supplied with the repository. When
# set to "global", queries the latest online version.
SOURCE := "local"

# Default prefix for running commands. Can be updated if a virtual
# environment is used.
$(eval PREFIX=poetry run )

RAWDATA = rawdata/alls-well-that-ends-well_TEIsimple_FolgerShakespeare.xml \
					rawdata/a-midsummer-nights-dream_TEIsimple_FolgerShakespeare.xml \
					rawdata/antony-and-cleopatra_TEIsimple_FolgerShakespeare.xml \
					rawdata/as-you-like-it_TEIsimple_FolgerShakespeare.xml \
					rawdata/coriolanus_TEIsimple_FolgerShakespeare.xml \
					rawdata/cymbeline_TEIsimple_FolgerShakespeare.xml \
					rawdata/hamlet_TEIsimple_FolgerShakespeare.xml \
					rawdata/henry-iv-part-1_TEIsimple_FolgerShakespeare.xml \
					rawdata/henry-iv-part-2_TEIsimple_FolgerShakespeare.xml \
					rawdata/henry-viii_TEIsimple_FolgerShakespeare.xml \
					rawdata/henry-vi-part-1_TEIsimple_FolgerShakespeare.xml \
					rawdata/henry-vi-part-2_TEIsimple_FolgerShakespeare.xml \
					rawdata/henry-vi-part-3_TEIsimple_FolgerShakespeare.xml \
					rawdata/henry-v_TEIsimple_FolgerShakespeare.xml \
					rawdata/julius-caesar_TEIsimple_FolgerShakespeare.xml \
					rawdata/king-john_TEIsimple_FolgerShakespeare.xml \
					rawdata/king-lear_TEIsimple_FolgerShakespeare.xml \
					rawdata/loves-labors-lost_TEIsimple_FolgerShakespeare.xml \
					rawdata/macbeth_TEIsimple_FolgerShakespeare.xml \
					rawdata/measure-for-measure_TEIsimple_FolgerShakespeare.xml \
					rawdata/much-ado-about-nothing_TEIsimple_FolgerShakespeare.xml \
					rawdata/othello_TEIsimple_FolgerShakespeare.xml \
					rawdata/pericles_TEIsimple_FolgerShakespeare.xml \
					rawdata/richard-iii_TEIsimple_FolgerShakespeare.xml \
					rawdata/richard-ii_TEIsimple_FolgerShakespeare.xml \
					rawdata/romeo-and-juliet_TEIsimple_FolgerShakespeare.xml \
					rawdata/the-comedy-of-errors_TEIsimple_FolgerShakespeare.xml \
					rawdata/the-merchant-of-venice_TEIsimple_FolgerShakespeare.xml \
					rawdata/the-merry-wives-of-windsor_TEIsimple_FolgerShakespeare.xml \
					rawdata/the-taming-of-the-shrew_TEIsimple_FolgerShakespeare.xml \
					rawdata/the-tempest_TEIsimple_FolgerShakespeare.xml \
					rawdata/the-two-gentlemen-of-verona_TEIsimple_FolgerShakespeare.xml \
					rawdata/the-winters-tale_TEIsimple_FolgerShakespeare.xml \
					rawdata/timon-of-athens_TEIsimple_FolgerShakespeare.xml \
					rawdata/titus-andronicus_TEIsimple_FolgerShakespeare.xml \
					rawdata/troilus-and-cressida_TEIsimple_FolgerShakespeare.xml \
					rawdata/twelfth-night_TEIsimple_FolgerShakespeare.xml

all: setup preprocess representations

representations: preprocess
	@$(PREFIX) python3 src/hyperbard/create_graph_representations.py
	@$(PREFIX) python3 src/hyperbard/create_hypergraph_representations.py

preprocess: $(RAWDATA)
	@$(PREFIX) python3 src/hyperbard/run_preprocessing.py

$(RAWDATA):
	@echo "Checking whether raw data needs to be extracted..."
	make -C rawdata SOURCE=$(SOURCE)

# Sets up a virtual environment or a `poetry` environment, depending on
# the configuration of the user.
setup:
ifeq ($(SETUP),venv)
	@echo "Using 'venv' to create virtual environment"
	python3 -m venv .venv
	. .venv/bin/activate
	$(eval PREFIX=)
else
	@echo "Using 'poetry' to create virtual environment"
	poetry install
	$(eval PREFIX=poetry run )
endif
