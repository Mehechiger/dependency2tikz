#!/usr/bin/python3
# -*- coding:utf-8 -*-

import os
import re
from tqdm import tqdm
from collections import defaultdict
import argparse
import json
import pandas as pd
from dep2tikz.tikz import Tikz
from dep2tikz.structure import Token, Tag, Arc, AnnotationSet, AnnotationSetStructure

def run(filename, output_dir):
    print(filename)
    if os.path.isdir(output_dir):
        print("files exist, skipping")
        return
    else:
        os.mkdir(output_dir)

    eps = json.load(open(filename + ".json", "r"))
    corrections_df = pd.read_csv(filename + ".csv", index_col=0)
    #corrections_df = corrections_df[corrections_df["effect"] == "correction"] # TODO make this script work as well with "first"!

    for ep, trees in tqdm(eps.items()):
        corrections_df_ep = corrections_df[corrections_df["episode"] == int(ep)]
        corrections_df_ep = corrections_df_ep[corrections_df_ep["count_true"] == 1]
        corrections_ep = {}
        for count_action, group in corrections_df_ep.groupby("count_action"):
            corrections_ep[count_action] = defaultdict(lambda: defaultdict(list))
            for key, action_type in [("tags", "tag"), ("deps", "syn"), ("sdps", "sem")]:
                corrections_ep[count_action][key]["prev"] = [tuple(map(lambda x: x if x != -1 else None, x)) for x in group[group["action_type"] == action_type][["prev_dep", "prev_gov", "prev_rel"]].to_numpy()]
                corrections_ep[count_action][key]["new"] = [tuple(map(lambda x: x if x != -1 else None, x)) for x in group[group["action_type"] == action_type][["new_dep", "new_gov", "new_rel"]].to_numpy()]

        filename = os.path.join(output_dir, "%s_%s_%s.tex" % (ep, len(trees), "_".join(map(lambda x: re.sub(r'\W', '', x), trees['gold']["sequence_info"][:10]))))
        tikz = Tikz()
        tikz.begin_doc()

        gold = trees.pop('gold')
        pred = trees.pop('pred')
        if trees == {}: # if no correction is logged
            continue
        trees = sorted(trees.items(), key=lambda x:int(x[0]))

        trees = AnnotationSetStructure([AnnotationSet(id=int(count_action),
                                                      tokens=[Token(form=token) for token in gold['sequence_info']],
                                                      tags=[Tag(form=tag) for tag in tree['tag_info']],
                                                      deps=[Arc(dep=dep[0], gov=dep[1], rel=dep[2]) for dep in tree['dependencies_info']] + ([Arc(tree['root_info']), ] if tree['root_info'] is not None else []),
                                                      sdps=[Arc(dep=sdp[0], gov=sdp[1], rel=sdp[2]) for sdp in tree['semantic_dependencies_info']] + [Arc(toppred) for toppred in tree['toppreds_info']],
                                                      ) for count_action, tree in trees]).diff(corrections_ep)

        tikz.add_trees(trees)

        pred = AnnotationSet(id=-1,
                             tokens=[Token(form=token) for token in gold['sequence_info']],
                             tags=[Tag(form=tag) for tag in pred['tag_info']],
                             deps=[Arc(dep=dep[0], gov=dep[1], rel=dep[2]) for dep in pred['dependencies_info']] + ([Arc(pred['root_info']), ] if pred['root_info'] is not None else []),
                             sdps=[Arc(dep=sdp[0], gov=sdp[1], rel=sdp[2]) for sdp in pred['semantic_dependencies_info']] + [Arc(toppred) for toppred in pred['toppreds_info']],
                             )
        if pred != trees.get(-1):
            tikz.add_tree(pred._diff(trees.get(-1)))

        gold = AnnotationSet(id=-1,
                             tokens=[Token(form=token) for token in gold['sequence_info']],
                             tags=[Tag(form=tag) for tag in gold['tag_info']],
                             deps=[Arc(dep=dep[0], gov=dep[1], rel=dep[2]) for dep in gold['dependencies_info']] + [Arc(gold['root_info']), ],
                             sdps=[Arc(dep=sdp[0], gov=sdp[1], rel=sdp[2]) for sdp in gold['semantic_dependencies_info']] + [Arc(toppred) for toppred in gold['toppreds_info']],
                             )
        tikz.add_tree(gold.set_colors(color_add='Aquamarine', color_del='Salmon', color_sub='OliveGreen')._diff(pred))

        tikz.end_doc()
        tikz.write(filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir", required=True)
    parser.add_argument("-o", "--output_dir", required=True)
    args = parser.parse_args()

    for filename in os.listdir(args.input_dir):
        if filename[-5:] == ".json":
            filename = filename[:-5]
            run(os.path.join(args.input_dir, filename), os.path.join(args.output_dir, filename))