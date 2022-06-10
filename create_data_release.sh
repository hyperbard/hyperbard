#!/bin/sh

zip -r hyperdata.zip rawdata data graphdata metadata/playtypes.csv -x "__MACOSX" -x ".DS_Store" -x "*/.DS_Store" -x "*/Makefile"