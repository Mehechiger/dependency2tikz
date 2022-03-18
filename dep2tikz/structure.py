#!/usr/bin/python3
# -*- coding:utf-8 -*-
from .tikz import _sub_spes

class AnnotationUnit:
    def __init__(self, color=None):
        self.color = color

    def paint(self, color=None):
        self.color = color
        return self

    def bleach(self):
        return self.paint()

    def copy(self):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class AnnotationUnitWithPrev(AnnotationUnit):
    def __init__(self, form, color=None):
        super().__init__(color=color)
        self.set_form(form)
        self.form_prev = None
        self.color_prev = None

    def set_form(self, form):
        self.form = form
        return self

    @property
    def empty(self):
        return self.form is None

    def copy(self):
        return AnnotationUnitWithPrev(form=self.form, color=self.color)

    def __hash__(self):
        return self.form.__hash__()

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.form == other.form)

    def __str__(self):
        if self.form == None:  # In current configurations, neither token nor tag could be deleted without adding a new one (sub allowed)
            return r'\qquad'

        form = _sub_spes(self.form)
        if self.color is not None:
            string = r'\textcolor{%s}{%s}' % (self.color, form)
        else:
            string = form
        if self.form_prev is not None and self.color_prev is not None:
            form_prev = _sub_spes(self.form_prev)
            string += r'/\textcolor{%s}{%s}' % (self.color_prev, form_prev)
        return string


class Token(AnnotationUnitWithPrev):
    def __init__(self, form, color=None):
        super().__init__(form=form, color=color)

    def copy(self):
        return Token(form=self.form, color=self.color)


class Tag(AnnotationUnitWithPrev):
    def __init__(self, form, form_prev=None, color=None, color_prev=None):
        super().__init__(form=form, color=color)
        self.form_prev = form_prev
        self.color_prev = color_prev

    def set_form_prev(self, form_prev=None):
        self.form_prev = form_prev
        return self

    def paint_prev(self, color_prev=None):
        self.color_prev = color_prev
        return self

    def copy(self):
        return Tag(form=self.form, form_prev=self.form_prev, color=self.color, color_prev=self.color_prev)

    def drop_prev(self):
        return self.set_form_prev().paint_prev()


class Arc(AnnotationUnit):
    def __init__(self, dep, gov=None, rel=None, rel_prev=None, color=None, color_prev=None, start=0):
        super().__init__(color=color)
        self.dep = dep
        self.gov = gov
        self.rel = rel
        self.rel_prev = rel_prev
        self.color_prev = color_prev
        if start is None:
            return
        elif start == 0:
            self.dep += 1
            if self.gov is not None:
                self.gov += 1

    def set_rel_prev(self, rel_prev=None):
        self.rel_prev = rel_prev
        return self

    def paint_prev(self, color_prev=None):
        self.color_prev = color_prev
        return self

    def copy(self):
        return Arc(dep=self.dep, gov=self.gov, rel=self.rel, rel_prev=self.rel_prev, color=self.color, color_prev=self.color_prev, start=None)

    def drop_prev(self):
        self.rel_prev = None
        return self

    def __hash__(self):
        return (self.dep, self.gov, self.rel).__hash__()

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.gov == other.gov) and (self.dep == other.dep) and (self.rel == other.rel)

    def str(self, rel=None):
        if rel is None:
            if self.rel is None:
                return ""
            else:
                rel = self.rel

        rel = _sub_spes(rel)
        if self.color is not None:
            string = r'\textcolor{%s}{%s}' % (self.color, rel)
        else:
            string = rel
        if self.rel_prev is not None and self.color_prev is not None:
            rel_prev = _sub_spes(self.rel_prev)
            string += r'/\textcolor{%s}{%s}' % (self.color_prev, rel_prev)
        return string


class AnnotationSet:
    def __init__(self, id, tokens, tags=None, deps=None, sdps=None, color_add='blue', color_del='red', color_sub='green', show_token_pos=True):
        self.id = id
        self._process(tokens, tags, deps, sdps, show_token_pos)
        self.components = [self.with_tag, self.with_syn, self.with_sem]
        self.color_add = color_add
        self.color_del = color_del
        self.color_sub = color_sub

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.tokens == other.tokens) and (self.tags_cleaned == other.tags_cleaned) and (self.deps_cleaned == other.deps_cleaned) and (self.sdps_cleaned == other.sdps_cleaned)

    def set_colors(self, color_add='blue', color_del='red', color_sub='green'):
        self.color_add = color_add
        self.color_del = color_del
        self.color_sub = color_sub
        return self

    def paint_all(self, color=None):
        self.tokens = [token.paint(color) for token in self.tokens]

        if self.with_tag:
            self.tags = [tag.paint(color) for tag in self.tags]

        if self.with_syn:
            self.deps = {dep.paint(color) for dep in self.deps}

        if self.with_sem:
            self.sdps = {sdp.paint(color) for sdp in self.sdps}

        return self

    def bleach_all(self, clean=False):
        if clean:
            self.tags = self.tags_cleaned
            self.deps = self.deps_cleaned
            self.sdps = self.sdps_cleaned
        return self.paint_all()

    def _process(self, tokens, tags=None, deps=None, sdps=None, show_token_pos=True):
        self.tokens = tokens
        self.with_tag, self.with_syn, self.with_sem = False, False, False

        if tags is not None:
            self.with_tag = True
            self.tags = tags

        if deps is not None:
            self.with_syn = True
            self.deps = set(deps)

        if sdps is not None:
            self.with_sem = True
            self.sdps = set(sdps)

    @property
    def tags_cleaned(self):
        return [tag.drop_prev() for tag in self.tags]

    @property
    def deps_cleaned(self):
        return {dep.drop_prev() for dep in self.deps if dep.color != self.color_del}

    @property
    def sdps_cleaned(self):
        return {sdp.drop_prev() for sdp in self.sdps if sdp.color != self.color_del}

    def diff(self, tags, deps, sdps):
        self.bleach_all(clean=True)
        if self.with_tag and tags["prev"]:
            pos = tags["prev"][0][0]
            prev = tags["prev"][0][2]
            new = tags["new"][0][2]
            tag = self.tags[pos]
            if tag.empty:
                tag.set_form(new).paint(self.color_add)
            else:
                tag.set_form_prev(prev).paint_prev(self.color_del).set_form(new).paint(self.color_sub)

        if self.with_syn and deps["prev"]:
            dels = set()
            subs = set()
            for prev in deps["prev"]:
                is_del = True
                for new in deps["new"]:
                    if prev.dep == new.dep and prev.gov == new.gov:
                        sub = new.copy().set_rel_prev(prev.rel).paint_prev(self.color_del)
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
                        sub = new.copy().set_rel_prev(prev.rel).paint_prev(self.color_del)
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
        assert self.components == other.components
        if self.with_tag:
            for i, tag in enumerate(self.tags):
                if other.tags[i].empty:
                    if not tag.empty:
                        tag.paint(self.color_add)
                elif tag == other.tags[i]:
                    tag.bleach()
                else:
                    tag.set_form_prev(other.tags[i].form).paint_prev(self.color_del).paint(self.color_sub)

        if self.with_syn:
            only_this = {dep.copy(): True for dep in self.deps_cleaned.difference(other.deps_cleaned)}
            only_other = {dep.copy() for dep in other.deps_cleaned.difference(self.deps_cleaned)}
            self.deps = {dep.copy().bleach() for dep in self.deps_cleaned.intersection(other.deps_cleaned)}
            for dep in only_this:
                for other_dep in only_other:
                    if dep.dep == other_dep.dep and dep.gov == other_dep.gov:
                        self.deps.add(dep.paint(self.color_sub).set_rel_prev(other_dep.rel).paint_prev(self.color_del))
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
                        self.sdps.add(sdp.paint(self.color_sub).set_rel_prev(other_sdp.rel).paint_prev(self.color_del))
                        only_other.remove(other_sdp)
                        only_this[sdp] = False
                        break
                if only_this[sdp]:
                    self.sdps.add(sdp.paint(self.color_add))
            for sdp in only_other:
                self.sdps.add(sdp.paint(self.color_del))

        return self


class AnnotationSetStructure:
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
                deps = {k: {Arc(dep=arc[0], gov=arc[1], rel=arc[2]) for arc in v} for k, v in corrections_tree["deps"].items()}
                sdps = {k: {Arc(dep=arc[0], gov=arc[1], rel=arc[2]) for arc in v} for k, v in corrections_tree["sdps"].items()}
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