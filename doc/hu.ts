.sub("$URL", "https://code.google.com/p/hobbyutil")
.(
    m = 60
    level1 = "="*m
    level2 = "-"*m
    level3 = "+"*m
    level4 = "^"*m
.)

hobbyutil 
{level1}

Introduction
{level2}

    This Mercurial repository is associated with the Google code
    project at `hobbyutil <$URL>`_ .  
    This project is a container for some of the things I've developed
    or gotten interested in over the years, usually as a result of a
    hobby.  

    The organization of the repository is centered around "projects".
    A project is a subdirectory of the top-level directory of the
    repository (the first-level subdirectory is a category).  For
    example, the ``eng/pqs`` project contains the following files::

        ProcessSimulator.odt
        ProcessSimulator.pdf
        manufacture.py
        pqs.py
        sig.py

    This project contains an Open Office (OO) document
    ``ProcessSimulator.odt`` that describes some python scripts that
    can estimate the output of a continuous stochastic process that is
    inspected by a measurement tool with significant measurement
    uncertainty (it uses a Monte Carlo simulation).  The
    ``ProcessSimulator.pdf`` file is the PDF form of the Open Office
    document and the ``*.py`` files are the python scripts.

    Other projects will have other types of files.  If a project isn't
    simply a document file or a script, I try to include a ``0readme``
    file to explain the project's purpose and structure.  Most of the
    time I'll use a ``makefile`` to build things when construction is
    needed; an occasional shell script might be in there instead.

    A number of the projects utilize python library modules that are
    in other projects.  These are maintained in the repository as
    softlinks.  I no longer have access to a Windows machine, so I
    don't know how this repository will behave on a Windows machine
    (i.e., I don't know if a UNIX softlink gets made into something
    similar under Windows).  If you try to run a python script in a
    project and get an import error, see if you can find the missing
    module in one of the other directories; make a soft link if you
    can or hard link if you can't (or just copy the needed file into
    the directory that needs it).

    If you find something broken or unclear, please submit an issue at
    https://code.google.com/p/hobbyutil/issues/list on the project's site.

Top level structure 
{level2}

    The files in the repository's root directory are:

    - ``0readme`` Text file describing hobbyutil.  Note it's also a
      restructured text file that ``0readme.html`` is made from.
    - ``0readme.html`` HTML version.
    - ``hu.py`` This python script was initially used to construct the
      hobbyutil repository by copying the files from their various
      locations on my computer.  It now serves as a kind of makefile
      to tell me when the "source" files (the files in the primary
      locations on my computer) have changed compared to the
      hobbyutil's copies.  

    The ``doc`` directory contains the files used to construct
    ``0readme`` and ``0readme.html``.  The remaining directories are
    project directories.

Policies
{level2}

* Python code:  version 3.4 is the working target.  A major goal is to
  also have the code work in version 2.7.  
* Code and documents are licensed under the OSL3 license.
* Stuff whose files are rather large (e.g. because of PDFs with a
  number of bitmaps) have been left in the Downloads area of
  http://code.google.com/p/hobbyutil.  Stuff that didn't seem too
  popular hasn't been included in the repository.  
* All PDF documents now include the Open Office source file that was
  used to construct that document.

If you used an old version of something that is no longer available in
the repository or on the Downloads page at
http://code.google.com/p/hobbyutil, you can send me an email and I
will either have it in my archives or can recover it easily from my
system.

If you find a bug or issue, I recommend you send me an email.  I
rarely check the Issues tab on the project's page.

Projects
{level2}

.inc("hu.list")

History 
{level2}

    In the late 1990's, I had a small business selling software to a
    group of health care businesses that helped them with their
    billing.  I had a website for the business.  On the side, I put
    some stuff that I had generated from my hobbies on the site for
    like-minded individuals.  The website was provided for free by a
    friend.

    A few years later, the friend sold his business and I had to start
    paying for the website.  I eventually reached the conclusion that
    it wasn't worth the money to continue to maintain the website
    because my wife and I were only using it for email (the business
    had gone defunct a few years after starting it).  I moved the
    files to Google code as the hobbyutil project in December of 2009.   

    In June of 2014 I finally abandoned my crashed and trashed Windows
    system [#]_ and went back to using Linux.  I concurrently decided
    that hobbyutil would use a Mercurial repository for its files
    rather than the Downloads page (which is messy to maintain and
    Google no longer allows making changes to it).  It required a
    significant amount of work to organize and move things to the new
    hobbyutil repository structure, but it made everything simpler to
    maintain.  The actual source files are scattered all over my
    computer and much of the work was reorganizing my other project
    directories and getting document's linked images in the proper
    location (this resulted in the util/loo project.  The ``hu.py``
    script is the tool I use to relate my computer's file system with
    the contents of the hobbyutil repository.  You'll see around 150
    projects given in that script, but I've culled out the ones that
    had few downloads or didn't seem like people would be interested
    in them.  If you think you might want one of the non-published
    projects, let me know by email and I can send you the relevant
    files.

Motivation
{level2}

    It requires a fair bit of work to generate, maintain, and package
    these files.  What's the motivation to do this?  

    Most of my motivation comes from wanting to give back to the open
    source community because of some key open source software projects
    I've used:

    * vim
    * python
    * GNU compiler toolchain, bash, and UNIX-type utilities
    * cygwin
    * Open Office

    I've spent many thousands of hours using those tools over the decades
    and I'm grateful for the power they've provided me.  Putting the
    hobbyutil information on the web is a small way of giving back to the
    open source community.

    Some other motivations are:

    * The enjoyment of understanding something (or *thinking* that you
      understand it <smile>) and wanting to show someone else that
      it's actually pretty simple.  Of course, the term "simple" is
      relative: like the mathematician who tells another that
      something is "trivial" and when the other person asks how so,
      the first mathematician explains the details for 45 minutes,
      after which the second mathematician says, "Oh, I see now, it is
      trivial".  
    * I'm a practical person and value practical tips and techniques.
      I enjoy passing on things I've learned or discovered during this
      journey we call life.
    * Sometimes something just impresses me with its elegance and
      brilliance -- the derivation of the force on a particle in a
      spherical shell for an inverse square law force and Henry
      Cavendish's brilliant experiments are an example (see the
      science/sphshell project).
    * I had to teach myself my hobbies.  For example, excluding a
      couple of hours one afternoon with my grandfather, I had to
      teach myself how to machine things when I got his lathe after he
      died.  Because I pursued a professional career, I didn't have
      the time or resources to learn from the pros.  So I
      experimented, read, made lots of mistakes, and occasionally
      discovered a different way to do things.  Such experiences make
      a hobby fun and I like passing those tidbits on in the hopes
      that they'll be of use to others.  For a bunch of tips, see
      Frank Ford's machinist/shop `tips
      <http://frets.com/FretsPages/pagelist.html>`_.

Footnotes
{level2}

.. [#] Windows is an ancient Babylonian term meaning *you'll need to
    reformat your hard disk sooner than you think*.

.(
    import time
    date = time.strftime("%d %b %Y")
.)

Version:  {date}
