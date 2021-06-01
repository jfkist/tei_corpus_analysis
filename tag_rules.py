#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' FILE: 
    AUTHOR: jan
'''

class VarLenSearchRule:
    
    def __init__(self, rules, name=None):
        self._rules = rules
        self._name = name
    
    def expand(self, n):
        i = 0
        for j in range(len(self._rules)):
            i = j
            if type(self._rules[i]) is VarRule:
                break
        rules = self._rules[:]
        del rules[i]
        for m in range(n):
            rules.insert(i, self._rules[i]._rule)       
        return SearchRule(rules, name=self._name)
    
    def  __str__(self):
        if self._name:
            return self._name
        else:
            return ' + '.join([str(rule) for rule in self._rules])

class VarRule:
    
    def __init__(self, rule):
        self._rule = rule
    
    def __str__(self):
        return '...'

class SameWordRule:
    
    def __init__(self, pos):
        self._pos = pos
    
    def __str__(self):
        return f'SAME({self._pos})'

class SearchRule:
    
    def __init__(self, rules, name=None):
        self._rules = rules
        self._name = name
    
    def __len__(self):
        return len(self._rules)
    
    def match(self, pos_tags):
        return all([ pos_tag[0] == pos_tags[rule._pos][0]
                     if type(rule) is SameWordRule
                     else rule.match(pos_tag)
                     for rule, pos_tag in zip(self._rules, pos_tags) ])
    
    def  __str__(self):
        if self._name:
            return self._name
        else:
            return ' + '.join([str(rule) for rule in self._rules])

class OrRule:
    
    def __init__(self, rules, name=None):
        self._rules = rules
        self._name = name
    
    def match(self, pos_tag):
        re = any([rule.match(pos_tag) for rule in self._rules])
        #if re:
        #    print(f"Succesfully matched {pos_tag} with one in {str(self)}")
        #else:
        #    print(f"Failed to match {pos_tag} with any of {str(self)}")
        return re
        
    def  __str__(self):
        if self._name:
            return self._name
        else:
            return '/'.join([str(rule) for rule in self._rules])

class AndRule:
    
    def __init__(self, rules):
        self._rules = rules
    
    def match(self, pos_tag):
        re = all([rule.match(pos_tag) for rule in self._rules])
        #if re:
        #    print(f"Succesfully matched {pos_tag} with one in {str(self)}")
        #else:
        #    print(f"Failed to match {pos_tag} with any of {str(self)}")
        return re
        
    def __str__(self):
        return f'ALL({"/".join([str(rule) for rule in self._rules])})'

class AnyRule:
    
    def __init__(self):
        pass
    
    def match(self, pos_tag):
        return True
    
    def __str__(self):
        return f'ANY'

class NotRule:
    
    def __init__(self, rule):
        self._rule = rule
    
    def match(self, pos_tag):
        return not self._rule.match(pos_tag)
    
    def __str__(self):
        return f'NOT({str(self._rule)})'

class TagRule:
    
    def __init__(self, tag):
        self._tag = tag
    
    def match(self, pos_tag):
        tag = pos_tag[1]
        re = (tag == self._tag)
        #if re:
        #    print(f"Matched {tag} with {self._tag}")
        return re
    
    def __str__(self):
        return self._tag

class WordRule:
    
    def __init__(self, word):
        self._word = word
    
    def match(self, pos_tag):
        word = pos_tag[0]
        re = (word.lower() == self._word.lower())
        #if re:
        #    print(f"Matched {word} with {self._word}")
        return re
    
    def __str__(self):
        return self._word

def do_search_rule(pos_tags, search_rule):
    
    #print("Attempting match with rule:")
    #print(search_rule)
    if type(search_rule) is VarLenSearchRule:
        return do_var_len_search_rule(pos_tags, search_rule, 3)
    n = len(search_rule)
    matches = []
    for i in range(len(pos_tags)-(n-1)):
        if search_rule.match(pos_tags[i:i+n]):
            matches.append( (i, n) )
    return matches

def do_var_len_search_rule(pos_tags, var_len_search_rule, max_var):
    
    matches = []
    for n in range(max_var):
        search_rule = var_len_search_rule.expand(n+1)
        #print(f"Created rule: {str(search_rule)}")
        matches.extend(do_search_rule(pos_tags, search_rule))
    return matches

def rule_from_words_str(words_str, name=None):
    words = [word for word in words_str.split(', ')]
    return OrRule([WordRule(word) for word in words], name=name)

PublicVerbRule = rule_from_words_str("acknowledge, admit, agree, assert, claim, complain, declare, deny, explain, hint, insist, mention, proclaim, promise, protest, remark, reply, report, say, suggest, swear, write", name='PUB')

PrivateVerbRule = rule_from_words_str("anticipate, assume, believe, conclude, decide, demonstrate, determine, discover, doubt, estimate, fear, feel, find, forget, guess, hear, hope, imagine, imply, indicate, infer, know, learn, mean, notice, prove, realize, recognize, remember, reveal, see, show, suppose, think, understand", name='PRV')

SuasiveVerbRule = rule_from_words_str("agree, arrange, ask, beg, command, decide, demand, grant, insist, instruct, ordain, pledge, pronounce, propose, recommend, request, stipulate, suggest, urge", name='SUA')

SeemAppearRule = rule_from_words_str("seem, appear", name='SEAM/APPEAR')

DoRule = rule_from_words_str("do, does, did, don't, doesn't, didn't, doing, done", name='DO')
HaveRule = rule_from_words_str("have, has, had, having, haven't, hasn't, hadn't", name='HAVE')
BeRule = rule_from_words_str("am, is, are, was, were, being, been, isn't, aren't, wasn't, weren't", name='BE')

TitleRule = rule_from_words_str("mr, ms", name='TITLE')

""" Rules for finding that + verb complement according to Biber

a) and/nor/but/or/also/ALL-P + that + DET/PRO/there/plural noun/proper noun/TITLE
(these are that-clauses in clause initial positions)

ALL-P = all punctuation
CL-P = clausal punctuation

b) PUB/PRV/SUA/SEEM/APPEAR + that + xxx (where xxx is NOT: V/AUX/CL-P/T#/and)
({that-clauses as complements to verbs which are not included in the
above verb classes are not counted - see Quirk et al. 1985:1179ff.)

(c) PUB/PRV/SUA + PREP + xxx + N + that (where xxx is any number of words, but NOT = N)
(This algorithm allows an intervening prepositional phrase between a verb and its complement.)
"""

rule21a = SearchRule([
    OrRule([
        TagRule('CC'),
        TagRule('.'),
        TagRule(':'),
        TagRule(','),
    ]),
    WordRule('that'),
    OrRule([
        TagRule('DT'), #determiner
        TagRule('PDT'), #pre-determiner
        TagRule('WDT'), #wh-determiner
        TagRule('EX'), #existential there
        TagRule('PRP'), #pronoun personal
        TagRule('PRP$'), #pronoun possesive
        TagRule('WP'), #wh-pronoun
        TagRule('WP$'), #wh-pronoun possesive
        TagRule('NN'), #noun common singular or mass
        TagRule('NNS'), #common noun plural
        TagRule('NNP'), #noun proper singular
        TagRule('NNPS'), #noun proper plural
    ])
])

rule21b = SearchRule([
    OrRule([
        PublicVerbRule,
        PrivateVerbRule,
        SuasiveVerbRule,
        SeemAppearRule,        
    ]),
    WordRule('that'),
    NotRule(OrRule([
        OrRule([ #Verbs
            TagRule('VBD'),
            TagRule('VBN'),
            TagRule('VB'),
            TagRule('VBZ'),
            TagRule('VBP'),
            TagRule('VBG')
        ]),
        OrRule([ #Auxiliaries
            TagRule('MD'),
            DoRule,
            HaveRule,
            BeRule
        ]),
        TagRule('.'),
        TagRule(':'),
        WordRule('and')
    ]))
])

rule21c = VarLenSearchRule([
    OrRule([
        PublicVerbRule,
        PrivateVerbRule,
        SuasiveVerbRule     
    ]),
    TagRule('IN'),
    VarRule(
        AndRule([
            AnyRule(),
            NotRule(OrRule([ #Nouns
                TagRule('NN'), #noun common singular or mass
                TagRule('NNS'), #common noun plural
                TagRule('NNP'), #noun proper singular
                TagRule('NNPS'), #noun proper plural
            ]))
        ])
    ),
    OrRule([ #Nouns
        TagRule('NN'), #noun common singular or mass
        TagRule('NNS'), #common noun plural
        TagRule('NNP'), #noun proper singular
        TagRule('NNPS'), #noun proper plural
    ]),
    WordRule('that')
])

"""
FinAdvClauseRule = SearchRule([
    TagRule('IN'),
    AndRule([
        AnyRule(),
        NotRule(TagRule('VBG'))
    ])
])
"""

FinAdvClauseRule = SearchRule([
    OrRule([
        WordRule('if'),
        WordRule('because')
    ])
])

RepetitionRule = VarLenSearchRule([
    AnyRule(),
    VarRule(
        AnyRule()
    ),
    SameWordRule(0)
])

smrule1 = SearchRule([
    OrRule([
        WordRule('gonna'),
        WordRule('hafta'),
        WordRule('gotta'),
        WordRule('oughta'),
    ]),
])

smrule2 = SearchRule([
    OrRule([
        WordRule('got'),
        WordRule('going'),
        WordRule('have'),
    ]),
    TagRule('TO')
])

smrule3 = SearchRule([
    WordRule('better'),
    NotRule(OrRule([
        TagRule('IN'),
        TagRule('CC'),
    ]))
])
