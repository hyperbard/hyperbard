#!/bin/sh

zip -r hyperbard_data.zip rawdata data graphdata metadata/playtypes.csv DATALICENSE -x "__MACOSX" -x ".DS_Store" -x "*/.DS_Store" -x "*/Makefile"