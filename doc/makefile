# vim: noet

# Makefile for 0readme and 0readme.html in the hobbyutil directory.
# Note:  as of writing this makefile, the ts.py script is not part of
# the hobbyutil project yet (it's still under development).  If it's
# not in prog/ts of the project, then you'll have to wait until it's
# released.

# Converts restructured text file into HTML
r2h = /usr/local/bin/rst2html.py
# Text substitution tool
tspy = /pylib/pgm/ts/ts.py

all:  ../0readme ../0readme.html
../0readme.html:  hu.rst hu.css
	${r2h} --stylesheet hu.css hu.rst >$@
../0readme:  hu.rst 
	cp $< $@
hu.rst:  hu.ts hu.list
	python ${tspy} hu.ts >$@
hu.css: hu.css.ts
	python ${tspy} $< >$@
hu.list: ../hu.py
	python ../hu.py list | sed -e 's/^/    /' > $@
hu.css.ts:

clean:
	rm -f ../0readme.html ../0readme hu.rst hu.list
