A Python interface to the Penn Discourse Treebank 2
=========================

## Overview

The [Penn Discourse Treebank 2.0](http://www.seas.upenn.edu/~pdtb/)
(PDTB) is an incredibly rich resource for studying not only the way
discourse coherence is expressed but also how information about
discourse commitments (content attribution) is conveyed
linguistically. However, the file format and annotation methods of the
standard distribution can be an obstacle to research with this
resource. The goal of this code is to remove those obstacles.

This project was originally part of my LSA Linguistic Institute 2011
course [Computational Pragmatics](http://compprag.christopherpotts.net/index.html). 
For much more information on the PDTB, see [this page](http://compprag.christopherpotts.net/pdtb.html).


## Files

* `pdtb2.csv.zip`: Reformatted and repackaged corpus. This link is
  password protected. I will give out the password to people who have
  the requisite LDC license. Unzip the file to use it.
* `pdtb2.py`: Python classes for working with the corpus in the
  `pdtb2.csv` format.
* `pdtb2_functions.py`: illustrations of `pdtb.py` in use.
* `pdtb-template.dot`: template for Graphviz output of `Datum` objects.

The code in this repository is compatible with Python 2 and Python 3.
Its only other external dependency is [NLTK](http://www.nltk.org/install.html), 
with [the data installed](http://www.nltk.org/data.html)
so that WordNet is available.


## `CorpusReader` objects

The main interface provided by pdtb.py is the `CorpusReader`.

```python
from pdtb2 import CorpusReader

corpus = CorpusReader('pdtb2.csv')
```

The central method for `CorpusReader` objects is `iter_data` which
allows you to iterate through the data in the corpus. Intuitively,
`iter_data` reads each row of the source csv file `pdtb2.csv` and
turns it into a `Datum` object, which has lots of methods and
attributes for doing cool things. See `pdtb_functions.relation_count`
for a simple illustration (counting `datum.Relation` instances). There
are 40,600 `Datum` objects in the corpus.


## `Datum` objects

Datum objects have huge numbers of attributes and methods. For lots of
details, see
[here](http://compprag.christopherpotts.net/pdtb.html#structure).
Here's a simple example of working with text and trees (with row 17
chosen because it's a manageable but illustrative case):

```python
from pdtb2 import CorpusReader, Datum

iterator = CorpusReader('pdtb2.csv').iter_data(display_progress=False)
for _ in range(17): next(iterator)

d = next(iterator)

d.arg1_words()
['that', '*T*-1', 'hung', 'over', 'parts', 'of', 'the', 'factory', ',']

d.arg1_words(lemmatize=True)
['that', '*T*-1', 'hang', 'over', 'part', 'of', 'the', 'factory', ',']

d.arg1_pos(wn_format=True)
[('that', 'wdt'), ('*T*-1', '-none-'), ('hung', 'v'), ('over', 'in'), \
('parts', 'n'), ('of', 'in'), ('the', 'dt'), ('factory', 'n'), (',', ',')]

d.arg1_pos(lemmatize=True)
[('that', 'wdt'), ('*T*-1', '-none-'), ('hang', 'v'), ('over', 'in'), \
('part', 'n'), ('of', 'in'), ('the', 'dt'), ('factory', 'n'), (',', ',')]

len(d.Arg1_Trees)
5

for t in d.Arg1_Trees:
	t.pprint()
	
(WHNP-1 (WDT that))
(NP-SBJ (-NONE- *T*-1))
(VBD hung)
(PP-LOC
  (IN over)
  (NP (NP (NNS parts)) (PP (IN of) (NP (DT the) (NN factory)))))
(, ,)
```

There are similarly named methods for Sups, connectives, and attributions.

The `SpanList` and `GornList` attributes are for connecting with the
Penn Treebank files. The relevant material is already inserted into
the CSV file and accessible via the `_RawText` and `_Trees`
attributes, so you probably won't need it, but it is there just in
case you need to connect with the external files.

## For more

There's a much fuller overview here: 
[http://compprag.christopherpotts.net/swda.html](http://compprag.christopherpotts.net/swda.html)
