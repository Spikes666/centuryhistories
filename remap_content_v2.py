#!/usr/bin/env python3
"""
Remaps all facts in content.json to more specific geographic locations.
Version 2 — tighter keyword matching, no false positives.
"""
import json, os

CONTENT_PATH = 'flashcards/content.json'

REGIONS = [
    # ── Specific battles / events ──
    {"k":["gettysburg"],                    "lat":39.8,  "lng":-77.2, "z":9, "l":"Gettysburg, Pennsylvania"},
    {"k":["pearl harbor"],                  "lat":21.4,  "lng":-157.9,"z":9, "l":"Pearl Harbor, Hawaii"},
    {"k":["hiroshima"],                     "lat":34.4,  "lng":132.5, "z":9, "l":"Hiroshima, Japan"},
    {"k":["nagasaki"],                      "lat":32.7,  "lng":129.9, "z":9, "l":"Nagasaki, Japan"},
    {"k":["normandy","d-day"],              "lat":49.3,  "lng":-0.7,  "z":8, "l":"Normandy, France"},
    {"k":["stalingrad"],                    "lat":48.7,  "lng":44.5,  "z":8, "l":"Stalingrad (Volgograd), Russia"},
    {"k":["auschwitz"],                     "lat":50.0,  "lng":19.2,  "z":9, "l":"Auschwitz, Poland"},
    {"k":["battle of waterloo"],            "lat":50.7,  "lng":4.4,   "z":9, "l":"Waterloo, Belgium"},
    {"k":["battle of hastings","1066"],     "lat":50.9,  "lng":0.6,   "z":9, "l":"Hastings, England"},
    {"k":["battle of crécy","battle of crecy"], "lat":50.2,"lng":1.9, "z":9, "l":"Crécy, France"},
    {"k":["battle of tours","battle of poitiers","732 ce"], "lat":46.6,"lng":0.3,"z":7,"l":"Tours/Poitiers, France"},
    {"k":["battle of lepanto"],             "lat":38.4,  "lng":21.5,  "z":8, "l":"Gulf of Lepanto, Greece"},
    {"k":["battle of manzikert"],           "lat":39.2,  "lng":42.5,  "z":8, "l":"Manzikert, Turkey"},
    {"k":["battle of yarmouk"],             "lat":32.8,  "lng":36.1,  "z":8, "l":"Yarmouk River, Syria"},
    {"k":["battle of karbala","karbala"],   "lat":32.6,  "lng":44.0,  "z":8, "l":"Karbala, Iraq"},
    {"k":["battle of adrianople","378 ce"], "lat":41.7,  "lng":26.6,  "z":8, "l":"Adrianople (Edirne), Turkey"},
    {"k":["battle of ain jalut"],           "lat":32.6,  "lng":35.3,  "z":8, "l":"Ain Jalut, Palestine"},
    {"k":["battle of las navas"],           "lat":38.3,  "lng":-3.6,  "z":8, "l":"Las Navas de Tolosa, Spain"},
    {"k":["battle of talas","talas river"], "lat":42.5,  "lng":72.2,  "z":7, "l":"Talas River, Central Asia"},
    {"k":["battle of lechfeld"],            "lat":48.2,  "lng":10.9,  "z":8, "l":"Lechfeld, Bavaria"},
    {"k":["milvian bridge"],                "lat":41.9,  "lng":12.5,  "z":8, "l":"Milvian Bridge, Rome"},
    {"k":["salt march"],                    "lat":21.1,  "lng":72.6,  "z":7, "l":"Dandi, Gujarat, India"},
    {"k":["berlin wall"],                   "lat":52.5,  "lng":13.4,  "z":9, "l":"Berlin Wall, Germany"},
    {"k":["cuban missile crisis"],          "lat":23.0,  "lng":-80.0, "z":6, "l":"Cuba"},
    {"k":["moon landing","apollo 11","neil armstrong"], "lat":28.6,"lng":-80.6,"z":7,"l":"Kennedy Space Center, Florida"},
    {"k":["september 11","9/11","twin towers","world trade center"], "lat":40.7,"lng":-74.0,"z":10,"l":"New York City"},
    {"k":["korean war","38th parallel"],    "lat":37.5,  "lng":127.0, "z":6, "l":"Korean Peninsula"},
    {"k":["vietnam war","north vietnam","south vietnam","saigon","hanoi"], "lat":16.0,"lng":107.0,"z":5,"l":"Vietnam"},
    {"k":["transcontinental railroad"],     "lat":41.0,  "lng":-112.0,"z":5, "l":"American West"},
    {"k":["march on washington","martin luther king"], "lat":38.9,"lng":-77.0,"z":9,"l":"Washington D.C."},
    {"k":["emancipation proclamation","gettysburg address"], "lat":38.9,"lng":-77.0,"z":7,"l":"Washington D.C."},
    {"k":["civil rights act","voting rights act"], "lat":38.9,"lng":-77.0,"z":8,"l":"Washington D.C."},
    {"k":["wall street crash","stock market crash 1929"], "lat":40.7,"lng":-74.0,"z":10,"l":"Wall Street, New York"},
    {"k":["marshall plan"],                 "lat":52.0,  "lng":13.0,  "z":4, "l":"Post-War Europe"},
    {"k":["boston tea party","boston massacre"], "lat":42.4,"lng":-71.1,"z":9,"l":"Boston, Massachusetts"},
    {"k":["declaration of independence","continental congress"], "lat":39.9,"lng":-75.2,"z":8,"l":"Philadelphia, Pennsylvania"},
    {"k":["constitutional convention","us constitution"], "lat":39.9,"lng":-75.2,"z":8,"l":"Philadelphia, Pennsylvania"},
    # ── Specific ancient / medieval sites ──
    {"k":["pompeii","mount vesuvius","herculaneum"], "lat":40.7,"lng":14.4,"z":9,"l":"Bay of Naples, Italy"},
    {"k":["dead sea scrolls","qumran"],     "lat":31.7,  "lng":35.5,  "z":9, "l":"Qumran, Dead Sea"},
    {"k":["nag hammadi"],                   "lat":26.0,  "lng":32.3,  "z":9, "l":"Nag Hammadi, Egypt"},
    {"k":["great pyramid","pyramid of giza"], "lat":29.9,"lng":31.1,  "z":9, "l":"Giza, Egypt"},
    {"k":["the colosseum","flavian amphitheatre"], "lat":41.9,"lng":12.5,"z":9,"l":"The Colosseum, Rome"},
    {"k":["hadrian's wall"],                "lat":55.0,  "lng":-2.2,  "z":8, "l":"Hadrian's Wall, Northern England"},
    {"k":["hagia sophia"],                  "lat":41.0,  "lng":28.9,  "z":9, "l":"Hagia Sophia, Istanbul"},
    {"k":["dome of the rock"],              "lat":31.8,  "lng":35.2,  "z":9, "l":"Dome of the Rock, Jerusalem"},
    {"k":["notre-dame de paris","notre-dame cathedral"], "lat":48.9,"lng":2.3,"z":9,"l":"Notre-Dame, Paris"},
    {"k":["palace of versailles"],          "lat":48.8,  "lng":2.1,   "z":9, "l":"Palace of Versailles, France"},
    {"k":["potosí","potosi, bolivia"],      "lat":-19.6, "lng":-65.8, "z":8, "l":"Potosí, Bolivia"},
    {"k":["house of wisdom"],               "lat":33.3,  "lng":44.4,  "z":8, "l":"Baghdad, Iraq"},
    # ── Specific councils / treaties ──
    {"k":["council of nicaea"],             "lat":40.4,  "lng":29.7,  "z":8, "l":"Nicaea (Iznik), Turkey"},
    {"k":["council of ephesus"],            "lat":37.9,  "lng":27.3,  "z":8, "l":"Ephesus, Turkey"},
    {"k":["council of chalcedon"],          "lat":40.9,  "lng":29.1,  "z":8, "l":"Chalcedon (Kadikoy), Turkey"},
    {"k":["council of trent"],              "lat":46.1,  "lng":11.1,  "z":8, "l":"Trent, Italy"},
    {"k":["council of constance"],          "lat":47.7,  "lng":9.2,   "z":8, "l":"Constance, Germany"},
    {"k":["diet of worms"],                 "lat":49.6,  "lng":8.4,   "z":8, "l":"Worms, Germany"},
    {"k":["edict of milan"],                "lat":45.5,  "lng":9.2,   "z":8, "l":"Milan, Italy"},
    {"k":["edict of thessalonica"],         "lat":40.6,  "lng":22.9,  "z":8, "l":"Thessalonica, Greece"},
    {"k":["peace of westphalia"],           "lat":51.9,  "lng":7.6,   "z":8, "l":"Westphalia, Germany"},
    {"k":["congress of vienna"],            "lat":48.2,  "lng":16.4,  "z":8, "l":"Vienna, Austria"},
    {"k":["treaty of versailles"],          "lat":48.8,  "lng":2.1,   "z":8, "l":"Versailles, France"},
    # ── Specific people / places ──
    {"k":["large language model","artificial intelligence","chatgpt","machine learning","neural network"], "lat":20.0,"lng":0.0,"z":2,"l":"The Modern World"},
    {"k":["wittenberg","95 theses","luther nailed"], "lat":51.9,"lng":12.6,"z":9,"l":"Wittenberg, Germany"},
    {"k":["calvin","reformed church in geneva"], "lat":46.2,"lng":6.1,"z":8,"l":"Geneva, Switzerland"},
    {"k":["polycarp of smyrna"],            "lat":38.4,  "lng":27.1,  "z":8, "l":"Smyrna (Izmir), Turkey"},
    {"k":["irenaeus of lyon"],              "lat":45.7,  "lng":4.8,   "z":8, "l":"Lyon, France"},
    {"k":["paul of tarsus","born in tarsus"], "lat":36.9,"lng":34.9,  "z":8, "l":"Tarsus, Turkey"},
    {"k":["augustine of hippo","bishop of hippo"], "lat":36.9,"lng":7.8,"z":8,"l":"Hippo Regius (Annaba), Algeria"},
    {"k":["ambrose, bishop of milan","bishop of milan"], "lat":45.5,"lng":9.2,"z":8,"l":"Milan, Italy"},
    {"k":["athanasius of alexandria","origen of alexandria","hypatia"], "lat":31.2,"lng":29.9,"z":8,"l":"Alexandria, Egypt"},
    {"k":["medici bank","medici family","cosimo de' medici","lorenzo de' medici"], "lat":43.8,"lng":11.2,"z":8,"l":"Florence, Italy"},
    {"k":["sistine chapel","michelangelo painted"], "lat":41.9,"lng":12.5,"z":9,"l":"Vatican City, Rome"},
    {"k":["john locke","locke argued"],     "lat":51.5,  "lng":-0.1,  "z":7, "l":"England (John Locke)"},
    {"k":["adam smith","wealth of nations","david hume","scottish enlightenment"], "lat":55.9,"lng":-3.2,"z":7,"l":"Edinburgh, Scotland"},
    {"k":["justinian code","corpus juris civilis","justinian i","justinian's"], "lat":41.0,"lng":28.9,"z":7,"l":"Constantinople (Istanbul), Turkey"},
    # ── Specific cities ──
    {"k":["constantinople","istanbul"],     "lat":41.0,  "lng":28.9,  "z":8, "l":"Constantinople (Istanbul), Turkey"},
    {"k":["baghdad"],                       "lat":33.3,  "lng":44.4,  "z":8, "l":"Baghdad, Iraq"},
    {"k":["mecca"],                         "lat":21.4,  "lng":39.8,  "z":8, "l":"Mecca, Saudi Arabia"},
    {"k":["medina"],                        "lat":24.5,  "lng":39.6,  "z":8, "l":"Medina, Saudi Arabia"},
    {"k":["jerusalem"],                     "lat":31.8,  "lng":35.2,  "z":9, "l":"Jerusalem"},
    {"k":["library of alexandria","serapeum"], "lat":31.2,"lng":29.9, "z":8, "l":"Alexandria, Egypt"},
    {"k":["carthage"],                      "lat":36.9,  "lng":10.3,  "z":8, "l":"Carthage (near Tunis), Tunisia"},
    {"k":["cordoba, spain","cordoba,","al-andalus under"],  "lat":37.9,"lng":-4.8,"z":8,"l":"Cordoba, Spain"},
    {"k":["granada, spain","emirate of granada"], "lat":37.2,"lng":-3.6,"z":8,"l":"Granada, Spain"},
    {"k":["toledo, spain"],                 "lat":39.9,  "lng":-4.0,  "z":8, "l":"Toledo, Spain"},
    {"k":["florence"],                      "lat":43.8,  "lng":11.2,  "z":8, "l":"Florence, Italy"},
    {"k":["venice"],                        "lat":45.4,  "lng":12.3,  "z":8, "l":"Venice, Italy"},
    {"k":["naples"],                        "lat":40.8,  "lng":14.3,  "z":8, "l":"Naples, Italy"},
    {"k":["sicily"],                        "lat":37.6,  "lng":14.0,  "z":7, "l":"Sicily, Italy"},
    {"k":["vienna"],                        "lat":48.2,  "lng":16.4,  "z":8, "l":"Vienna, Austria"},
    {"k":["moscow"],                        "lat":55.8,  "lng":37.6,  "z":8, "l":"Moscow, Russia"},
    {"k":["st. petersburg","leningrad"],    "lat":59.9,  "lng":30.3,  "z":8, "l":"St. Petersburg, Russia"},
    {"k":["kyiv","kiev"],                   "lat":50.5,  "lng":30.5,  "z":8, "l":"Kyiv, Ukraine"},
    {"k":["athens"],                        "lat":37.9,  "lng":23.7,  "z":8, "l":"Athens, Greece"},
    {"k":["sparta"],                        "lat":37.1,  "lng":22.4,  "z":8, "l":"Sparta, Greece"},
    {"k":["babylon"],                       "lat":32.5,  "lng":44.4,  "z":8, "l":"Babylon (near Hillah), Iraq"},
    {"k":["nineveh"],                       "lat":36.4,  "lng":43.2,  "z":7, "l":"Nineveh (Mosul), Iraq"},
    {"k":["persepolis"],                    "lat":29.9,  "lng":52.9,  "z":8, "l":"Persepolis, Iran"},
    {"k":["timbuktu"],                      "lat":16.8,  "lng":-3.0,  "z":8, "l":"Timbuktu, Mali"},
    {"k":["tenochtitlan"],                  "lat":19.4,  "lng":-99.1, "z":8, "l":"Tenochtitlan (Mexico City), Mexico"},
    {"k":["cusco","cuzco"],                 "lat":-13.5, "lng":-72.0, "z":7, "l":"Cusco, Peru"},
    {"k":["delhi"],                         "lat":28.6,  "lng":77.2,  "z":8, "l":"Delhi, India"},
    {"k":["university of oxford","oxford university"], "lat":51.8,"lng":-1.3,"z":9,"l":"Oxford, England"},
    {"k":["university of bologna"],         "lat":44.5,  "lng":11.3,  "z":9, "l":"Bologna, Italy"},
    {"k":["canterbury"],                    "lat":51.3,  "lng":1.1,   "z":9, "l":"Canterbury, England"},
    {"k":["antioch"],                       "lat":36.2,  "lng":36.2,  "z":8, "l":"Antioch (Antakya), Turkey"},
    {"k":["ephesus"],                       "lat":37.9,  "lng":27.3,  "z":8, "l":"Ephesus, Turkey"},
    {"k":["nazareth"],                      "lat":32.7,  "lng":35.3,  "z":9, "l":"Nazareth, Israel"},
    {"k":["sea of galilee","galilee"],      "lat":32.9,  "lng":35.5,  "z":8, "l":"Sea of Galilee, Israel"},
    {"k":["sinai peninsula","mount sinai"], "lat":28.5,  "lng":33.9,  "z":7, "l":"Sinai Peninsula, Egypt"},
    {"k":["new york city","new york,","manhattan","wall street","harlem"], "lat":40.7,"lng":-74.0,"z":9,"l":"New York City"},
    {"k":["washington, d.c.","washington d.c","white house","capitol hill"], "lat":38.9,"lng":-77.0,"z":9,"l":"Washington D.C."},
    {"k":["philadelphia"],                  "lat":39.9,  "lng":-75.2, "z":9, "l":"Philadelphia, Pennsylvania"},
    {"k":["boston"],                        "lat":42.4,  "lng":-71.1, "z":9, "l":"Boston, Massachusetts"},
    {"k":["jamestown"],                     "lat":37.2,  "lng":-76.8, "z":9, "l":"Jamestown, Virginia"},
    {"k":["plymouth colony"],               "lat":41.9,  "lng":-70.7, "z":9, "l":"Plymouth, Massachusetts"},
    # ── Broader regions ──
    {"k":["mesopotamia","sumer","sumerian","gilgamesh","cuneiform","akkad"], "lat":33.0,"lng":44.0,"z":5,"l":"Mesopotamia (modern Iraq)"},
    {"k":["egypt","egyptian","nile","pharaoh","ptolemy","osiris","ramesses"], "lat":26.8,"lng":30.8,"z":5,"l":"Egypt"},
    {"k":["persia","persian empire","sassanid","achaemenid","zoroastrian","parthian","cyrus the great","darius the"], "lat":32.4,"lng":53.7,"z":5,"l":"Persia (modern Iran)"},
    {"k":["arabian peninsula","hijra","islam spread","arab conquest","umayyad","abbasid caliphate","quran was compiled"], "lat":24.0,"lng":45.0,"z":5,"l":"Arabian Peninsula"},
    {"k":["ottoman empire","ottoman sultan","ottoman forces","suleiman","mehmed ii"], "lat":39.0,"lng":35.0,"z":5,"l":"Ottoman Empire (modern Turkey)"},
    {"k":["byzantine empire","byzantine emperor","byzantine forces"], "lat":41.0,"lng":29.0,"z":5,"l":"Byzantine Empire"},
    {"k":["roman empire","pax romana","roman roads","roman citizenship","roman province"], "lat":41.9,"lng":12.5,"z":4,"l":"The Roman Empire"},
    {"k":["rome,","in rome","of rome","sacked rome","emperor nero","emperor augustus","imperial rome","roman senate"], "lat":41.9,"lng":12.5,"z":7,"l":"Rome, Italy"},
    {"k":["judea","judah","israel","hebrew bible","jewish revolt","jewish war","jewish community","jewish leader","maccab","hasmonean","zealot","pharisee","essene","bar kokhba"], "lat":31.8,"lng":35.2,"z":6,"l":"Judea / Israel"},
    {"k":["greece","greek philosophy","helleni","macedon","alexander the great","neoplatonism","plotinus","proclus"], "lat":38.0,"lng":23.7,"z":6,"l":"Greece"},
    {"k":["syria","palmyra","zenobia","damascus","levant"], "lat":35.0,"lng":38.0,"z":6,"l":"Syria"},
    {"k":["north africa","numidia","vandal kingdom"], "lat":33.0,"lng":9.0,"z":5,"l":"North Africa"},
    {"k":["charlemagne","carolingian","frankish kingdom","merovingian","clovis"], "lat":46.6,"lng":2.2,"z":5,"l":"Frankish Kingdom (modern France)"},
    {"k":["france","french revolution","paris,","napoleon,","bourbon"], "lat":46.2,"lng":2.2,"z":5,"l":"France"},
    {"k":["england","britain","british empire","london,","anglo-saxon","tudor","plantagenet","parliament of"], "lat":52.0,"lng":-1.5,"z":6,"l":"England / Britain"},
    {"k":["germany","holy roman empire","german states","prussia","bismarck","german unification"], "lat":51.2,"lng":10.5,"z":5,"l":"Germany"},
    {"k":["spain","iberian","reconquista","al-andalus","castile","aragon","spanish inquisition","spanish armada"], "lat":40.4,"lng":-3.7,"z":5,"l":"Spain"},
    {"k":["italy","italian city","papal states","the papacy","the pope","renaissance italy"], "lat":42.5,"lng":12.5,"z":5,"l":"Italy"},
    {"k":["scandinavia","viking age","viking raid","norse","norway","sweden","denmark","iceland","leif eriksson"], "lat":62.0,"lng":15.0,"z":4,"l":"Scandinavia"},
    {"k":["ireland","irish monk","irish monastery","saint patrick","columba"], "lat":53.4,"lng":-8.2,"z":6,"l":"Ireland"},
    {"k":["russia","soviet union","ussr","bolshevik","tsar nicholas","romanov dynasty","russian revolution"], "lat":55.8,"lng":37.6,"z":4,"l":"Russia"},
    {"k":["china","chinese empire","ming dynasty","qing dynasty","tang dynasty","song dynasty","han dynasty","yuan dynasty"], "lat":35.9,"lng":104.2,"z":4,"l":"China"},
    {"k":["japan","japanese empire","edo period","meiji restoration","tokugawa","samurai","shogunate"], "lat":36.2,"lng":138.3,"z":5,"l":"Japan"},
    {"k":["india","mughal empire","british raj","indian subcontinent","hinduism","buddhism in india"], "lat":20.6,"lng":79.0,"z":4,"l":"India"},
    {"k":["africa","west africa","sub-saharan","mali empire","songhai empire","rwanda","south africa","apartheid"], "lat":8.0,"lng":21.0,"z":4,"l":"Africa"},
    {"k":["mongol empire","mongol conquest","mongol invasion","genghis khan","kublai khan"], "lat":47.9,"lng":106.9,"z":4,"l":"Mongolia"},
    {"k":["united states","american civil war","american revolution","american independence","american colony","american president"], "lat":38.9,"lng":-95.7,"z":4,"l":"United States"},
    {"k":["mexico","aztec empire","maya","spanish conquest of"], "lat":19.4,"lng":-99.1,"z":5,"l":"Mexico"},
    {"k":["peru","inca empire"],            "lat":-13.5,"lng":-72.0,"z":5,"l":"Peru"},
    {"k":["brazil"],                        "lat":-14.2,"lng":-51.9,"z":4,"l":"Brazil"},
    {"k":["caribbean","cuba,","haiti,","saint-domingue"], "lat":19.0,"lng":-72.0,"z":5,"l":"Caribbean"},
    {"k":["netherlands","dutch east india","dutch republic","amsterdam,"], "lat":52.4,"lng":4.9,"z":7,"l":"Netherlands"},
    {"k":["portugal","portuguese empire","vasco da gama","prince henry"], "lat":39.4,"lng":-8.2,"z":6,"l":"Portugal"},
    {"k":["central asia","silk road","samarkand","timur","tamerlane"], "lat":41.3,"lng":64.6,"z":5,"l":"Central Asia"},
    {"k":["the balkans","balkan","serbia","hungary","bohemia","visigoth","ostrogoth"], "lat":45.0,"lng":18.0,"z":5,"l":"The Balkans"},
    {"k":["age of exploration","circumnavigation","columbus","magellan","drake,","cook,"], "lat":10.0,"lng":-30.0,"z":3,"l":"Age of Exploration"},
    {"k":["early christian","christian community","christian church","new testament","old testament","the gospels","gospel of mark","gospel of matthew","gospel of john","gospel of thomas","bart ehrman","misquoting jesus","textual criticism","biblical manuscript","biblical canon"], "lat":35.0,"lng":25.0,"z":4,"l":"The Early Christian World"},
    {"k":["world war ii","second world war","nazi germany","the holocaust","third reich","nuremberg trials"], "lat":50.0,"lng":14.0,"z":4,"l":"World War II Europe"},
    {"k":["world war i","first world war","western front","the somme","verdun","assassination of archduke"], "lat":49.0,"lng":3.0,"z":5,"l":"World War I — Western Front"},
    {"k":["cold war","iron curtain","nato alliance","warsaw pact","nuclear arms"], "lat":52.0,"lng":20.0,"z":3,"l":"Cold War Europe"},
    {"k":["industrial revolution","steam engine","factory system","textile mill","spinning jenny","power loom"], "lat":52.5,"lng":-1.9,"z":6,"l":"Industrial Revolution — England"},
    {"k":["french revolution","reign of terror","robespierre","storming of the bastille"], "lat":48.9,"lng":2.3,"z":7,"l":"Paris, France"},
    {"k":["internet","world wide web","social media","covid-19","climate change","paris agreement","global pandemic"], "lat":20.0,"lng":0.0,"z":2,"l":"The Modern World"},
]

def zoom_to_delta(z):
    return {2:60,3:35,4:22,5:12,6:6,7:3,8:1.5,9:0.7,10:0.35}.get(z, 8)

def make_map(r):
    d = zoom_to_delta(r["z"])
    lat, lng = r["lat"], r["lng"]
    bbox = f"{lng-d},{lat-d},{lng+d},{lat+d}"
    return {
        "map_label": r["l"],
        "map_iframe": f"https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={lat},{lng}"
    }

def get_region(fact):
    lower = fact.lower()
    for r in REGIONS:
        for k in r["k"]:
            if k in lower:
                return r
    return {"lat":35.0,"lng":20.0,"z":3,"l":"The Mediterranean & Ancient World"}

with open(CONTENT_PATH) as f:
    data = json.load(f)

for c in data['centuries']:
    if c.get('era') == 'Revolutionary Era (1776–1900)':
        c['era'] = 'Industrial Age (1800–1900)'

total = 0
for century in data['centuries']:
    for fact in century['facts']:
        r = get_region(fact['fact'])
        maps = make_map(r)
        fact['map_label'] = maps['map_label']
        fact['map_iframe'] = maps['map_iframe']
        total += 1

with open(CONTENT_PATH, 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Remapped {total} facts across {len(data['centuries'])} centuries")