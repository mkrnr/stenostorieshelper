import codecs
from collections import OrderedDict
import collections
import csv
import html
import json
from operator import itemgetter
import re
import sys
from urllib.request import urlopen

from stenostorieshelper.simplifier import Simplifier


class Updater(object):
    endings = []
    endings.append(("ing", "G"))
    endings.append(("s", "S"))
    endings.append(("ds", "Z"))
    endings.append(("ed", "D"))
    endings.append(("d", "D"))
    endings.append(("n't", "PBT"))
    endings.append(("n", "PB"))
    endings.append(("er", "R"))
    
    index_dict = {}
    index_dict["word"] = 0
    index_dict["outline"] = 1
    index_dict["sim-outline"] = 2
    index_dict["rank"] = 3
    index_dict["type"] = 4
    index_dict["alt"] = 5
    index_dict["story"] = 6
    index_dict["notes"] = 7
    index_dict["tags"] = 8
    
    # ensure word type order
    word_types = []
    word_types.append("root")
    word_types.append("conjugation")
    word_types.append("plural")
    word_types.append("comparative")
    word_types.append("superlative")
        
    def __init__(self):
        self.number_alt_strokes = 5
        self.prev_root_row = []
        self.tsv_lines = []
        self.simplifier = Simplifier()    
    
    def is_boring(self, row):
        if row[self.index_dict["type"]] == "root":
            return False
        for ending in self.endings:
            same = self.check_plover(row[0], row[1], ending[0], ending[1])
            if same:
                return True
        return False
                
    def check_plover(self, word, word_stroke, word_ending, stroke_ending):
        short_word = re.sub(word_ending + '$', '', word)
        short_stroke = re.sub(stroke_ending + '$', '', word_stroke)
        short_stroke = re.sub('-$', '', short_stroke)
        if len(word) == len(short_word):
            # word ending didn't match
            return False
        if len(self.prev_root_row) == 0:
            return False
        root_short_stroke = re.sub(stroke_ending + '$', '', self.prev_root_row[1])
        root_short_stroke = re.sub('-$', '', root_short_stroke)
        return short_stroke == root_short_stroke
            
    # ['abstract', '1 - NGSL', '2858.00', 'AB/STRABG', '', 'Y', 'AB/STRAK', '', 'This outline ends in TRAK because riding on a train TRAK (track) is a great place to paint abstract art. Everything moves so quickly that your canvas will just look like a blur of blue, brown, and green.', '', '8', '2', '0', '', '', '2718', '53.118', '20.50', '0.6300', '8,383', '2,501', '0.0000']
    
    def update(self, row):
        if len(row[self.index_dict["sim-outline"]]) == 0:
            sim_outline = self.simplifier.simplify_outline(row[self.index_dict["outline"]])
            row[self.index_dict["sim-outline"]] = sim_outline

        if(row[self.index_dict["type"]] == "root"):
            self.prev_root_row = row
        if(self.is_boring(row)):
            # TODO write to separate list
            row[self.index_dict["tags"]] = "old"
            self.boring_words[row[0]] = row
            # row[self.index_dict]="old"
            # self.rope[row[0]]=[]

    def sort_rows(self, word_dict):
        sorted_rows = []
        rank_dict = {}
        for word in word_dict:
            row = word_dict[word]
            if len(row) == 0:
                continue
            rank = int(row[self.index_dict["rank"]])
            if rank not in rank_dict:
                rank_dict[rank] = []
            rank_dict[rank].append(row)
        ordered_rank_dict = collections.OrderedDict(sorted(rank_dict.items()))

        for rank in ordered_rank_dict:
            sorted_rows.extend(self.sort_rows_by_type(ordered_rank_dict[rank]))

        return sorted_rows

    def sort_rows_by_type(self, rows):
        sorted_rows = []
        for word_type in self.word_types:
            type_rows = []
            for row in rows:
                if row[self.index_dict["type"]] == word_type:
                    type_rows.append(row)
            sorted_type_rows = sorted(type_rows, key=itemgetter(self.index_dict["word"]))
            sorted_rows.extend(sorted_type_rows)
        if len(rows) != len(sorted_rows):
            raise ValueError('length of rows different from sorted_rows')
        return sorted_rows
    
    def cleanup_strings(self, rows):
        new_rows = []
        for row in rows:
            new_row = []
            for element in row:
                decoded_element = html.unescape(element)
                decoded_element = decoded_element.replace("<br>", "")
                decoded_element = decoded_element.replace("\xa0", " ")
                new_row.append(decoded_element)
            new_rows.append(new_row)
        return new_rows

    
if __name__ == '__main__':
    updater = Updater()
    
    updated_tsv = sys.argv[1]
    original_tsv = sys.argv[2]
    old_words_tsv = sys.argv[3]
    
    output_tsv = sys.argv[4]
    output_old_words_tsv = sys.argv[5]

    plover_dict = {}
    # always use the latest main.json
    with urlopen('https://raw.githubusercontent.com/openstenoproject/plover/master/plover/assets/main.json') as data_file:    
        strokes = json.load(data_file)
        for stroke in strokes:
            transl = strokes[stroke]
            if transl not in plover_dict:
                plover_dict[transl] = []
            plover_dict[transl].append(stroke)
    
    plover_shortest = {}
    plover_alternatives = {}
    for word in plover_dict:
        sorted_strokes = sorted(plover_dict[word], key=len)
        plover_dict[word] = sorted_strokes
        plover_shortest[word] = sorted_strokes[0]
        if len(sorted_strokes) > 1:
            alternatives = []
            for i in range(1, min(updater.number_alt_strokes + 1, len(sorted_strokes))):
                alternatives.append(sorted_strokes[i])
            plover_alternatives[word] = alternatives
    updater.rope = OrderedDict()
    with open(updated_tsv, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        for row in spamreader:
            updater.rope[row[0]] = row

    with open(original_tsv, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')

        count = 1
        for row in spamreader:
            if row[0] not in updater.rope:
                print("MISSING: " + str(count) + ": " + row[0])
            count += 1

    updater.boring_words = OrderedDict()
    for word in updater.rope:
        updater.update(updater.rope[word])

    for word in updater.boring_words:
        updater.rope.pop(word)

    # read old boring words
    with open(old_words_tsv, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        for row in spamreader:
            updater.boring_words[row[0]] = row
    
    updated_rows = updater.cleanup_strings(updater.sort_rows(updater.rope))
    updated_boring_words = updater.cleanup_strings(updater.sort_rows(updater.boring_words))
    
    with codecs.open(output_tsv, 'w', 'utf-8') as text_file:
        for row in updated_rows:
            if(len(row) > 0):
                text_file.write('\t'.join(row) + '\n')
    
    with codecs.open(output_old_words_tsv, 'w', 'utf-8') as text_file:
        for row in updated_boring_words:
            if(len(row) > 0):
                text_file.write('\t'.join(row) + '\n')
        
