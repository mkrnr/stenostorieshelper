import re
from plover.log import stroke


class Simplifier(object):
    # based on https://github.com/morinted/discord_steno_bot
    left_replacements = []
    left_replacements.append(('J', 'SKWR'))
    left_replacements.append(('V', 'SR'))
    left_replacements.append(('Z', 'STKPW'))
    left_replacements.append(('G', 'TKPW'))
    left_replacements.append(('D', 'TK'))
    left_replacements.append(('N', 'TPH'))
    left_replacements.append(('F', 'TP'))
    left_replacements.append(('X', 'KP'))
    left_replacements.append(('C', 'KR'))
    left_replacements.append(('Y', 'KWR'))
    left_replacements.append(('Q', 'KW'))
    left_replacements.append(('B', 'PW'))
    left_replacements.append(('M', 'PH'))
    left_replacements.append(('L', 'HR'))
    left_replacements.append(('CH', 'KH'))

    mid_replacements = []
    mid_replacements.append(('*II', 'AO*EU'))
    mid_replacements.append(('II', 'AOEU'))
    mid_replacements.append(('*UU', 'AO*U'))
    mid_replacements.append(('UU', 'AOU'))
    mid_replacements.append(('*EE', 'AO*E'))
    mid_replacements.append(('EE', 'AOE'))
    mid_replacements.append(('OO', 'AO'))
    mid_replacements.append(('AA*', 'A*EU'))
    mid_replacements.append(('AA', 'AEU'))
    mid_replacements.append(('I', 'EU'))

    right_replacements = []
    right_replacements.append(('J', 'PBLG'))
    right_replacements.append(('N', 'PB'))
    right_replacements.append(('X', 'BGS'))
    right_replacements.append(('CH', 'FP'))
    right_replacements.append(('SH', 'RB'))
    right_replacements.append(('SHN', 'GS'))
    right_replacements.append(('K', 'BG'))
    right_replacements.append(('M', 'PL'))
    
    def simplify_outline(self, outline):
        simplified_outline = ""
        for stroke in outline.split("/"):
            simplified_outline += self.simplify_stroke(stroke) + "/"
        simplified_outline = re.sub("/$", "", simplified_outline)
        return simplified_outline

    def simplify_stroke(self, stroke):
        m = re.compile("(S?T?K?P?W?H?R?)(A?O?-?\*?E?U?)(F?R?P?B?L?G?T?S?D?Z?)")
        stroke_split = m.search(stroke)
        left = self.simplify(stroke_split.group(1), self.left_replacements)
        mid = self.simplify(stroke_split.group(2), self.mid_replacements)
        right = self.simplify(stroke_split.group(3), self.right_replacements)
        return left + mid + right

    def simplify(self, stroke_part, replacements):
        for replacement in replacements:
            stroke_part = stroke_part.replace(replacement[1], replacement[0])
        return stroke_part

    
if __name__ == '__main__':
    simplifier = Simplifier()
    print(simplifier.simplify_outline("TAEUP/AO*EU"))
