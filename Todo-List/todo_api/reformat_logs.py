import os
import re

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Remove all standard verbose headers
    content = re.sub(r'\s*print\(f"   📂 File    : .*?"\)\n', '', content)
    content = re.sub(r'\s*print\(f"   🔧 Function: .*?"\)\n', '', content)
    content = re.sub(r'\s*print\(f"   🏛️  Layer   : .*?"\)\n', '', content)
    content = re.sub(r'\s*print\(f"   🌐 Implements: .*?"\)\n', '', content)
    content = re.sub(r'\s*print\(f"   📂 Repo : .*?"\)\n', '', content)
    content = re.sub(r'\s*print\(f"              📂 File: .*?"\)\n', '', content)
    
    # Replace step lines to be sleeker
    content = re.sub(r'print\(f"   ➡️  STEP [A-Z0-9]+: (.*?)"\)', r'print(f"   ├─ ➡️  \1")', content)
    content = re.sub(r'print\(f"   ✅ STEP [A-Z0-9]+: (.*?)"\)', r'print(f"   ├─ ✅ \1")', content)
    content = re.sub(r'print\(f"   📤 STEP [A-Z0-9]+: (.*?)"\)', r'print(f"   └─ 📤 \1")', content)

    # Remove horizontal bars
    content = re.sub(r'\s*print\("="[\*0-9]+ \+ "\\n"\)\n', '', content)
    content = re.sub(r'\s*print\("\\n" \+ "="[\*0-9]+\)\n', '', content)
    content = re.sub(r'\s*print\("="[\*0-9]+\)\n', '', content)
    content = re.sub(r'\s*print\("-"[\*0-9]+\)\n', '', content)

    # Simplify other prints
    content = re.sub(r'\s*print\("📥 \[DDD\] REQUEST RECEIVED — PRESENTATION LAYER"\)\n', '', content)

    # Indentations
    content = re.sub(r'print\(f"              (.*?)"\)', r'print(f"   │    \1")', content)
    content = re.sub(r'print\(f"   ✅ (.*?)"\)', r'print(f"   ├─ ✅ \1")', content)
    content = re.sub(r'print\(f"   ❌ (.*?)"\)', r'print(f"   └─ ❌ \1")', content)
    content = re.sub(r'print\(f"   ↩️  (.*?)"\)', r'print(f"   └─ ↩️  \1")', content)

    with open(filepath, 'w') as f:
        f.write(content)

src_dir = '/Users/apple/internship-practice/Todo-List/todo_api/src'
for root, dirs, files in os.walk(src_dir):
    for file in files:
        if file.endswith('.py'):
            process_file(os.path.join(root, file))

print("Logs reformatted safely!")
