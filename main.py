#!/usr/bin/python3
#, '*- coding:utf-8, '*-

import argparse
from dep2tikz.tikz import Tikz
from dep2tikz.structure import Arc, Tree, ForestStructure

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()
    
    tokens = ['Chase', 'Manhattan', ',', 'which', 'sold', '14', 'million', 'additional', 'shares', 'at']

    # init
    tags = ['NNP', None, ',', None, 'VBD', None, 'CD', 'JJ', 'NNS', 'IN']
    deps = [(None, 'root', 2), (6, 'number', 5), (4, 'nsubj', 3), (4, 'prep', 9)]
    sdps = [(None, 'toppred', 2), (7, 'ARG1', 8), (6, 'ARG1', 8), (4, 'ARG2', 8)]
    tree_1 = Tree(tokens, tags, [Arc(dep[2], dep[0], dep[1]) for dep in deps], [Arc(sdp[2], sdp[0], sdp[1]) for sdp in sdps])

    # del
    tags = ['NNP', None, ',', None, 'VBD', None, 'CD', 'JJ', 'NNS', 'IN']
    deps = [(6, 'number', 5), (4, 'nsubj', 3), (4, 'prep', 9)]
    sdps = [(None, 'toppred', 2), (6, 'ARG1', 8)]
    tree_2 = Tree(tokens, tags, [Arc(dep[2], dep[0], dep[1]) for dep in deps], [Arc(sdp[2], sdp[0], sdp[1]) for sdp in sdps])

    # add
    tags = ['NNP', 'CD', ',', 'CD', 'VBD', 'JJ', 'CD', 'JJ', 'NNS', 'IN']
    deps = [(None, 'root', 2), (6, 'number', 5), (4, 'nsubj', 3), (4, 'prep', 9)]
    sdps = [(None, 'toppred', 2), (7, 'ARG1', 8), (6, 'ARG1', 8), (4, 'ARG2', 8)]
    tree_3 = Tree(tokens, tags, [Arc(dep[2], dep[0], dep[1]) for dep in deps], [Arc(sdp[2], sdp[0], sdp[1]) for sdp in sdps])

    # sub tags
    tags = ['JJ', '.', 'CD', 'CD', 'VBD', 'JJ', 'CD', 'JJ', 'NNS', 'IN']
    deps = [(None, 'root', 2), (6, 'number', 5), (4, 'nsubj', 3), (4, 'prep', 9)]
    sdps = [(None, 'toppred', 2), (7, 'ARG1', 8), (6, 'ARG1', 8), (4, 'ARG2', 8)]
    tree_4 = Tree(tokens, tags, [Arc(dep[2], dep[0], dep[1]) for dep in deps], [Arc(sdp[2], sdp[0], sdp[1]) for sdp in sdps])

    # sub rel
    tags = ['JJ', '.', 'CD', 'CD', 'VBD', 'JJ', 'CD', 'JJ', 'NNS', 'IN']
    deps = [(None, 'root', 2), (6, 'numberEE', 5), (4, 'nsubjEE', 3), (4, 'prep', 9)]
    sdps = [(None, 'toppred', 2), (7, 'ARG1', 8), (6, 'ARG1EE', 8), (4, 'ARG2', 8)]
    tree_5 = Tree(tokens, tags, [Arc(dep[2], dep[0], dep[1]) for dep in deps], [Arc(sdp[2], sdp[0], sdp[1]) for sdp in sdps])
    
    # sub dep
    tags = ['JJ', '.', 'CD', 'CD', 'VBD', 'JJ', 'CD', 'JJ', 'NNS', 'IN']
    deps = [(None, 'root', 9), (6, 'numberEE', 5), (4, 'nsubjEE', 7), (4, 'prep', 2)]
    sdps = [(None, 'toppred', 8), (7, 'ARG1', 8), (6, 'ARG1EE', 8), (4, 'ARG2', 2)]
    tree_6 = Tree(tokens, tags, [Arc(dep[2], dep[0], dep[1]) for dep in deps], [Arc(sdp[2], sdp[0], sdp[1]) for sdp in sdps])
    
    # sub gov
    tags = ['JJ', '.', 'CD', 'CD', 'VBD', 'JJ', 'CD', 'JJ', 'NNS', 'IN']
    deps = [(None, 'root', 9), (1, 'numberEE', 5), (1, 'nsubjEE', 7), (4, 'prep', 2)]
    sdps = [(None, 'toppred', 8), (2, 'ARG1', 8), (1, 'ARG1EE', 8), (4, 'ARG2', 2)]
    tree_7 = Tree(tokens, tags, [Arc(dep[2], dep[0], dep[1]) for dep in deps], [Arc(sdp[2], sdp[0], sdp[1]) for sdp in sdps])

    trees = ForestStructure([tree_1, tree_2, tree_3, tree_4, tree_5, tree_6, tree_7])
    tikz = Tikz(trees, gold=tree_7)
    tikz.write_all(args.output)