#!/usr/bin/python3
# -*- coding:utf-8 -*-
import re


def _sub_spes(w):
    w = re.sub(r'\\', r'\\textbackslash ', w)
    w = re.sub(r'(?=[\$%#\{\}])', r'\\', w)
    w = re.sub(r'_', r'\\_{}', w)
    w = re.sub(r'\^', r'\\^{}', w)
    w = re.sub(r'~', r'\\~{}', w)
    return w

def _sub_spes_list(l):
    res = []
    for w in l:
        if w is not None:
            w = _sub_spes(w)
        res.append(w)
    return res

class Tikz:
    def __init__(self, theme='simple'):
        self.buffer = r''
        self.theme = theme

    def to_buffer(self, string):
        self.buffer += string + '\n'

    def reset_buffer(self):
        self.buffer = r''

    def write(self, filename):
        with open(filename, "w") as f:
            f.write(self.buffer)
        self.reset_buffer()

    def add_trees(self, trees):
        for tree in trees:
            self.process_tree(tree)

    def add_tree(self, tree):
        self.process_tree(tree)

    def begin_doc(self):
        self.reset_buffer()
        self.to_buffer(r'\documentclass[multi=dependency]{standalone}')
        self.to_buffer(r'\usepackage[usenames,dvipsnames]{xcolor}')
        self.to_buffer(r'\usepackage[T1]{fontenc}')
        self.to_buffer(r'\usepackage[utf8]{inputenc}')
        self.to_buffer(r'\usepackage{tikz-dependency}')
        self.to_buffer(r'\begin{document}')

    def end_doc(self):
        self.to_buffer(r'\end{document}')

    def process_tree(self, tree):
        #  automatically adding offsets when a pos has too many in/out arcs
        self.to_buffer(r'\begin{dependency}[theme=%s]' % self.theme)

        self.to_buffer(r'\begin{deptext}' + '\n')
        self.to_buffer(r' \& '.join(map(str, tree.tokens)) + r' \\')
        self.to_buffer(r' \& '.join(map(str, tree.tags)) + r' \\')
        self.to_buffer(r'\end{deptext}')

        for dep in tree.deps:
            color = r''
            if dep.color is not None:
                color = r'[edge style={%s}, label style={text=%s}]' % (dep.color, dep.color)
            if dep.gov is None:
                self.to_buffer(r'\deproot%s{%d}{root}' % (color, dep.dep))
            else:
                self.to_buffer(r'\depedge%s{%d}{%d}{%s}' % (color, dep.gov, dep.dep, _sub_spes(dep.rel + (dep.rel_prev if dep.rel_prev is not None else ''))))

        for sdp in tree.sdps:
            color = r''
            if sdp.color is not None:
                color = r', edge style={%s}, label style={text=%s}' % (sdp.color, sdp.color)
            if sdp.gov is None:
                self.to_buffer(r'\deproot%s{%d}{toppred}' % (r'[edge below%s]' % color, sdp.dep))
            else:
                self.to_buffer(r'\depedge%s{%d}{%d}{%s}' % (r'[edge below%s]' % color, sdp.gov, sdp.dep, _sub_spes(sdp.rel + (sdp.rel_prev if sdp.rel_prev is not None else ''))))

        self.to_buffer(r'\end{dependency}')
        self.to_buffer('')  # empty line marks a new paragraph in LaTeX, but multi=dependency causes newpage
