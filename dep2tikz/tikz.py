#!/usr/bin/python3
# -*- coding:utf-8 -*-

class Tikz:
    def __init__(self, paperheight='200cm', paperwidth='50cm', theme='simple'):
        self.buffer = r''
        self.paperheight = paperheight
        self.paperwidth = paperwidth
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

    def add_gold(self, gold):
        self.process_tree(gold)

    def begin_doc(self):
        self.reset_buffer()
        self.to_buffer(r'\documentclass[multi=dependency]{article}')
        self.to_buffer(r'\usepackage[paperheight=%s, paperwidth=%s, top=10cm, bottom=5cm, left=10cm, right=5cm]{geometry}' % (self.paperheight, self.paperwidth))
        self.to_buffer(r'\usepackage[T1]{fontenc}')
        self.to_buffer(r'\usepackage[utf8]{inputenc}')
        self.to_buffer(r'\usepackage{tikz-dependency}')
        self.to_buffer(r'\begin{document}')

    def end_doc(self):
        self.to_buffer(r'\end{document}')

    def process_tree(self, tree):
        self.to_buffer(r'\begin{dependency}[theme=%s]' % self.theme)

        self.to_buffer(r'\begin{deptext}[column sep=1em]')
        self.to_buffer(r' \& '.join(tree.tokens) + r' \\')
        self.to_buffer(r' \& '.join(tree.tags.values()) + r' \\')
        self.to_buffer(r'\end{deptext}')

        for dep in tree.deps:
            color = r''
            if dep.color is not None:
                color = r'[edge style={%s}, label style={text=%s}]' % (dep.color, dep.color)
            if dep.gov is None:
                self.to_buffer(r'\deproot%s{%d}{root}' % (color, dep.dep))
            else:
                self.to_buffer(r'\depedge%s{%d}{%d}{%s}' % (color, dep.gov, dep.dep, dep.rel))

        for sdp in tree.sdps:
            color = r''
            if sdp.color is not None:
                color = r', edge style={%s}, label style={text=%s}' % (sdp.color, sdp.color)
            if sdp.gov is None:
                self.to_buffer(r'\deproot%s{%d}{toppred}' % (r'[edge below%s]' % color, sdp.dep))
            else:
                self.to_buffer(r'\depedge%s{%d}{%d}{%s}' % (r'[edge below%s]' % color, sdp.gov, sdp.dep, sdp.rel))

        self.to_buffer(r'\end{dependency}')
        self.to_buffer('')  # empty line marks a new paragraph in LaTeX, but multi=dependency causes newpage
