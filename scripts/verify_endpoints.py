import re, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app

app = create_app()
# Collect endpoints referenced in source/templates
pattern = re.compile(r"url_for\('\s*([\w\.]+)\s*'")
refs = set()
for root, dirs, files in os.walk('.'):
    for fn in files:
        if fn.endswith(('.py', '.html')):
            path = os.path.join(root, fn)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    s = f.read()
                for m in pattern.finditer(s):
                    refs.add(m.group(1))
            except Exception:
                pass

# Collect actual endpoints
with app.app_context():
    endpoints = set(r.endpoint for r in app.url_map.iter_rules())

missing = sorted([r for r in refs if r not in endpoints])
print('Referenced endpoints:', sorted(refs))
print('\nRegistered endpoints:', sorted(endpoints))
print('\nMissing endpoints:', missing)
if missing:
    sys.exit(2)
else:
    sys.exit(0)
