# vim: noet
# Make the files needed for the lookup.py script from the WordNet 3.0
# installation.  The WordNet package needs to be installed in the
# directory ./WordNet-3.0 relative to where this makefile is.
# The PYTHON environment variable must point to the python executable.

# If you install WordNet somewhere else, put its directory here
W = WordNet-3.0

# This is the destination of the WordNet dictionary file, which
# contains one word per line.  Besides the files given in the all
# target below, this dictionary file will be needed by lookup.py.
words_dict = ../../words.wordnet

data  = data.adj data.adv data.noun data.verb
index = index.sense
tools = mkwords.py 
ludir = lookup
p     = ../..
pylib_files = $p/lookup.py $p/wrap.py $p/color.py $p/simple.py \
		  	  $p/words.pdf

.PHONY: ${data} ${index} pkg

all:  ${data} ${index} ${tools}
	${PYTHON} mkwords.py ${index} ${words_dict}

data.adj: $W/dict/data.adj
	cp $< $@
data.adv: $W/dict/data.adv
	cp $< $@
data.noun: $W/dict/data.noun
	cp $< $@
data.verb: $W/dict/data.verb
	cp $< $@
index.sense: $W/dict/index.sense
	cp $< $@

# Make the zip file for distribution
pkg:
	rm -rf ${ludir}
	mkdir ${ludir}
	cp ${pylib_files} ${ludir}
	cp mkwords.py makefile ${ludir}
	rm -f lookup.zip
	zip -9q lookup.zip ${ludir}/*
	mv lookup.zip lookup_$(shell /bin/date +%d%b%Y).zip
