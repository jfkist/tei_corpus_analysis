#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' FILE: 
    AUTHOR: jan
'''

import os
import re
import nltk
from tei import TeiTranscript
from tag_rules import *
from collections import Counter

def word_tokens(text):
    return [token for token in nltk.word_tokenize(text) if re.match(r'[\w]+', token)]

def split_sents(text):
    return [sent if not sent.endswith('.') else sent[:-1]
            for sent in re.split('(?<=\w)\.\s', text)]

def pos_tag(text, tagset='universal'):
    sents = split_sents(text)
    tagged_sents = [nltk.pos_tag(nltk.word_tokenize(sent),tagset=tagset) for sent in sents]
    reee = []
    for sent in tagged_sents:
        reee.extend(sent)
        reee.extend(nltk.pos_tag(['.'],tagset=tagset))
    return reee

def do_pos_tagging(transcripts):
    pos_tags = [pos_tag(ts.plaintext, tagset=None) for ts in transcripts]
    tags = Counter()
    for ts_tags in pos_tags:
        tags.update([tpl[1] for tpl in ts_tags])
    norm = 1000 / sum(tags.values())
    freqs = {tag: round(freq * norm, 2) for tag, freq in tags.items()}
    if True:
        for tag in freqs.keys():
            if tag:
                print(tag, freqs[tag])
                nltk.help.upenn_tagset(tag)
    print(freqs)
    print(sum([val for key, val in freqs.items()]))

def get_search_context(pos_tags, i, n, head=0, tail=0):
    
    """
    j = i
    for n in range(words):
        j = plaintext.find(' ', j + 1)
    if j == -1:
        j = None
    return plaintext[i:j]
    """
    j = i + n
    if i - head >= 0:
        i -= head
    if j + tail < len(pos_tags):
        j += tail
    n = j - i
    words = [ pos_tag[0].upper() if ((head+tail > 0) and (head <= k < n-tail))
              else pos_tag[0] for pos_tag, k in zip(pos_tags[i:j], range(n)) ]
    return ' '.join(words)

def find_feature_context(pos_tags, rules, head=0, tail=0):
    """ Takes pos tags from a single text as input
        Useful for further analysis """
    matches = []
    for rule in rules:
        matches.extend(do_search_rule(pos_tags, rule))
    context = [ get_search_context(pos_tags, match[0], match[1], head, tail)
                for match in matches ]
    return context

def find_feature_count(pos_tags, rules, normal=1000):
    w = 0
    matches = []
    for tags in pos_tags:
        w += len(tags)
        for rule in rules:
            matches.extend(do_search_rule(tags, rule))
    return len(matches) / (w/normal)

def find_tag_counts(pos_tags, normal=1000):
    c = Counter()
    w = 0
    for tags in pos_tags:
        w += len(tags)
        c.update([tag[1] for tag in tags])
    return {key:val/(w/normal) for key, val in c.items()}

def find_minimal_reponses(transcripts):
    for ts in transcripts:
        u = ts.utterances
        for i in range(len(u) - 1):
            u1, u2 = u[i], u[i + 1]
            if u1.who != u2.who:
                print("response found!")
                print(f"{u1.who}: {u1.wordrange(-5)}\
                      \n{u2.who}: {u2.wordrange(0, 5)}")

def main():
    
    transcripts = []
    for root, dirs, files in os.walk('/home/jan/Documents/school/la6/project/base'):
            for file in [os.path.join(root, file) for file in files if file.endswith('xml')]:
                transcripts.append(TeiTranscript(file))
    transcripts = [ts for ts in transcripts if hasattr(ts, '_xml')]

    """
    pos_tags = [pos_tag(ts.plaintext, tagset=None) for ts in transcripts]

    #counts = find_counts(pos_tags)
    #print(', '.join([f'{key}: {val:.2f}' for key, val in counts.items()]))

    # MAKE SURE TO SET TAGSET TO NONE SO ITLL USE UPENN!

    count_0 = find_feature_count(pos_tags, [smrule1, smrule2, smrule3])
    print(f'Semi-modals: {count_0:.2f} per 1000 words')

    count_1 = find_feature_count(pos_tags, [rule21a, rule21b, rule21c])
    print(f'Verb + that clauses: {count_1:.2f} per 1000 words')

    count_2 = find_feature_count(pos_tags, [FinAdvClauseRule])
    print(f'Finite adverbial clauses: {count_2:.2f} per 1000 words')

    count_3 = find_feature_count(pos_tags, [RepetitionRule])
    print(f'Repetitions: {count_3:.2f} per 1000 words')
    """

def showcase():

    transcripts = []
    for root, dirs, files in os.walk('/home/jan/Documents/school/la6/project/base'):
        for file in [os.path.join(root, file) for file in files if file.endswith('xml')]:
            transcripts.append(TeiTranscript(file))
    transcripts = [ts for ts in transcripts if hasattr(ts, '_xml')]

    hum_tss = [ts for ts in transcripts if ts.faculty == 'ah']
    sci_tss = [ts for ts in transcripts if ts.faculty == 'ps']
    law_tss = [ts for ts in transcripts if ts.faculty == 'ls']

    from random import choice

    todo_tss = []

    todo_tss.extend([ts for ts in transcripts if ts._file == '/home/jan/Documents/school/la6/project/base/baseah_xml/ah/ahlct030.xml'])
    todo_tss.extend([ts for ts in transcripts if ts._file == '/home/jan/Documents/school/la6/project/base/baseps_xml/ps/pslct033.xml'])
    todo_tss.extend([ts for ts in transcripts if ts._file == '/home/jan/Documents/school/la6/project/base/basels_xml/ls/lssem002.xml'])

    """
    for tss in [hum_tss, sci_tss, law_tss]:
        while True:
            ts = choice(tss)
            print(ts._file)
            last_who = None
            for u in ts.utterances:
                if last_who != u.who:
                    print(u.who)
                last_who = u.who
                print(f'    {u.plaintext}')
            wat_do = input("Wat do? ")
            if wat_do == 'next':
                todo_tss.append(ts)
                break
    """

    for ts in todo_tss:
        with open(f'./todo_{ts.faculty}.txt', 'w') as f:
            last_who = None
            for u in ts.utterances:
                if last_who != u.who:
                    f.write(f'{u.who}\n')
                last_who = u.who
                f.write(f'  {u.plaintext}\n')

def test():
    pos_tags = pos_tag("You better get going because mine is better than yours", tagset=None)
    print(pos_tags)

if __name__=='__main__':
    #main()
    #test()
    showcase()
