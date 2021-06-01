#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' FILE: 
    AUTHOR: jan
'''

import re
import xml.etree.ElementTree as ET
from functools import cached_property

class XmlStr:
    
    def __init__(self, xml_str):
        self._str = re.sub(r"\\'", "'", str(xml_str))
        #self._xml = ET.fromstring(xml_str)
    
    @property
    def inner(self):
        line = self._str.strip()
        return line[line.find('>')+1:line.rfind('<')]
        #opening_tag = line[0:line.find('>')+1]
        #closing_tag = line[:]
    
    def __getattr__(self, name):
        attr_index = self._str.find(f'{name}=')
        if attr_index != -1:
            eq_index = self._str.find('=', attr_index)
            end_index = min(self._str.find(' ', eq_index),self._str.find('>', eq_index))
            return self._str[eq_index+1:end_index]
        else:
            raise AttributeError
    
class TeiUtterance(XmlStr):
    
    def __init__(self, xml_str):
        super().__init__(xml_str)
    
    @cached_property
    def plaintext(self):
        text = self.inner
        #remove any xml <>
        no_xml = re.sub(r'\<.*?\>', '', text)
        #remove any non-punctuation symbols
        no_symbols = re.sub(r'[#]', '', no_xml)
        #remove duplicate spaces
        no_dupl_space = re.sub(r'\ \s+', ' ', no_symbols)
        return no_dupl_space.strip()    
    
    @cached_property
    def words(self):
        return self.plaintext.split(' ')
    
    def wordrange(self, start, stop=None):
        l = len(self.words)
        #negative start, positive stop
        #negative start, negative stop
        tru_start = [start,l+start][start < 0]
        if stop:
            tru_stop  = [stop,l+stop][stop < 0]
        else:
            tru_stop = l
        if tru_stop < tru_start:
            raise IndexError
        i = 0
        for n in range(tru_start):
            i = self.plaintext.find(' ', i) + 1
        j = i
        for m in range(tru_stop - tru_start):
            j = self.plaintext.find(' ', j + 1)
        if j == -1:
            j = None
        return self.plaintext[i:j]
    
class TeiTranscript:
    
    def __init__(self, xmlfile):
        self._file = xmlfile
        try:
            self._xml = ET.parse(xmlfile)
            for el in self._xml.getroot().iter():
                el.tag = el.tag.lower()
                el.attrib = {a.lower():v for a, v in el.attrib.items()}
        except ET.ParseError as err:
            print(f'Unable to parse {xmlfile}')
            print(f'Parsing error at {err.position}')
        
    @property
    def corpus(self):
        return ['MICASE','BASE']['base' in self._file]
    
    @property
    def metadata(self):
        raise NotImplementedError
    
    @cached_property
    def speakers(self):
        if not hasattr(self, '_speakers'):
            root = self._xml.getroot()
            persons = root.findall('.//particdesc/person')
            attribs = [p.attrib for p in persons]
            self._speakers = {a['id']:{key:val for key, val in a.items() if key != 'id'} for a in attribs}
        return self._speakers
    
    @property
    def text(self):
        return self._xml.getroot().find('./text')
    
    @property
    def utterances(self):
        tag = {'BASE':'u','MICASE':'u1'}[self.corpus]
        return [TeiUtterance(ET.tostring(u)) for u in self.text.iter(tag=tag)]
    
    @property
    def plaintext(self):
        return ' '.join([u.plaintext for u in self.utterances])
    
    @property
    def wordcount(self):
        return len(self.plaintext.split(' '))

    @property
    def faculty(self):
        if 'base' in self._file:
            return self._file.split('/')[-2]

def main():
    pass
    
if __name__=='__main__':
    main()
