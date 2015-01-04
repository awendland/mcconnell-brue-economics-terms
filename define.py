#!/usr/bin/env python

import difflib

class FuzzyDict(dict):
    "Provides a dictionary that performs fuzzy lookup"
    def __init__(self, items = None, cutoff = .6):
        """Construct a new FuzzyDict instance

        items is an dictionary to copy items from (optional)
        cutoff is the match ratio below which mathes should not be considered
        cutoff needs to be a float between 0 and 1 (where zero is no match
        and 1 is a perfect match)"""
        super(FuzzyDict, self).__init__()

        if items:
            self.update(items)
        self.cutoff =  cutoff

        # short wrapper around some super (dict) methods
        self._dict_contains = lambda key: \
            super(FuzzyDict,self).__contains__(key)

        self._dict_getitem = lambda key: \
            super(FuzzyDict,self).__getitem__(key)

    def _search(self, lookfor, stop_on_first = False):
        """Returns the value whose key best matches lookfor

        if stop_on_first is True then the method returns as soon
        as it finds the first item
        """

        # if the item is in the dictionary then just return it
        if self._dict_contains(lookfor):
            return True, lookfor, self._dict_getitem(lookfor), 1

        # set up the fuzzy matching tool
        ratio_calc = difflib.SequenceMatcher()
        ratio_calc.set_seq1(lookfor)

        # test each key in the dictionary
        best_ratio = 0
        best_match = None
        best_key = None
        for key in self:

            # if the current key is not a string
            # then we just skip it
            try:
                # set up the SequenceMatcher with other text
                ratio_calc.set_seq2(key)
            except TypeError:
                continue

            # we get an error here if the item to look for is not a
            # string - if it cannot be fuzzy matched and we are here
            # this it is definitely not in the dictionary
            try:
            # calculate the match value
                ratio = ratio_calc.ratio()
            except TypeError:
                break

            # if this is the best ratio so far - save it and the value
            if ratio > best_ratio:
                best_ratio = ratio
                best_key = key
                best_match = self._dict_getitem(key)

            if stop_on_first and ratio >= self.cutoff:
                break

        return (
            best_ratio >= self.cutoff,
            best_key,
            best_match,
            best_ratio)


    def __contains__(self, item):
        "Overides Dictionary __contains__ to use fuzzy matching"
        if self._search(item, True)[0]:
            return True
        else:
            return False

    def __getitem__(self, lookfor):
        "Overides Dictionary __getitem__ to use fuzzy matching"
        matched, key, item, ratio = self._search(lookfor)

        if not matched:
            raise KeyError(
                "'%s'. closest match: '%s' with ratio %.3f"%
                    (str(lookfor), str(key), ratio))

        return item

### Start Econ Code
import json
with open('econ_terms_data.json') as data_file:    
    data = json.load(data_file)

terms = FuzzyDict(data)

class colors:
    BG_WHITE = '\033[47m'
    BG_YELLOW = '\033[43m'
    PURPLE = '\033[35m'
    RED = '\033[31m'
    BLACK = '\033[30m'
    BLINK = '\033[5m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def main(args):
    import re
    for term in args:
        if len(term) > 0:
            print("")
            result = terms._search(term)
            match = result[1]
            definition = result[2]
            score = result[3]
            message = colors.BG_WHITE + colors.BLACK + term + colors.END
            if (score < .97):
                message += " -> " + colors.BG_YELLOW + colors.BLACK + match + colors.END
            message += ": " + re.sub(r'_(.+?)_', '\\033[4m\g<1>\\033[0m', definition)
            print(message)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print("Here's a demo of running " + colors.RED + "define.py \"aggregate demand\"" + colors.END + " in the terminal")
        main(['aggregate demand'])
        print("")
        print("You can also use " + colors.RED + "define.py FILE_NAME.txt OPTIONAL_DELIMITER=\"\\n\"" + colors.END + " to load a file")
    else:
        if ".txt" in sys.argv[1]:
            sep = "\n"
            if len(sys.argv) > 2:
                sep = sys.argv[2]
            with open(sys.argv[1]) as chapter_file:    
                chapter = chapter_file.read().split(sep)
            main(chapter)
        else:
            main(sys.argv[1:])
else:
    main(['aggregate demand'])