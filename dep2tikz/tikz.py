#!/usr/bin/python3
# -*- coding:utf-8 -*-

class Tikz:
    def __init__(self, trees, gold=None, paperheight='200cm', paperwidth='50cm', theme='simple'):
        self.trees = trees
        self.gold = gold
        self.buffer = r''
        self.paperheight = paperheight
        self.paperwidth = paperwidth
        self.theme = theme

    def to_buffer(self, string):
        self.buffer += string + '\n'

    def reset_buffer(self):
        self.buffer = r''

    def write_all(self, filename):
        self.reset_buffer()
        self.before_process_document()
        for tree in self.trees:
            self.process_tree(tree)
        if self.gold is not None:
            self.process_tree(self.gold)
        self.after_process_document()
        with open(filename, "w") as f:
            f.write(self.buffer)
        self.reset_buffer()

    def before_process_document(self):
        self.to_buffer(r'\documentclass[multi=dependency]{standalone}')
        self.to_buffer(r'\usepackage[paperheight=%s, paperwidth=%s, top=0cm, bottom=0cm, left=0cm, right=0cm]{geometry}' % (self.paperheight, self.paperwidth))
        self.to_buffer(r'\usepackage[T1]{fontenc}')
        self.to_buffer(r'\usepackage[utf8]{inputenc}')
        self.to_buffer(r'\usepackage{tikz-dependency}')
        self.to_buffer(r'\begin{document}')

    def after_process_document(self):
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
