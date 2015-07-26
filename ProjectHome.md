This project is a repository for things I've developed over the years
for my various hobbies.

**Update 27 Aug 2014**:  The primary location for the files is now in
the Mercurial repository under the **Source** link above.  The
deprecated files under the **Download** link have been removed; the ones
that are remaining are larger files that haven't been changed in a
while (they won't move to the repository until they're updated).

There were around 150 different projects (clumps of files) on
this site and I felt this was too many.  I've kept the popular stuff,
but removed things that weren't downloaded very often.  Now there are
roughly about half the number of projects.

To be able to get the files from the Source link, you'll need to have
Mercurial installed on your system; Mercurial is a version control
system.  If you're intimidated by needing to use some arcane piece of
software, don't be -- it's quite easy: download/install Mercurial,
then type a single command.  See the notes at the bottom of this page
for more detail.

The repository is structured with the directory naming scheme shown in
the table below.  Each project will include the source files used to
construct it and possibly a `0readme` file which will explain the
project's nature and use.  A python script will have its documentation
inside the file.  A project is a collection of one or more files.

Here are some other pages that also might be of interest:

  * Python code to talk to a Radio Shack [multimeter](http://code.google.com/p/rs22812/)
  * Python graphics [library](http://code.google.com/p/pygraphicsps/) that outputs Postscript
  * Python code for a console-based RPN [calculator](http://code.google.com/p/hcpy/)
  * Lightweight library for typesafe numerical calculations in C++ using physical [units](http://code.google.com/p/unitscpp/)

The projects in the table below have names of the form cat/name where
cat is the category and name is a short name identifying the project.
The categories are:

| elec | Electrical and electronics |
|:-----|:---------------------------|
| eng  | General engineering/technical |
| math | Mathematics                |
| misc | Miscellaneous              |
| prog | Programming                |
| science | Science                    |
| shop | Shop-related               |
| util | Utilities                  |

The decorations after the names are:  T means a self test python
module is included; 3 means the python code will run under python 3.

| elec/bode  | Generate a Bode plot with a python script (needs numpy and matplotlib).  You define the transfer function in a file which is passed on the command line. |
|:-----------|:---------------------------------------------------------------------------------------------------------------------------------------------------------|
| elec/cs    | A battery-operated 1 ampere current source used to make low resistance measurements.  You can measure to 0.1 milliohm with the typical digital multimeter. |
| elec/esr   | Describes a technique of estimating a capacitor's ESR (equivalent series resistance) without having to buy a special meter.                              |
| elec/rms   | An article for hobbyists about making RMS electrical measurements.                                                                                       |
| eng/pqs    | This package contains python scripts that make it easy to simulate a production process that is inspected by a measurement process with a significant measurement uncertainty.  Such a situation can result in significant producer's and consumer's risk.  It's easy to understand how this Monte Carlo simulation script works and believe its output. |
| math/frange T3 | A python module that provides a floating point analog to range().  Doesn't suffer from the typical floating point problems seen in naive implementations. |
| math/root T3 | Pure-python root-finding methods such as bisection, Brent's method, Ridder's method, Newton-Raphson, and a nice general-purpose method by Jack Crenshaw that uses inverse parabolic interpolation. |
| math/tri   | Python script to solve triangles.                                                                                                                        |
| math/trigd  | Gives some algebraic expressions for a few special values of trigonometric functions in degrees.                                                         |
| math/triguc  | Contains a vector drawing of the trig functions on the unit circle.  The python script used to generate the graphics is included, so you can tweak it to your tastes. |
| math/xyz T3 | Contains a python script that provides a mini-language to perform  analytical geometry calculations in 2 and 3 dimensions. Use translations, rotations, and dilatations to transform to different coordinate systems.  Geometric objects provided are points, lines, and planes. The script can calculate their intersections, reflections, and projections and find angles and distances between them.  Note@  you'll get a python 3 warning because of the use of the sig.py module, but you should get correct output. |
| misc/donor  | A short blurb on organ donation and why it suddenly has become an  important topic for me.                                                               |
| misc/markup  | Derives the equations for markup and profit used in business.                                                                                            |
| misc/shave  | Some thoughts on shaving your beard.                                                                                                                     |
| prog/fset  | Treat lines of files as a set. Allows you to look at the union, intersection, difference, etc. between the lines of various files.                       |
| prog/hg    | Some python scripts that make it easier to work with Mercurial repositories.  delta.py shows you the revision numbers where a file changed; hgs.py shows you things like files that are not in the repository, changed files, etc.  fhg.py will find all Mercurial repositories under a given directory and show those needing a check-in. |
| prog/license  | This is a python script that will allow you to change the license  you use in your source code files.  This is done by replacing a string between two 'trigger' strings.  A number of open source licenses are included in the script (e.g., BSD, GPL2, etc.) and it's easy to include others.  The script will first check that all the indicated source files have the trigger strings and that backup copies of the source files can first be made. |
| prog/odict T3 | A bare-bones ordered dictionary for python. You won't need this if you are on python 2.7 or later because there's a built-in ordered  dictionary.        |
| prog/oopy  | A document explaining how to call python functions from Open Office Calc spreadsheets.                                                                   |
| prog/python  | Contains a document that discusses why learning the python programming language might be a good thing for technical folks.                               |
| prog/seq   | Python script to send various arithmetical progressions to stdout.  Handles integers, floating point, and fractions. Also see fseq.py.                   |
| prog/sig T3 | Contains a python script to format floating point numbers to a specified number of significant figures or round to a specified template. Works with floats, integers, python Decimals, fractions, mpmath numbers, numpy arrays, complex numbers, and numbers with uncertainty, including any mix of those number types in a container that can be iterated over. |
| prog/util T3 | Contains a number of miscellaneous python functions I've written and collected from the web.                                                             |
| prog/wordnum T3 | A python script that can convert back and forth between numbers and their word forms.  Handles short and long scales, ordinals, integers, floats (normal and exponential notation), and fractions.  Easy interface through an object's function call; wordnum(36) gives 'thirty six'; wordnum('thirty six') returns the integer 36.  Tested on python 2.7.6 and 3.4.0. |
| prog/xref  | A C++ console program that will cross reference the tokens in a set of files -- each token will be listed in alphabetical order with the file it occurs in along with the line numbers it's found on.  It can perform spell checking.  It has a -k option which will split composite tokens in the source code and spell check the individual tokens (this helps identify composite tokens that are misspelled). |
| science/chemname  | A list of archaic chemical names with their modern equivalents and chemical formulas.                                                                    |
| science/mixture  | A python script to aid in mixture calculations. Adapted from a C program at http://www.myvirtualnetwork.com/mklotz/files/mixture.zip.                    |
| science/sphshell  | Discusses gravitation and electrostatics inside a uniform spherical shell and why there is no force on a particle. Also looks at Henry Cavendish's elegant experiment in the 1700's showing that the exponent in Coulomb's Law is 2. |
| science/u T3 | A lightweight python library module that provides conversion factors for various physical units.  Using a clever idea by Steve Byrnes, it can also perform dimensional checking to determine dimensional consistency of numerical calculations. Easy to use -- an experienced scientist or engineer will be using it in a few minutes after seeing an example (see the PDF in the package for details). |
| science/units  | A short blurb on the capabilities of the wonderful GNU units program.  This is one of the most-used programs on my computer because I am constantly converting between various units. It can also help you do back-of-the-envelope type calculations and avoid making dumb unit mistakes that invalidate everything. |
| shop/ball  | Python script to calculate steps to turn a ball on a lathe.                                                                                              |
| shop/bar   | Python script to print out a table of the masses of bar stock in different sizes. You can choose diameters of either inches or mm and get the table in units of kg/m, lbf/ft, or lbm/in. Use the -c option to get conversion factors for other materials. |
| shop/bc    | Contains a python script that will calculate the Cartesian coordinates of holes on a bolt circle.                                                        |
| shop/bucket  | Shows how to calculate bucket volumes and mark volume calibration  marks on nearly any bucket.  It turns out there's a reasonably simple closed formula for this, regardless of the cross-sectional shape of the bucket.  Includes a python script that will do the calculations for you (you'll have to modify the script if the bucket isn't round or square). |
| shop/chain  | Contains a python script and a document to help with chain drilling holes and disks.                                                                     |
| shop/circ3  | Python script that calculates the radius/diameter of a circle that passes through three points. You can specify either the Cartesian coordinates of the points or the distances between the points. If you download the python uncertainties library, the script will calculate the uncertainty in the radius/diameter given one or more uncertainties for the points or distances. |
| shop/cove  | A python script and documentation that show you how to cut a cove with your table saw.  Use this formula and method when it just has to be done correctly on a workpiece you can't mess up on. |
| shop/cut   | Contains a python script that will calculate a solution to the one-dimensional cutting problem.  This problem appears when you have a set of raw materials and need to cut a stated set of workpieces from the stock.  The algorithm used is one called first fit decreasing, which means to sort the stock and pieces to be cut by size, then select the largest piece and cut it from the smallest piece of stock. |
| shop/density  | Python script to calculate densities of various materials. The script performs the following tasks - look up the density of a particular material, find materials that have a density close to a given value, express density information in desired units, and show results relative to a given density. |
| shop/frustum  | Shows how to lay out the frustum of a cone with dividers in your shop.                                                                                   |
| shop/gblock  | A C++ program to print out combinations of gauge blocks that yield a desired composite length (the subset sum problem). Should work with most any set of gauge blocks. Uses brute-force searching to find solutions -- it's not elegant, but it works.  A python script is also included that does the same task and it will probably be fast enough for most folks' needs.  The C++ code runs about an order of magnitude faster than the python code. |
| shop/holes  | Contains a python script that will help you lay out holes that are equally-spaced around a circle.                                                       |
| shop/hose  | Here's an effective way to secure a hose to a hose fitting. It's better than anything you can buy in a store.                                            |
| shop/mass  | Contains a python script that will calculate the volume and mass of a project constructed from various primitive geometrical objects.  This lets you e.g. evaluate the mass and volume of a prospective design and document it through the datafile describing it. |
| shop/pipes  | A document showing a derivation of a formula that can be used to make a template for cutting the end of a pipe so that it can be welded to another pipe. |
| shop/refcards  | Contains some reference cards that will print out on 4 by 6 inch cards. I find these handy to keep in my drafting materials box when I'm doing design work at a drafting board. |
| shop/thd   | Prints out various dimensions associated with threads. Calculates the values based on the ASME B1.1-1989 standard document. If you machine threads on a lathe, you may find this program handy. |
| util/app   | Handy application if you like to work at a cygwin command line. Given one or more files, it will cause them to be opened with their registered application. |
| util/bd    | Performs a comparison between binary files; differences are printed in hex dump format. You can print an ASCII picture that represents where the different bytes in the files are in percentage through the file. |
| util/bidict T3 | Creates a dictionary object in python that lets you treat it in  both directions  as a mapping. If bd is a bidict, you perform normal dictionary access as 'bd[key](key.md)', while getting the key that corresponds to a particular value is gotten via 'bd(value)'. I wrote this because an application needed to get both the number of month names (e.g., Feb  to 2 and be able to get the month name associated with a month number). It's an example of a discrete bijective function. |
| util/color  | Python module to provide color printing help to a console window.  It was developed under Windows/cygwin using Windows console calls, but I've moved back to Linux, so it now uses ANSI escape sequences (I no longer have a Windows box to test it on, so I can't claim the latest version works under Windows, but it should be easy to fix if it's broken). |
| util/dedent  | Python script that will remove the common space characters from a set of text lines from files given on the command line or stdin.                       |
| util/ds    | Contains python scripts to help you launch datasheets, manuals, and other documentation files from a command line prompt.  I use this script to lauch manuals and ebooks and it quickly finds the ones I want amongst thousands of files.  For example, to open the PDF manual on my HP 3400 voltmeter, I type the command  'ds 3400'  and I'm presented with three document choices that have the string '3400' in the file name. I choose the number of the file I want to open and it's launched.  If there's only one match, the file is opened in less than a second.  This is **much** faster than using a file system explorer to find a file.  I also describe how I launch various project I'm working on in my cygwin environment on Windows (a UNIX-like working environment). |
| util/ext   | This python script will make a list of the extensions used in file names in the directories given on the command line. It can also recurse into each directory given on the command line. |
| util/fdiff  | Contains python scripts that can identify differences in two directory trees and perform updates as needed to synchronize these two trees.  I wrote these utilities in the late 1990's to help keep my work and home computers synchronized; the challenge was that new files that needed to be kept could be generated on either computer, so blind copying couldn't be used -- the script needs to determine the differences, based on such things as timestamp or file contents.  There are more modern tools such as WinMerge at Sourceforge, kdiff3, meld, etc.  that can do these comparisons, but I still sometimes utilize this python code for checking things with scripts. |
| util/goto  | Contains a sh-type shell function and a python script that let you navigate around to various directories. I've had a number of UNIX users tell me they couldn't live without this tool once they started using it. |
| util/loo   | Python script that will print out the image files in Open Office documents.  Image files that are not at or below the same directory as the document file will be marked '[relative](not.md)'.  Missing files will be marked '[missing](missing.md)'.  It can also be used as a module in other python programs.  Uses a heuristic rather than any deep knowledge about OO files.  It is particularly useful if you link image files into OO files (which I always do). |
| util/lookup  | Package that contains a python script that can help you look up words in a word dictionary. It can also use the information from WordNet to show synonyms, definitions, and types of words (e.g., adjectives, adverbs, nouns, and verbs).  See the words.pdf file for examples of use and what it can do for you. |
| util/mod   | Python script to recursively find files that have changed within a specified time period.  It helps you find that file you know you worked on recently, but can't remember where it was or what its name is. |
| util/pfind  | Python script to find files and directories. Similar to the UNIX find (but not as powerful), but with a somewhat simpler syntax. It can color-code the output to show where things matched. I use this script a lot. |
| util/space  | See where the space is being consumed in a directory tree and where the biggest files are.                                                               |
| util/tlc   | Python script to rename all files in a directory to lower or upper case.                                                                                 |
| util/tree  | Python script to print an ASCII representation of a directory tree.  It can optionally decorate the tree with each directory's size in MBytes.           |
| util/uni   | A handy python script to find Unicode characters.  Example - find  the Unicode symbol for a steaming pile of poo.  Run the script with the regular expression 'poo' as an argument. You'll see the symbol you want has a code point of U+1f4a9. Run the script with '1f4a9' on the command line and the PDF containing the symbol will be opened.  You'll need to download the relevant files from the Unicode website (see the comments for the links). |
| util/us    | Python script to replace all space characters in file names with underscores. Can also do the reverse and act recursively.                               |


## Legacy projects ##

A few non-deprecated projects remain in the Downloads area because
they are relatively large files.  I won't include them in the
repository until I find the need to change them.  I have deleted the
deprecated files.  The projects are:

fountain\_pen\_primer\_12Dec2011.pdf
> Discusses the care and feeding of fountain pens as writing tools.

DinosaurArithmetic\_25Sep2012.zip
> This document discusses doing calculations without using an
> electronic calculator. It also includes a spreadsheet that
> gives the tables that were common in the math books years ago,
> as people don't use this stuff much anymore. I'm not
> advocating that we give up our calculators, but it's useful
> for a technical person to know how to reason quantitatively
> when a calculator isn't handy. This document looks at some of
> the methods for doing this.

diurnal\_variations\_26Jul2012.pdf
> Shows a plot of the light from the sky measured with a cheap
> photodiode. Since inexpensive datalogging equipment can be
> purchased that use e.g. the USB interface, this would be a
> great experiment for school kids and parents to do together.
> Because it's so simple to do, I predict you'll get hooked if
> you try it.

Octopus\_10Jul2012.pdf
> If you own an oscilloscope and like to troubleshoot electrical
> things, you'll probably want to build an Octopus tester. One can
> be built from a 6.3 V RMS filament transformer and a single
> resistor, so there's no significant parts costs.  It's a handy
> troubleshooting tool.  People have been using them since the
> 30's.

BNC\_connector\_power\_15Sep2011.pdf
> Gives some experimental data about using RF coax cables with
> BNC connectors for DC and low-frequency power.

elements\_22Sep2011.zip
> Contains elements.pdf, a document that contains a periodic
> table of the elements, a plot of the vapor pressures of the
> elements, values of physical parameters sorted by value, and
> various physical parameters of the elements plotted as a
> function of atomic number. The raw data are contained in the
> elements.ods Open Office spreadsheet; the zip archive includes
> the python scripts used to generate the plots. If you'd like
> to generate the plots yourself, you can, as the tools are all
> open source or freely available, but be warned that there are
> numerous libraries that you'll need to get. I've wanted a
> document like this for a long time, but I knew that most of
> the work would be in manually typing in all the data from
> various places. I was right... :^)

CartPlatform\_10Aug2012.pdf
> Simple platform for a Harbor Freight garden cart.  I find it quite
> useful as a dirt repository when digging up e.g. sprinklers in the
> yard.

C\_snippets\_Jan2011.zip
> This is a zip file of the C snippets code put together by Bob
> Stout; it is the Jul 1997 edition, although I downloaded it 18 Jan
> 2011 from somewhere. Apparently Bob Stout died in 2008 and the
> snippets domain wasn't picked up by anyone else (the snippets.org
> now belongs to someone, but it isn't related to Stout's snippet
> collection). I thought it would be useful to make sure there was
> another cache of the Snippets collection.  While some of the code
> is only of interest to archeologists investigating primitive DOS
> cultures, there are numerous useful algorithms in there, so it's
> worth your time to take a look, as there are 416 separate C files.
> We all owe a debt of gratitude to Bob Stout for his dedication in
> writing, collecting, and collating all this stuff.

antifreeze\_5Feb2012.pdf
> How to calculate how much antifreeze to add to an existing
> partially-filled radiator to get a desired concentration.  It also
> discusses the refractometer, a tool to measure antifreeze
> concentrations and a lead-acid battery's sulfuric acid specific
> gravity (which tells you the state of charge).

AnalyticGeometry\_5Sep2012.pdf
> Contains formulas relating to analytic geometry in the
> plane and space, trigonometry, and mensuration.

drules\_16Apr2012.pdf
> Contains some drafting rules that I've always wanted. These
> are primarily 6 inch scales both in inch and mm divisions. You
> can print them at full scale and glue them to a chunk of wood
> to make some handy scales.

Concise300\_7Sep2012.pdf
> Discusses the Concise 300, a circular slide rule still in
> production in Japan.  If you've never used a slide rule, you
> may be surprised to find that they can be good tools to help
> you with calculations accurate to roughly one percent.

inductance\_06Dec2010.zip
> Provides an Open Office spreadsheet that can calculate the
> inductance of common electrical structures.  Includes a PDF
> document describing the use and which gives references for the
> formulas used.  There is also a PDF file of the spreadsheet so
> that you can see what it looks like without having Open Office --
> this will help you decide if you want to install Open Office to be
> able to use the spreadsheet.

sine\_sticks\_27Jun2011.pdf
> How to build a simple device from scrap that will measure
> angles in the shop.  Perhaps surprisingly, it can measure with
> resolution as good or better than a Starrett machinist's
> vernier protractor that costs hundreds of dollars.

help\_system\_12Aug2012.zip
> If you use the vim editor, you have a convenient tool for
> accessing textual information. This package contains the tools I
> use to build a help system I've used for the past couple of
> decades; I started building this textual information in the 80s.
> Vim's ability to use "hyperlinks" in its textual help
> files is used to advantage here.  I've used these files on both
> Windows and Linux boxes.

SolarSystemScaleModel\_16Sep2011.pdf
> This document describes a python script that prints out the
> dimensions of a scaled solar system. You can use it to make a
> scale solar system in your yard or on your street. Be warned
> -- things will be smaller and farther apart than you think.
> This would be a good exercise for a parent and a child -- both
> will learn information you can't learn from a book.

nozzle\_6Oct2011.pdf
> Describes a nice hose nozzle you can make if you have a lathe.
> It will work better for cleaning things off than the typical
> store-bought nozzles.

GlendaGuard\_10Aug2011.pdf
> Describes a simple concrete sprinkler guard that my wife
> designed and built. We've used them for over 20 years and they
> work well, are simple to make, and cheap.

PartsStorageMethods\_21Nov2012.pdf
> Describes one way of storing lots of little electronic parts
> and how to find them quickly.

XmasTomatoes\_24Nov2012.pdf
> Using Christmas tree lights to keep tomato plants from
> freezing at night.

PullingFencePosts\_25Jul2012.pdf
> Using a class 2 lever can be a surprisingly effective way to
> pull fence posts out of the ground.

scale\_27Jan2011.zip
> The scale.pdf file contains two sheets of paper with slide
> rule type scales on them. If you duplex print this and keep it
> in a binder, you may find it useful for simple technical
> calculations when an electronic calculator isn't handy. The
> other file explains how to use things.

## Getting the source code repository ##

To download the hobbyutil source code repository, you need Mercurial
installed on your system.  Mercurial is a revision control tool.  It's
easy to install and use.  To install, go to
http://mercurial.selenic.com/ and download the appropriate package.
Your installation goal is to be able to type **hg** at a console command
prompt and have the Mercurial installation respond with its default
help message, which will look something like

```
Mercurial Distributed SCM

basic commands:

 add           add the specified files on the next commit
 annotate      show changeset information by line for each file
    <middle lines deleted>
 summary       summarize working directory state
 update        update working directory (or switch revisions)

use "hg help" for the full list of commands or "hg -v" for details
```

On Windows, this usually means running an installer package.  On
UNIX-type systems, see the right-hand pane of Mercurial's download
page for common system installations.

Once Mercurial is installed, **cd** to a directory where you'd like to
clone the hobbyutil repository and execute the command

```
hg clone https://code.google.com/p/hobbyutil
```

It will take some time to copy the information.  When completed,
you'll have a directory named **hobbyutil** that contains the source
code for the project.

The names of the projects in the left-hand side of the table above
correspond to the directory names in the repository.

You can just use the content as-is or adapt it to your needs.  Note
that the documentation files are supplied in both Open Office source
code and associated PDF files.  Some of the packages use
reStructuredText for documentation and an associated HTML file will be
included.  See the [docutils](http://docutils.sourceforge.net/) project
for tools that can turn the reStructuredText file(s) into other
document forms.