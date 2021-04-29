#!/usr/bin/python3
# -*- coding:utf-8 -*-

class Arc:
    def __init__(self, dep, gov=None, rel=None, color=None, start=0):
        self.dep = dep
        self.gov = gov
        self.rel = rel
        self.rel_prev = None
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
        return self.paint()

    def copy(self):
        return Arc(dep=self.dep, gov=self.gov, rel=self.rel, color=self.color, start=None)

    def __hash__(self):
        return (self.dep, self.gov, self.rel).__hash__()

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.gov == other.gov) and (self.dep == other.dep) and (self.rel == other.rel)


class Tree:
    def __init__(self, id, tokens, tags=None, deps=None, sdps=None, color_add='blue', color_del='red', color_sub='green', show_token_pos=True):
        self.id = id
        self.tokens = tokens
        self._process(tags, deps, sdps, show_token_pos)
        self.components = [self.with_tag, self.with_syn, self.with_sem]
        self.color_add = color_add
        self.color_del = color_del
        self.color_sub = color_sub

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.tags_ == other.tags_) and (self.deps_cleaned == other.deps_cleaned) and (self.sdps_cleaned == other.sdps_cleaned)

    def set_colors(self, color_add='blue', color_del='red', color_sub='green'):
        self.color_add = color_add
        self.color_del = color_del
        self.color_sub = color_sub
        return self

    def paint_all(self, color=None):
        self.tokens = [(r'\textcolor{%s}{%s}' % (color, token) if color is not None else token) for token in self.tokens]
        if self.with_tag:
            self.tags = {i: (r'\textcolor{%s}{%s}' % (color, (tag if tag is not None else r'\qquad')) if color is not None else (tag if tag is not None else r'\qquad')) for i, tag in enumerate(self.tags_, 1)}
        if self.with_syn:
            self.deps = {dep.paint(color) for dep in self.deps}
        if self.with_sem:
            self.sdps = {sdp.paint(color) for sdp in self.sdps}
        return self

    def bleach_all(self, clean=False):
        if clean:
            self.deps = self.deps_cleaned
            self.sdps = self.sdps_cleaned
        return self.paint_all()

    def _process(self, tags=None, deps=None, sdps=None, show_token_pos=True):
        if show_token_pos:
            self.tokens = ['[%s]%s' % (pos, token) for pos, token in enumerate(self.tokens, 1)]

        if tags is not None:
            self.with_tag = True
            self.tags_ = tags
            self.tags = {i: (tag_ if tag_ is not None else r'\qquad') for i, tag_ in enumerate(self.tags_, 1)}

        if deps is not None:
            self.with_syn = True
            self.deps = set()
            for dep_ in deps:
                self.deps.add(dep_)

        if sdps is not None:
            self.with_sem = True
            self.sdps = set()
            for sdp_ in sdps:
                self.sdps.add(sdp_)

    @property
    def deps_cleaned(self):
        return {dep for dep in self.deps if dep.color != self.color_del}

    @property
    def sdps_cleaned(self):
        return {sdp for sdp in self.sdps if sdp.color != self.color_del}

    def diff(self, tags, deps, sdps):
        self.bleach_all(clean=True)
        if self.with_tag and tags["prev"]:
            pos = tags["prev"][0][0]
            new = tags["new"][0][2]
            if self.tags_[pos] is None:
                self.tags[pos + 1] = r'\textcolor{%s}{%s}' % (self.color_add, new)
            else:
                self.tags[pos + 1] = r'\textcolor{%s}{%s}\textcolor{%s}{/%s}' % (self.color_sub, new, self.color_del, self.tags_[pos])

        if self.with_syn and deps["prev"]:
            dels = set()
            subs = set()
            for prev in deps["prev"]:
                is_del = True
                for new in deps["new"]:
                    if prev.dep == new.dep and prev.gov == new.gov:
                        sub = new.copy()
                        sub.rel_prev = "/" + prev.rel
                        subs.add(sub)
                        is_del = False
                if is_del:
                    dels.add(prev.copy())
                for dep in self.deps.copy():
                    if prev.dep == dep.dep and prev.gov == dep.gov:
                        self.deps.remove(dep)

            news = deps["new"].difference(subs)
            self.deps = self.deps.difference(deps["prev"])\
                .difference(deps["new"])\
                .union({sub.paint(self.color_sub) for sub in subs})\
                .union({del_.paint(self.color_del) for del_ in dels})\
                .union({new.paint(self.color_add) for new in news})

        if self.with_sem and sdps["prev"]:
            dels = set()
            subs = set()
            for prev in sdps["prev"]:
                is_del = True
                for new in sdps["new"]:
                    if prev.dep == new.dep and prev.gov == new.gov:
                        sub = new.copy()
                        sub.rel_prev = "/" + prev.rel
                        subs.add(sub)
                        is_del = False
                if is_del:
                    dels.add(prev.copy())
                for sdp in self.sdps.copy():
                    if prev.dep == sdp.dep and prev.gov == sdp.gov:
                        self.sdps.remove(sdp)

            news = sdps["new"].difference(subs)
            self.sdps = self.sdps.difference(sdps["new"])\
                .union({sub.paint(self.color_sub) for sub in subs})\
                .union({del_.paint(self.color_del) for del_ in dels})\
                .union({new.paint(self.color_add) for new in news})

        return self

    def _diff(self, other):
        # TODO
        assert self.components == other.components
        if self.with_tag:
            for i, tag in self.tags.items():
                if other.tags_[i - 1] is None:
                    if self.tags_[i - 1] is not None:
                        self.tags[i] = r'\textcolor{%s}{%s}' % (self.color_add, tag)
                elif self.tags_[i - 1] == other.tags_[i - 1]:
                    self.tags[i] = self.tags_[i - 1] if self.tags_[i - 1] is not None else r'\qquad'
                else:
                    self.tags[i] = r'\textcolor{%s}{%s}' % (self.color_sub, tag)

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
        self.trees_ = trees

    def get(self, i):
        return self.trees[i]

    def diff(self, corrections_ep=None):
        if corrections_ep is None:
            return self._diff()
        else:
            self.trees = []
            for tree in self.trees_:
                corrections_tree = corrections_ep[tree.id]
                tags = corrections_tree["tags"]
                deps = {k: {Arc(*arc) for arc in v} for k, v in corrections_tree["deps"].items()}
                sdps = {k: {Arc(*arc) for arc in v} for k, v in corrections_tree["sdps"].items()}
                self.trees.append(tree.diff(tags, deps, sdps))
            return self

    def _diff(self):
        self.trees = [self.trees_[0], ]
        if len(self.trees_) < 2:
            return self

        for i in range(1, len(self.trees_)):
            self.trees.append(self.trees_[i]._diff(self.trees_[i-1]))
        return self

    def __iter__(self):
        return iter(self.trees)