import csv
import sys

from pattern.en import  lexeme, comparative, superlative, pluralize, parse  # @UnresolvedImport

ngsl = []
additions = []

add_set = []


def add(addition, word, is_word, word_type):
    if is_word or addition != word and addition not in ngsl and addition not in add_set:
        if len(addition.split(" ")) == 1:
            additions.append((addition, ngsl.index(word) + 1, word_type))
            add_set.append(addition)


def check_pos(pos_tag, word):
    if pos_tag == 'NN':
        add(pluralize(word), word, False, "plural")
    elif pos_tag == 'VB':
        for lex in lexeme(word):
            add(lex, word, False, "conjugation")
    elif pos_tag == 'JJ':
        comp = comparative(word)
        add(comp, word, False, "comparative")
        sup = superlative(word)
        add(sup, word, False, "superlative")


ngsl_file_path = sys.argv[1]
with open(ngsl_file_path, 'r') as csvfile:
    spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
    for row in spamreader:
        ngsl.append(row[0])

pos_tag = parse("to " + "test")

for word in ngsl:
    add(word, word, True, "root")
    if parse("to " + word).split(' ')[1].split('/')[1] == "VB":
        check_pos("VB", word)

    check_pos(parse(word).split('/')[1], word)

for addition in additions:
    print(addition[0] + "\t" + str(addition[1]) + "\t" + str(addition[2]))
