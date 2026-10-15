"""Resolve supported OOXML properties without treating absent direct values as defaults.

Precedence: document defaults, basedOn paragraph styles, character styles, direct
formatting. Table conditional styles, numbering and theme font/color evaluation
are deliberately outside this resolver's coverage.
"""
from copy import deepcopy
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


class StyleResolver:
    def __init__(self, document):
        self.root = document.styles.element
        self.styles = {s.get(qn('w:styleId')): s for s in self.root.findall(qn('w:style'))}

    def chain(self, style_id, kind):
        if not style_id:
            style_id = next((key for key, s in self.styles.items()
                             if s.get(qn('w:type')) == kind and
                             s.get(qn('w:default')) in ('1', 'true', 'on')), None)
        result, seen = [], set()
        while style_id and style_id not in seen:
            seen.add(style_id)
            style = self.styles.get(style_id)
            if style is None:
                break
            result.append(style)
            base = style.find(qn('w:basedOn'))
            style_id = base.get(qn('w:val')) if base is not None else None
        return list(reversed(result))

    @staticmethod
    def style_id(properties, tag):
        node = properties.find(qn('w:' + tag)) if properties is not None else None
        return node.get(qn('w:val')) if node is not None else None

    def properties(self, paragraph, run=None, native_linked=False):
        kind = 'rPr' if run is not None else 'pPr'
        result = OxmlElement('w:' + kind)
        sources = {}

        def merge(props, source, style=False):
            if props is None:
                return
            for child in props:
                if child.tag in (qn('w:pStyle'), qn('w:rStyle')):
                    continue
                old = result.find(child.tag)
                # vanish is a toggle property in styles, an absolute value in direct formatting.
                if style and child.tag == qn('w:vanish'):
                    if child.get(qn('w:val'), 'true') not in ('0', 'false', 'off'):
                        enabled = old is not None and old.get(qn('w:val'), 'true') not in ('0', 'false', 'off')
                        if old is None:
                            old = deepcopy(child)
                            result.append(old)
                        old.set(qn('w:val'), '0' if enabled else '1')
                    sources[child.tag.rsplit('}', 1)[-1]] = source
                    continue
                if old is None:
                    result.append(deepcopy(child))
                else:
                    # Attributes of composite properties (spacing/ind/rFonts) inherit independently.
                    old.attrib.update(child.attrib)
                    for sub in child:
                        previous = old.find(sub.tag)
                        if previous is not None:
                            old.remove(previous)
                        old.append(deepcopy(sub))
                sources[child.tag.rsplit('}', 1)[-1]] = source

        defaults = self.root.find(qn('w:docDefaults'))
        if defaults is not None:
            container = defaults.find(qn('w:' + kind + 'Default'))
            merge(container.find(qn('w:' + kind)) if container is not None else None, 'docDefaults')
        ppr = paragraph.find(qn('w:pPr'))
        for style in self.chain(self.style_id(ppr, 'pStyle'), 'paragraph'):
            merge(style.find(qn('w:' + kind)), 'paragraph_style:' + style.get(qn('w:styleId')), style=True)
        if run is not None and native_linked:
            # TestVkr232 applies the linked character style before direct run
            # formatting. Keep this compatibility behavior out of the normal
            # OOXML resolver and the existing copy-repair path.
            for style in self.chain(self.style_id(ppr, 'pStyle'), 'paragraph'):
                link = style.find(qn('w:link'))
                linked = self.styles.get(link.get(qn('w:val'))) if link is not None else None
                if linked is not None and linked.get(qn('w:type')) == 'character':
                    for character in self.chain(linked.get(qn('w:styleId')), 'character'):
                        merge(character.find(qn('w:rPr')), 'native_linked_character:' + character.get(qn('w:styleId')), style=True)
        if run is not None:
            rpr = run.find(qn('w:rPr'))
            for style in self.chain(self.style_id(rpr, 'rStyle'), 'character'):
                merge(style.find(qn('w:rPr')), 'character_style:' + style.get(qn('w:styleId')), style=True)
            merge(rpr, 'direct_run')
        else:
            merge(ppr, 'direct_paragraph')
        return result, sources
