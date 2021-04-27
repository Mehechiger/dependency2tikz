#!/usr/bin/python3
# -*- coding:utf-8 -*-

class Arc:
    def __init__(self, dep, gov=None, rel=None, color=None, start=0):
        self.dep = dep
        self.gov = gov
        self.rel = rel
        self.color = color
        self.start = start
        if self.start is None:
            return
        elif self.start == 0:
            self.dep += 1
            if self.gov is not None:
                self.gov += 1

    def paint(self, color=None):
        self.color = color
        return self

    def bleach(self):
        self.paint()
        return self

    def copy(self):
        return Arc(dep=self.dep, gov=self.gov, rel=self.rel, color=self.color, start=None)

    def __hash__(self):
        return (self.dep, self.gov, self.rel).__hash__()

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.gov == other.gov) and (self.dep == other.dep) and (self.rel == other.rel)


class Tree:
    def __init__(self, tokens, tags=None, deps=None, sdps=None, color_add=r'blue', color_del=r'red', color_sub=r'green'):
        self.tokens = tokens
        self._process(tags, deps, sdps)
        self.components = [self.with_tag, self.with_syn, self.with_sem]
        self.color_add = color_add
        self.color_del = color_del
        self.color_sub = color_sub

    def _process(self, tags=None, deps=None, sdps=None):
        if tags is not None:
            self.with_tag = True
            self.tags_ = tags
            self.tags = {i: (tag if tag is not None else r'\qquad') for i, tag in enumerate(tags, 1)}

        if deps is not None:
            self.with_syn = True
            self.root = None
            self.deps = set()
            for dep_ in deps:
                self.deps.add(dep_)

        if sdps is not None:
            self.with_sem = True
            self.sdps = set()
            self.toppreds = set()
            for sdp_ in sdps:
                self.sdps.add(sdp_)

    @property
    def deps_cleaned(self):
        return {dep for dep in self.deps if dep.color != self.color_del}

    @property
    def sdps_cleaned(self):
        return {sdp for sdp in self.sdps if sdp.color != self.color_del}

    def diff(self, other):
        assert self.components == other.components
        if self.with_tag:
            for i, tag in self.tags.items():
                if other.tags_[i - 1] is None:
                    if self.tags_[i - 1] is not None:
                        self.tags[i] = r'\textcolor{%s}{%s}' % (self.color_add, tag)
                elif self.tags_[i - 1] == other.tags_[i - 1]:
                    self.tags[i] = self.tags_[i - 1]
                else:
                    self.tags[i] = r'\textcolor{%s}{%s}' % (self.color_sub, tag)

        """
        if self.with_syn:
            only_this = {dep.copy() for dep in self.deps.difference(other.deps)}
            only_other = {dep.copy() for dep in other.deps.difference(self.deps)}
            self.deps = {dep.copy().bleach() for dep in self.deps.intersection(other.deps)}\
                .union({dep.copy().paint(self.color_add) for dep in only_this})\
                .union({dep.copy().paint(self.color_del) for dep in only_other})

        if self.with_sem:
            only_this = {sdp.copy() for sdp in self.sdps.difference(other.sdps)}
            only_other = {sdp.copy() for sdp in other.sdps.difference(self.sdps)}
            self.sdps = {sdp.copy().bleach() for sdp in self.sdps.intersection(other.sdps)}\
                .union({sdp.copy().paint(self.color_add) for sdp in only_this})\
                .union({sdp.copy().paint(self.color_del) for sdp in only_other})
        """

        if self.with_syn:
            only_this = {dep.copy(): True for dep in self.deps_cleaned.difference(other.deps_cleaned)}
            only_other = {dep.copy() for dep in other.deps_cleaned.difference(self.deps_cleaned)}
            self.deps = {dep.copy().bleach() for dep in self.deps_cleaned.intersection(other.deps_cleaned)}
            for dep in only_this:
                for other_dep in only_other:
                    if dep.dep == other_dep.dep and dep.gov == other_dep.gov:
                        self.deps.add(dep.paint(self.color_sub))
                        only_other.remove(other_dep)
                        only_this[dep] = False
                        break
                if only_this[dep]:
                    self.deps.add(dep.paint(self.color_add))
            for dep in only_other:
                self.deps.add(dep.paint(self.color_del))

        if self.with_sem:
            only_this = {sdp.copy(): True for sdp in self.sdps_cleaned.difference(other.sdps_cleaned)}
            only_other = {sdp.copy() for sdp in other.sdps_cleaned.difference(self.sdps_cleaned)}
            self.sdps = {sdp.copy().bleach() for sdp in self.sdps_cleaned.intersection(other.sdps_cleaned)}
            for sdp in only_this:
                for other_sdp in only_other:
                    if sdp.dep == other_sdp.dep and sdp.gov == other_sdp.gov:
                        self.sdps.add(sdp.paint(self.color_sub))
                        only_other.remove(other_sdp)
                        only_this[sdp] = False
                        break
                if only_this[sdp]:
                    self.sdps.add(sdp.paint(self.color_add))
            for sdp in only_other:
                self.sdps.add(sdp.paint(self.color_del))

        return self


class ForestStructure:
    def __init__(self, trees):
        self.trees = [trees[0], ]
        if len(trees) < 2:
            return

        for i in range(1, len(trees)):
            self.trees.append(trees[i].diff(trees[i-1]))

    def __iter__(self):
        return iter(self.trees)