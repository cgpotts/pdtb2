#!/usr/bin/env python

"""
Miscellaneous functions for exploring the Penn Discourse Treebank via
the classes in `pdtb.py`.
"""

__author__ = "Christopher Potts"
__version__ = "2.0"
__license__ = "GNU general public license, version 2"
__maintainer__ = "Christopher Potts"
__email__ = "See the author's website"
		
######################################################################

import csv
from random import shuffle
import re
import pickle
from collections import defaultdict
from operator import itemgetter

from pdtb2 import CorpusReader, Datum

######################################################################
 
def relation_count(corpus_filename='pdtb2.csv'):
    """Calculate and display the distribution of relations."""
    pdtb = CorpusReader(corpus_filename)
    # Create a count dictionary of relations:
    d = defaultdict(int)
    for datum in pdtb.iter_data():
        d[datum.Relation] += 1
    # Print the results to standard output:
    for key, val in d.items():
        print("{} {}".format(key, val))
 
######################################################################

def count_semantic_classes(corpus_filename='pdtb2.csv'):
    """Count ConnHeadSemClass1 values."""
    pdtb = CorpusReader(corpus_filename)
    d = defaultdict(int)
    for datum in pdtb.iter_data():
        sc = datum.ConnHeadSemClass1
        # Filter None values (should be just EntRel/NonRel data):
        if sc:
            d[sc] += 1
    return d

def count_semantic_classes_to_csv(output_filename):
    """Write the results of  count_semantic_classes() to a CSV file."""
    # Create the CSV writer:
    with open(output_filename, 'wt') as f:
        csvwriter = csv.writer(f)
        # Add the header row:
        csvwriter.writerow(['ConnHeadSemClass1', 'Count'])
        # Get the counts:
        d = count_semantic_classes()
        # Sort by name so that we can perhaps see trends in the
        # super-categories:
        for sem, count in sorted(d.items()):
            csvwriter.writerow([sem, count])
 
# count_semantic_classes_to_csv('ConnHeadSemClass1.csv')

######################################################################

def connective_distribution(corpus_filename='pdtb2.csv'):
    """Counts of connectives by relation type."""
    pdtb = CorpusReader(corpus_filename)
    d = defaultdict(lambda : defaultdict(int))
    for datum in pdtb.iter_data():
        cs = datum.conn_str(distinguish_implicit=False)
        # Filter None values (should be just EntRel/NoRel data):
        if cs:
            # Downcase for further collapsing, and add 1:
            d[datum.Relation][cs.lower()] += 1
    return d

def connective_distribution2wordle(d):
    """
    Map the dictionary returned by connective_distribution() to a
    Wordle format. The return value is a string. Its sublists it
    returned can be pasted in at http://www.wordle.net/advanced.
    """
    s = ''
    # Print lists of words with the relation type as the header:
    for rel, counts in list(d.items()):
        s += '======================================================================\n'
        s += rel + '\n'
        s += '======================================================================\n'
        # Map the counts dict to a list of pairs via items() and sort on
        # the second member (index 1) of those pairs, largest to smallest:
        sorted_counts = sorted(list(counts.items()), key=itemgetter(1), reverse=True)
        # Print the result in Wordle format:
        for conn, c in sorted_counts:
            # Spacing is hard to interpret in Wordle. This should help:
            conn = conn.replace(' ', '_')
            # Append to the growing string:
            s += '{}:{}\n'.format(conn, c)
    return s

######################################################################

def attribution_counts(corpus_filename='pdtb2.csv'):
    """Create a count dictionary of non-null attribution values."""
    pdtb = CorpusReader(corpus_filename)
    d = defaultdict(int)
    for datum in pdtb.iter_data():
        src = datum.Attribution_Source
        if src:
            d[src] += 1
    return d

def print_attribution_texts(corpus_filename='pdtb2.csv'):
    """Inspect the strings characterizing attribution values."""
    pdtb = CorpusReader(corpus_filename)
    for datum in pdtb.iter_data(display_progress=False):
        txt = datum.Attribution_RawText
        if txt:
            print(txt)

######################################################################

def adjacency_check(datum):
    """Return True if datum is of the form Arg1 (connective) Arg2, else False"""    
    if not datum.arg1_precedes_arg2():
        return False
    arg1_finish = max([x for span in datum.Arg1_SpanList for x in span])
    arg2_start = min([x for span in datum.Arg2_SpanList for x in span])    
    if datum.Relation == 'Implicit':
        if (arg2_start - arg1_finish) <= 3:
            return True
        else:
            return False
    else:
        conn_indices = [x for span in datum.Connective_SpanList for x in span]
        conn_start = min(conn_indices)
        conn_finish = max(conn_indices)
        if (conn_start - arg1_finish) <= 3 and (arg2_start - conn_finish) <= 3:
            return True
        else:
            return False        

def connective_initial(sem_re, output_filename, corpus_filename='pdtb2.csv'):
    """
    Pull out examples of Explicit or Implicit relations in which

    (i) Arg1 immediately precedes Arg2, with only the connective
        intervening in the case of Explicit.
    (ii) There is no supplementary text on either argument.
    (iii) ConnHeadSemClass1 matches the user-supplied regex sem_re    

    The results go into a CSV file named output_filename.
    """
    keepers = {} # Stores the items that pass muster.
    pdtb = CorpusReader(corpus_filename)
    for datum in pdtb.iter_data(display_progress=False):
        # Restrict to examples that are either Implicit or
        # Explicit and have no supplementary text:
        rel = datum.Relation
        if rel in ('Implicit', 'Explicit') and not datum.Sup1_RawText and not datum.Sup2_RawText:
            # Further restrict to the class of semantic relations captured by sem_re:            
            if sem_re.search(datum.ConnHeadSemClass1):                
                # Make sure that Arg1, the connective, and Arg2 are all adjacent:
                if adjacency_check(datum):
                    # Stick to simple connectives: for Explicit, the connective
                    # and its head are the same;
                    # for Implicit, there is no secondary connective.
                    if (rel == 'Explicit' and datum.ConnHead == datum.Connective_RawText) or \
                       (rel == 'Implicit' and not datum.Conn2):
                        itemId = "%s/%s" % (datum.Section, datum.FileNumber)
                        print(itemId)
                        # We needn't flag them, since column 2 does that.
                        conn = datum.conn_str(distinguish_implicit=False) 
                        # Store in a dict with file number keys to avoid taking two
                        # sentences from the same file:
                        keepers[itemId] = [
                            itemId,
                            rel,
                            datum.ConnHeadSemClass1,
                            datum.Arg1_RawText,
                            conn,
                            datum.Arg2_RawText]
    # Store the results in a CSV file:
    with open(output_filename, 'wt') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow([
            'ItemId',
            'Relation',
            'ConnHeadSemClass1',
            'Arg1',
            'Connective',
            'Arg2'])
        csvwriter.writerows(list(keepers.values()))
    print("CSV created.")
    
# connective_initial(re.compile(r'Expansion'), 'pdtb-continuation-data-expansion.csv')    

######################################################################

def semantic_classes_in_implicit_relations(corpus_filename='pdtb2.csv'):
    """Count the primary semantic classes for connectives
    limited to Implicit relations."""
    d = defaultdict(int)
    pdtb = CorpusReader(corpus_filename)
    for datum in pdtb.iter_data(display_progress=True):
        if datum.Relation == 'Implicit':
            d[datum.primary_semclass1()] += 1
    # Print, sorted by values, largest first:
    for key, val in sorted(list(d.items()), key=itemgetter(1), reverse=True):
        print(key, val)

# semantic_classes_in_implicit_relations()

######################################################################

def random_Implicit_subset(sample_size=30, corpus_filename='pdtb2.csv'):
    """
    Creates a CSV file containing randomly selected Implicit examples
    from each of the primary semantic classes. sample_size determines
    the size of the sample from each class (default: 30). The output
    is a file called pdtb-random-Implicit-subset.csv with columns named
    for the attributes/methods that determined the values.
    """    
    d = defaultdict(list)
    pdtb = CorpusReader(corpus_filename)
    for datum in pdtb.iter_data(display_progress=True):
        if datum.Relation == 'Implicit' and not datum.Sup1_RawText and not datum.Sup2_RawText:
            d[datum.primary_semclass1()].append(datum)
    with open('pdtb-random-Implicit-subset.csv', 'w') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(['Arg1_RawText', 'conn_str', 'Arg2_RawText', 'primary_semclass1'])
        for cls, data, in list(d.items()):
            shuffle(data)
            for datum in data[: sample_size]:
                row = [datum.Arg1_RawText, datum.conn_str(), datum.Arg2_RawText, cls]
                csvwriter.writerow(row)

######################################################################

def distribution_of_relative_arg_order(corpus_filename='pdtb2.csv'):
    d = defaultdict(int)
    pdtb = CorpusReader(corpus_filename)
    for datum in pdtb.iter_data(display_progress=True):
        d[datum.relative_arg_order()] += 1
    for order, count in sorted(list(d.items()), key=itemgetter(1), reverse=True):
        print(order, count)
                        
