'''
A minimal implementation of an ordered dictionary

The basic behavior is the order that items are entered into the
dictionary is remembered.  I only needed to recover that order on
iteration over the dictionary's keys.  Most of the rest of the odict's
behavior reflects ordinary dictionary behavior.  In particular, an
odict and regular dict will compare equal if they have the same
key/value pairs, regardless of the order they were entered.

The odict can be initialized via: 
    __init__(self, *vars, **kw)
        Zero vars:
            * Empty object
        One var:
            * Existing dictionary or odict
            * Sequence with (key, value) pairs
            * Sequence with key elements only (values set to None)
        Two vars:
            * Two sequences of (key, value) pairs
        Arbitrary number of keyword arguments in kw dictionary
            * dict(one=2, two=3), which is an allowed python form
              using keyword arguments.

Warning:
    If you iterate over the dictionary as is usual, you'll get the
    keys in the typical hashed order of a regular dictionary:
        for i in my_odict:
            print(i)
    will, in general, not give you the keys in the order you entered
    them.  Instead, use:
        for i in my_odict.keys():
            print(i)

References
----------

[1] You can find another odict implementation at
    http://www.voidspace.org.uk/python/odict.html.  You'll also find
    others if you do a web search on "python odict".

[2] Python 2.7 and later includes an OrderedDict object in the
    collections module; I'd suggest you use that if possible.
'''

# Copyright (C) 2012 Don Peterson
# Contact:  gmail.com@someonesdad1

#
#

from collections import Iterable

class odict(dict):
    def __init__(self, *vars, **kw):
        '''Initialize the dictionary.  The allowable forms are:
        Zero vars:
            * Empty object
        One var:
            * Existing dictionary
            * Sequence with (key, value) pairs
            * Sequence with key elements only (values set to None)
            * Existing odict
        Two vars:
            * Two sequences of (key, value) pairs
        Arbitrary number of keyword arguments
            * dict(one=2, two=3), which is an allowed python form.
        '''
        self._seq = []  # Keeps track of key entry order
        if not vars:
            if not kw:
                return
            else:
                dict.update(self, kw)
        else:
            if len(vars) == 1:
                item = vars[0]
                if isinstance(item, (dict, odict)):
                    for key in item:
                        self[key] = item[key]
                elif self._is_iterable(item):
                    for i in item:
                        if self._is_iterable(i):
                            # See if we can get two objects from it
                            item0 = i[0]
                            try:
                                item1 = i[1]
                            except IndexError:
                                # There's only one object
                                self[item0] = None
                            else:
                                # There's at least two objects
                                self[item0] = item1
                        else:
                            self[i] = None
                else:
                    raise ValueError("Can't initialize from this object")
            elif len(vars) == 2:
                # Must be two sequences of (key, value) pairs
                keys, values = vars
                if not self._is_iterable(keys) or not self._is_iterable(values):
                    raise TypeError("The two arguments must be iterable")
                for key, value in zip(keys, values):
                    self[key] = value
            else:
                raise ValueError("Too many arguments")

    def _is_iterable(self, x):
        '''Return True if x is an iterable.  Strings are excluded.
        '''
        if not isinstance(x, str) and isinstance(x, Iterable):
            return True
        return False

    def clear(self):
        '''Removes all elements.
        '''
        dict.clear(self)
        self._seq = []

    def copy(self):
        '''Returns a copy of the odict.
        '''
        return odict(self)

    def items(self):
        '''Returns a sequence of the key:value pairs.
        '''
        return zip(self._seq, self.values())

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._seq.remove(key)

    def __setitem__(self, key, value):
        if key not in self:
            self._seq.append(key)
        dict.__setitem__(self, key, value)

    def __repr__(self):
        s = "odict{"
        t = []
        for i in self._seq:
            t.append(repr(i) + ": " + repr(self[i]))
        s += ", ".join(t)
        s += "}"
        return s

    def __iter__(self):
        return iter(self._seq)

    iter = __iter__

    def iteritems(self):
        for i in self._seq:
            yield i, self[i]

    def iterkeys(self):
        return iter(self._seq)

    def itervalues(self):
        for i in self._seq:
            yield self[i]

    def keys(self):
        return self._seq[:]

    def pop(self, key, default=None):
        if key not in self:
            if default is None:
                raise KeyError("'%s' is not a key" % key)
            else:
                return default
        else:
            value = self[key]
            del self[key]
            return value

    def popitem(self):
        if self._seq:
            key = self._seq[-1]
            value = self[key]
            dict.__delitem__(self, key)
            del self._seq[-1]
            return key, value
        else:
            raise KeyError("Empty dictionary")

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        else:
            self[key] = default
            return default

    def update(self, *vars, **kw):
        '''Allowed forms:
        * A dict object
        * An odict object
        * kw args
        '''
        if vars:
            if len(vars) != 1:
                raise ValueError("Only one dict/odict allowed")
            other = vars[0]
            if isinstance(other, (dict, odict)):
                # Update from another dict
                for i in other:
                    self[i] = other[i]
            elif self._is_iterable(other):
                # Update from key:value pairs
                for item in other:
                    try:
                        key = item[0]
                        value = item[1]
                    except IndexError:
                        msg = "Elements must be sequences with >= 2 elements"
                        raise IndexError(msg)
                    self[key] = value
            else:
                raise TypeError("Unallowed type for update()")
        else:
            # Update from keyword dict
            self.update(kw)

    def values(self):
        return [self[i] for i in self._seq]

