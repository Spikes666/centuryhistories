#!/usr/bin/env python3
"""
Weekly content updater — calls Claude API to generate new facts,
adds them to content.json, and pushes to GitHub.
"""
import json, os, subprocess, random
from datetime import datetime
import urllib.request, urllib.error

CONTENT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flashcards/content.json')
API_KEY_PATH = os.path.expanduser('~/.anthropic_api_key')
FACTS_TO_ADD = 5
LOG_PATH     = os.path.expanduser('~/centuryhistories/update.log')

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_PATH, 'a') as f:
        f.write(line + '\n')

def get_api_key():
    if os.path.exists(API_KEY_PATH):
        with open(API_KEY_PATH) as f:
            return f.read().strip()
    return os.environ.get('ANTHROPIC_API_KEY', '')

def call_claude(prompt, api_key):
    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01'
        }
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
        return data['content'][0]['text']

def generate_facts(century, existing_facts, api_key):
    existing_sample = '\n'.join(f'- {f["fact"]}' for f in existing_facts[:5])
    prompt = f"""You are a historian generating flashcard facts for an educational history app.

Century: {century['label']}
Era: {century['era']}
Summary: {century['summary']}

The app draws on these sources:
- "Misquoting Jesus" by Bart Ehrman (early Christianity, textual criticism, Biblical history)
- "The Rest is History" podcast by Tom Holland and Dominic Sandbrook (world history)
- "Dominion" by Tom Holland (how Christianity shaped Western civilization)

Here are some existing facts for this century (do NOT repeat these):
{existing_sample}

Generate exactly {FACTS_TO_ADD} new, distinct historical facts for this century.
Each fact should be 1-3 sentences, specific, and educational.
Draw on the same sources and themes as the existing facts.
Focus on facts not already covered above.

Return ONLY a JSON array of strings, no other text. Example format:
["Fact one here.", "Fact two here.", "Fact three here."]"""

    response = call_claude(prompt, api_key)
    response = response.strip()
    if response.startswith('```'):
        response = response.split('\n', 1)[1]
        response = response.rsplit('```', 1)[0]
    return json.loads(response.strip())

def get_region(fact_text):
    lower = fact_text.lower()
    REGIONS = [
        {"k":["large language model","artificial intelligence","chatgpt","machine learning","neural network"], "lat":20.0,"lng":0.0,"z":2,"l":"The Modern World"},
        {"k":["gettysburg"],                    "lat":39.8,  "lng":-77.2, "z":9, "l":"Gettysburg, Pennsylvania"},
        {"k":["pearl harbor"],                  "lat":21.4,  "lng":-157.9,"z":9, "l":"Pearl Harbor, Hawaii"},
        {"k":["hiroshima"],                     "lat":34.4,  "lng":132.5, "z":9, "l":"Hiroshima, Japan"},
        {"k":["nagasaki"],                      "lat":32.7,  "lng":129.9, "z":9, "l":"Nagasaki, Japan"},
        {"k":["normandy","d-day"],              "lat":49.3,  "lng":-0.7,  "z":8, "l":"Normandy, France"},
        {"k":["stalingrad"],                    "lat":48.7,  "lng":44.5,  "z":8, "l":"Stalingrad (Volgograd), Russia"},
        {"k":["auschwitz"],                     "lat":50.0,  "lng":19.2,  "z":9, "l":"Auschwitz, Poland"},
        {"k":["battle of waterloo"],            "lat":50.7,  "lng":4.4,   "z":9, "l":"Waterloo, Belgium"},
        {"k":["battle of hastings","1066"],     "lat":50.9,  "lng":0.6,   "z":9, "l":"Hastings, England"},
        {"k":["milvian bridge"],                "lat":41.9,  "lng":12.5,  "z":8, "l":"Milvian Bridge, Rome"},
        {"k":["salt march"],                    "lat":21.1,  "lng":72.6,  "z":7, "l":"Dandi, Gujarat, India"},
        {"k":["berlin wall"],                   "lat":52.5,  "lng":13.4,  "z":9, "l":"Berlin Wall, Germany"},
        {"k":["cuban missile crisis"],          "lat":23.0,  "lng":-80.0, "z":6, "l":"Cuba"},
        {"k":["moon landing","apollo 11","neil armstrong"], "lat":28.6,"lng":-80.6,"z":7,"l":"Kennedy Space Center, Florida"},
        {"k":["september 11","9/11","twin towers","world trade center"], "lat":40.7,"lng":-74.0,"z":10,"l":"New York City"},
        {"k":["korean war","38th parallel"],    "lat":37.5,  "lng":127.0, "z":6, "l":"Korean Peninsula"},
        {"k":["vietnam war","north vietnam","south vietnam"], "lat":16.0,"lng":107.0,"z":5,"l":"Vietnam"},
        {"k":["transcontinental railroad"],     "lat":41.0,  "lng":-112.0,"z":5, "l":"American West"},
        {"k":["martin luther king","march on washington"], "lat":38.9,"lng":-77.0,"z":9,"l":"Washington D.C."},
        {"k":["declaration of independence","continental congress"], "lat":39.9,"lng":-75.2,"z":8,"l":"Philadelphia, Pennsylvania"},
        {"k":["pompeii","mount vesuvius","herculaneum"], "lat":40.7,"lng":14.4,"z":9,"l":"Bay of Naples, Italy"},
        {"k":["dead sea scrolls","qumran"],     "lat":31.7,  "lng":35.5,  "z":9, "l":"Qumran, Dead Sea"},
        {"k":["hagia sophia"],                  "lat":41.0,  "lng":28.9,  "z":9, "l":"Hagia Sophia, Istanbul"},
        {"k":["dome of the rock"],              "lat":31.8,  "lng":35.2,  "z":9, "l":"Dome of the Rock, Jerusalem"},
        {"k":["house of wisdom"],               "lat":33.3,  "lng":44.4,  "z":8, "l":"Baghdad, Iraq"},
        {"k":["council of nicaea"],             "lat":40.4,  "lng":29.7,  "z":8, "l":"Nicaea (Iznik), Turkey"},
        {"k":["council of trent"],              "lat":46.1,  "lng":11.1,  "z":8, "l":"Trent, Italy"},
        {"k":["peace of westphalia"],           "lat":51.9,  "lng":7.6,   "z":8, "l":"Westphalia, Germany"},
        {"k":["treaty of versailles"],          "lat":48.8,  "lng":2.1,   "z":8, "l":"Versailles, France"},
        {"k":["justinian code","corpus juris civilis","justinian's"], "lat":41.0,"lng":28.9,"z":7,"l":"Constantinople (Istanbul), Turkey"},
        {"k":["john locke","locke argued"],     "lat":51.5,  "lng":-0.1,  "z":7, "l":"England (John Locke)"},
        {"k":["adam smith","wealth of nations","david hume"], "lat":55.9,"lng":-3.2,"z":7,"l":"Edinburgh, Scotland"},
        {"k":["wittenberg","95 theses"],        "lat":51.9,  "lng":12.6,  "z":9, "l":"Wittenberg, Germany"},
        {"k":["irenaeus of lyon"],              "lat":45.7,  "lng":4.8,   "z":8, "l":"Lyon, France"},
        {"k":["augustine of hippo","bishop of hippo"], "lat":36.9,"lng":7.8,"z":8,"l":"Hippo Regius (Annaba), Algeria"},
        {"k":["athanasius of alexandria","origen of alexandria","hypatia"], "lat":31.2,"lng":29.9,"z":8,"l":"Alexandria, Egypt"},
        {"k":["constantinople","istanbul"],     "lat":41.0,  "lng":28.9,  "z":8, "l":"Constantinople (Istanbul), Turkey"},
        {"k":["baghdad"],                       "lat":33.3,  "lng":44.4,  "z":8, "l":"Baghdad, Iraq"},
        {"k":["mecca"],                         "lat":21.4,  "lng":39.8,  "z":8, "l":"Mecca, Saudi Arabia"},
        {"k":["medina"],                        "lat":24.5,  "lng":39.6,  "z":8, "l":"Medina, Saudi Arabia"},
        {"k":["jerusalem"],                     "lat":31.8,  "lng":35.2,  "z":9, "l":"Jerusalem"},
        {"k":["library of alexandria","serapeum"], "lat":31.2,"lng":29.9, "z":8, "l":"Alexandria, Egypt"},
        {"k":["carthage"],                      "lat":36.9,  "lng":10.3,  "z":8, "l":"Carthage (near Tunis), Tunisia"},
        {"k":["florence"],                      "lat":43.8,  "lng":11.2,  "z":8, "l":"Florence, Italy"},
        {"k":["venice"],                        "lat":45.4,  "lng":12.3,  "z":8, "l":"Venice, Italy"},
        {"k":["vienna"],                        "lat":48.2,  "lng":16.4,  "z":8, "l":"Vienna, Austria"},
        {"k":["moscow"],                        "lat":55.8,  "lng":37.6,  "z":8, "l":"Moscow, Russia"},
        {"k":["athens"],                        "lat":37.9,  "lng":23.7,  "z":8, "l":"Athens, Greece"},
        {"k":["babylon"],                       "lat":32.5,  "lng":44.4,  "z":8, "l":"Babylon (near Hillah), Iraq"},
        {"k":["timbuktu"],                      "lat":16.8,  "lng":-3.0,  "z":8, "l":"Timbuktu, Mali"},
        {"k":["tenochtitlan"],                  "lat":19.4,  "lng":-99.1, "z":8, "l":"Tenochtitlan (Mexico City), Mexico"},
        {"k":["delhi"],                         "lat":28.6,  "lng":77.2,  "z":8, "l":"Delhi, India"},
        {"k":["antioch"],                       "lat":36.2,  "lng":36.2,  "z":8, "l":"Antioch (Antakya), Turkey"},
        {"k":["nazareth"],                      "lat":32.7,  "lng":35.3,  "z":9, "l":"Nazareth, Israel"},
        {"k":["new york city","new york,","manhattan","wall street"], "lat":40.7,"lng":-74.0,"z":9,"l":"New York City"},
        {"k":["washington, d.c.","white house","capitol hill"], "lat":38.9,"lng":-77.0,"z":9,"l":"Washington D.C."},
        {"k":["mesopotamia","sumer","sumerian","gilgamesh","cuneiform","akkad"], "lat":33.0,"lng":44.0,"z":5,"l":"Mesopotamia (modern Iraq)"},
        {"k":["egypt","egyptian","nile","pharaoh","ptolemy","osiris"], "lat":26.8,"lng":30.8,"z":5,"l":"Egypt"},
        {"k":["persia","persian empire","sassanid","achaemenid","zoroastrian","cyrus the great"], "lat":32.4,"lng":53.7,"z":5,"l":"Persia (modern Iran)"},
        {"k":["arabian peninsula","hijra","islam spread","arab conquest","umayyad","abbasid caliphate"], "lat":24.0,"lng":45.0,"z":5,"l":"Arabian Peninsula"},
        {"k":["ottoman empire","ottoman sultan","suleiman","mehmed ii"], "lat":39.0,"lng":35.0,"z":5,"l":"Ottoman Empire (modern Turkey)"},
        {"k":["byzantine empire","byzantine emperor","byzantine forces"], "lat":41.0,"lng":29.0,"z":5,"l":"Byzantine Empire"},
        {"k":["roman empire","pax romana","roman roads","roman province"], "lat":41.9,"lng":12.5,"z":4,"l":"The Roman Empire"},
        {"k":["rome,","in rome","of rome","sacked rome","emperor nero","emperor augustus","imperial rome"], "lat":41.9,"lng":12.5,"z":7,"l":"Rome, Italy"},
        {"k":["judea","judah","israel","hebrew bible","jewish revolt","jewish war","maccab","hasmonean","zealot","pharisee","essene"], "lat":31.8,"lng":35.2,"z":6,"l":"Judea / Israel"},
        {"k":["greece","greek philosophy","helleni","macedon","alexander the great","neoplatonism"], "lat":38.0,"lng":23.7,"z":6,"l":"Greece"},
        {"k":["syria","palmyra","zenobia","damascus"], "lat":35.0,"lng":38.0,"z":6,"l":"Syria"},
        {"k":["charlemagne","carolingian","frankish kingdom","merovingian","clovis"], "lat":46.6,"lng":2.2,"z":5,"l":"Frankish Kingdom (modern France)"},
        {"k":["france","french revolution","paris,","napoleon,","bourbon"], "lat":46.2,"lng":2.2,"z":5,"l":"France"},
        {"k":["england","britain","british empire","london,","anglo-saxon","tudor","plantagenet"], "lat":52.0,"lng":-1.5,"z":6,"l":"England / Britain"},
        {"k":["germany","holy roman empire","prussia","bismarck","german unification"], "lat":51.2,"lng":10.5,"z":5,"l":"Germany"},
        {"k":["spain","iberian","reconquista","al-andalus","castile","spanish inquisition"], "lat":40.4,"lng":-3.7,"z":5,"l":"Spain"},
        {"k":["italy","italian city","papal states","the papacy","renaissance italy"], "lat":42.5,"lng":12.5,"z":5,"l":"Italy"},
        {"k":["scandinavia","viking age","norse","norway","sweden","denmark","iceland","leif eriksson"], "lat":62.0,"lng":15.0,"z":4,"l":"Scandinavia"},
        {"k":["ireland","irish monk","irish monastery","saint patrick"], "lat":53.4,"lng":-8.2,"z":6,"l":"Ireland"},
        {"k":["russia","soviet union","ussr","bolshevik","tsar nicholas","russian revolution"], "lat":55.8,"lng":37.6,"z":4,"l":"Russia"},
        {"k":["china","chinese empire","ming dynasty","qing dynasty","tang dynasty","song dynasty"], "lat":35.9,"lng":104.2,"z":4,"l":"China"},
        {"k":["japan","japanese empire","meiji restoration","tokugawa","samurai"], "lat":36.2,"lng":138.3,"z":5,"l":"Japan"},
        {"k":["india","mughal empire","british raj","indian subcontinent"], "lat":20.6,"lng":79.0,"z":4,"l":"India"},
        {"k":["africa","west africa","mali empire","songhai empire","rwanda","south africa","apartheid"], "lat":8.0,"lng":21.0,"z":4,"l":"Africa"},
        {"k":["mongol empire","mongol conquest","genghis khan","kublai khan"], "lat":47.9,"lng":106.9,"z":4,"l":"Mongolia"},
        {"k":["united states","american civil war","american revolution","american independence"], "lat":38.9,"lng":-95.7,"z":4,"l":"United States"},
        {"k":["mexico","aztec empire","maya","spanish conquest of"], "lat":19.4,"lng":-99.1,"z":5,"l":"Mexico"},
        {"k":["caribbean","cuba,","haiti,","saint-domingue"], "lat":19.0,"lng":-72.0,"z":5,"l":"Caribbean"},
        {"k":["portugal","portuguese empire","vasco da gama"], "lat":39.4,"lng":-8.2,"z":6,"l":"Portugal"},
        {"k":["age of exploration","circumnavigation","columbus","magellan"], "lat":10.0,"lng":-30.0,"z":3,"l":"Age of Exploration"},
        {"k":["early christian","christian community","new testament","old testament","the gospels","gospel of","bart ehrman","misquoting jesus","textual criticism","biblical manuscript"], "lat":35.0,"lng":25.0,"z":4,"l":"The Early Christian World"},
        {"k":["world war ii","second world war","nazi germany","the holocaust","third reich"], "lat":50.0,"lng":14.0,"z":4,"l":"World War II Europe"},
        {"k":["world war i","first world war","western front","assassination of archduke"], "lat":49.0,"lng":3.0,"z":5,"l":"World War I — Western Front"},
        {"k":["cold war","iron curtain","nato alliance","warsaw pact"], "lat":52.0,"lng":20.0,"z":3,"l":"Cold War Europe"},
        {"k":["industrial revolution","steam engine","factory system","spinning jenny"], "lat":52.5,"lng":-1.9,"z":6,"l":"Industrial Revolution — England"},
        {"k":["french revolution","reign of terror","robespierre","storming of the bastille"], "lat":48.9,"lng":2.3,"z":7,"l":"Paris, France"},
        {"k":["internet","world wide web","social media","covid-19","climate change","global pandemic"], "lat":20.0,"lng":0.0,"z":2,"l":"The Modern World"},
    ]
    for r in REGIONS:
        for k in r["k"]:
            if k in lower:
                d = {2:60,3:35,4:22,5:12,6:6,7:3,8:1.5,9:0.7,10:0.35}.get(r["z"], 8)
                bbox = f"{r['lng']-d},{r['lat']-d},{r['lng']+d},{r['lat']+d}"
                return {
                    "map_label": r["l"],
                    "map_iframe": f"https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={r['lat']},{r['lng']}"
                }
    return {
        "map_label": "The Mediterranean & Ancient World",
        "map_iframe": "https://www.openstreetmap.org/export/embed.html?bbox=-15,25,55,55&layer=mapnik"
    }
def git_push(message):
    repo = os.path.dirname(os.path.abspath(__file__))
    subprocess.run(['git', '-C', repo, 'add', 'flashcards/content.json'], check=True)
    subprocess.run(['git', '-C', repo, 'commit', '-m', message], check=True)
    subprocess.run(['git', '-C', repo, 'push'], check=True)

def main():
    log("=== Content update starting ===")

    api_key = get_api_key()
    if not api_key:
        log("ERROR: No API key found. Create ~/.anthropic_api_key or set ANTHROPIC_API_KEY")
        return

    with open(CONTENT_PATH) as f:
        data = json.load(f)

    century = random.choice(data['centuries'])
    log(f"Updating: {century['label']} (currently {len(century['facts'])} facts)")

    try:
        new_fact_texts = generate_facts(century, century['facts'], api_key)
        log(f"Generated {len(new_fact_texts)} new facts")
    except Exception as e:
        log(f"ERROR generating facts: {e}")
        return

    added = 0
    for text in new_fact_texts:
        if text and text not in [f['fact'] for f in century['facts']]:
            maps = get_region(text)
            century['facts'].append({
                "fact": text,
                "map_label": maps['map_label'],
                "map_iframe": maps['map_iframe']
            })
            added += 1
            log(f"  + [{maps['map_label']}] {text[:70]}...")

    if added == 0:
        log("No new facts added — all duplicates or empty")
        return

    with open(CONTENT_PATH, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total = sum(len(c['facts']) for c in data['centuries'])
    log(f"Saved. Total facts: {total}")

    try:
        git_push(f"Auto: +{added} facts for {century['label']} [{datetime.now().strftime('%Y-%m-%d')}]")
        log("Pushed to GitHub successfully")
    except Exception as e:
        log(f"ERROR pushing to GitHub: {e}")

    log("=== Done ===")

if __name__ == '__main__':
    main()