import re, json

with open('index.html', 'r') as f:
    html = f.read()

# Replace the hardcoded data with a fetch call
old = re.search(r'const allData\s*=\s*\{.*?\};\s*const ERA_STYLES', html, re.DOTALL).group(0)
new = '''const ERA_STYLES'''

# New fetch-based initialization
fetch_code = '''
let allData = null;

async function loadContent() {
  const res = await fetch('https://raw.githubusercontent.com/Spikes666/centuryhistories/main/flashcards/content.json');
  allData = await res.json();
  buildEraBar();
  renderToday();
}

const ERA_STYLES'''

html = html.replace(old, fetch_code)

# Replace buildEraBar/renderToday calls at bottom with loadContent()
html = html.replace('buildEraBar();\nrenderToday();', 'loadContent();')

with open('index.html', 'w') as f:
    f.write(html)

print("Done")