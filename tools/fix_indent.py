# -*- coding: utf-8 -*-
with open(r'10-pvz\pvz_ten_levels.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if (i < 3750 or i > 3800):
        if line.startswith('            else:'):
            new_lines.append('        else:\n')
        elif line.startswith('            fill ='):
            new_lines.append('        fill =' + line.split('fill =')[1])
        elif line.startswith('            border_c ='):
            new_lines.append('        border_c =' + line.split('border_c =')[1])
        elif line.startswith('        if highlight:'):
            new_lines.append('    if highlight:' + line.split('if highlight:')[1])
        elif line.startswith('        elif active:'):
            new_lines.append('    elif active:' + line.split('elif active:')[1])
        elif line.startswith('        hover ='):
            new_lines.append('    hover =' + line.split('hover =')[1])
        elif line.startswith('        if hover:'):
            new_lines.append('    if hover:' + line.split('if hover:')[1])
        elif line.startswith('        panel(self.screen'):
            new_lines.append('    panel(self.screen' + line.split('panel(self.screen')[1])
        elif line.startswith('        text_c ='):
            new_lines.append('    text_c =' + line.split('text_c =')[1])
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open(r'10-pvz\pvz_ten_levels.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Restored successfully!')
