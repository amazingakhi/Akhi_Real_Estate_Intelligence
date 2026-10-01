"""Quick check for non-ASCII outside comments/HTML."""
content = open('src/app.py', 'r', encoding='utf-8').read()
lines = content.split('\n')
problem_lines = []
for i, line in enumerate(lines):
    stripped = line.strip()
    if any(ord(c) > 127 for c in line):
        if stripped.startswith('#'):
            continue
        if stripped.startswith('<') or '"""' in stripped or "'''" in stripped:
            continue
        problem_lines.append((i + 1, line[:120]))

print(f'Potentially problematic lines: {len(problem_lines)}')
for ln, text in problem_lines[:30]:
    print(f'  Line {ln}: {repr(text)}')
