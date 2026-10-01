"""Fix remaining non-ASCII chars in app.py string literals."""
content = open('src/app.py', 'r', encoding='utf-8').read()

# Replace specific broken patterns with clean ASCII equivalents
replacements = [
    # Radio options must match exactly between definition and comparison
    ('["\\u2022 Add New Listing", " View All Listings", " Edit / Delete"]',
     '["Add New Listing", "View All Listings", "Edit / Delete"]'),
    ('if listing_action == "\\u2022 Add New Listing":',
     'if listing_action == "Add New Listing":'),
    ('elif listing_action == "View All Listings":',
     'elif listing_action == "View All Listings":'),
    # Clean up euro signs used as separators in display strings
    ('\u20ac\u20ac New: Email Notifications', '-- New: Email Notifications'),
    ('\u20ac\u20ac New: Payment / Subscription', '-- New: Payment / Subscription'),
    ('\u20ac\u20ac SEO, Open Graph', '-- SEO, Open Graph'),
    # icon= parameter fixes (these crash Streamlit)
    ('icon="\u2139\ufe0f"', ''),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f'Fixed: {repr(old[:50])}')

# Remove any remaining icon= parameters with non-ASCII values
import re
# Remove icon="<non-ascii>" patterns entirely from function calls
content = re.sub(r',\s*icon="[^\x00-\x7F]+"', '', content)
content = re.sub(r'icon="[^\x00-\x7F]+",\s*', '', content)

open('src/app.py', 'w', encoding='utf-8').write(content)
print('Done')

import ast
try:
    ast.parse(content)
    print('Syntax: OK')
except SyntaxError as e:
    print('Syntax ERROR:', e)
