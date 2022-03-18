#!/usr/bin/python3
#, '*- coding:utf-8, '*-

import argparse
from conllu import parse
from dep2tikz.tikz import Tikz, _sub_spes
from dep2tikz.structure import Tag, Arc, AnnotationSet, AnnotationSetStructure

def compare(pred, gold):
    assert len(pred) == len(gold)
    for i in range(len(pred)):
        assert pred[i]["form"] == gold[i]["form"]

    tokens = []
    tags_pred, tags_gold = [], []
    deps_pred, deps_gold = [], []

    for i in range(len(pred)):
        tokens.append(pred[i]["form"])

        tags_pred.append(Tag(pred[i]["upos"]))
        tags_gold.append(Tag(gold[i]["upos"]))

        if pred[i]["deprel"] == "root" or pred[i]["head"] == 0:
            deps_pred.append(Arc(pred[i]["id"] - 1, None, 'root'))
        else:
            deps_pred.append(Arc(pred[i]["id"] - 1, pred[i]["head"] - 1, pred[i]["deprel"]))

        if gold[i]["deprel"] == "root" or gold[i]["head"] == 0:
            deps_gold.append(Arc(gold[i]["id"] - 1, None, 'root'))
        else:
            deps_gold.append(Arc(gold[i]["id"] - 1, gold[i]["head"] - 1, gold[i]["deprel"]))

    tree_pred = AnnotationSet(0, tokens, tags_pred, deps_pred, None)
    tree_gold = AnnotationSet(0, tokens, tags_gold, deps_gold, None)

    trees = AnnotationSetStructure([tree_pred, tree_gold]).diff()

    return trees

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pred_input", required=True)
    parser.add_argument("-g", "--gold_input", required=True)
    parser.add_argument("-o", "--output_prefix", required=True)
    args = parser.parse_args()

    with open(args.pred_input, "r") as f:
        pred = parse(f.read())
    with open(args.gold_input, "r") as f:
        gold = parse(f.read())

    assert len(pred) == len(gold)
    for i in range(len(pred)):
        assert pred[i].metadata == gold[i].metadata

    for i in range(len(pred)):
        metadata = pred[i].metadata
        trees = compare(pred[i], gold[i])
        tikz = Tikz()
        tikz.begin_doc()
        tikz.to_buffer(r'\section{%s}' % i)
        for key, value in metadata.items():
            tikz.to_buffer(r'%s: %s\\' % (_sub_spes(key), _sub_spes(value)))
        tikz.add_trees(trees)
        tikz.end_doc()
        tikz.write(args.output_prefix + str(i) + ".tex")