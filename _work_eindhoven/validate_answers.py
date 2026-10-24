import json, glob, sys

srcs = {s['source_id'].split(':')[-1] for s in json.load(open('data_sources.json', encoding='utf-8'))}
topics = {t['slug'] for t in json.load(open('data_topics.json', encoding='utf-8'))}
ALLOWED_STAGES = {'before', 'planning', 'new', 'settled'}
REQUIRED = ['slug', 'topic', 'title', 'subtitle', 'summary', 'keywords', 'stages', 'sources', 'steps']
total = 0
problems = []
for f in sorted(glob.glob('answers_t*.json')):
    try:
        data = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        problems.append((f, 'JSON', str(e)))
        continue
    slugs = set()
    for a in data:
        total += 1
        for k in REQUIRED:
            if k not in a:
                problems.append((f, a.get('slug', '?'), 'missing ' + k))
        if a['slug'] in slugs:
            problems.append((f, a['slug'], 'duplicate slug'))
        slugs.add(a['slug'])
        if a['topic'] not in topics:
            problems.append((f, a['slug'], 'bad topic ' + a['topic']))
        st = set(x.strip() for x in a['stages'].split(';') if x.strip())
        if not st or not st <= ALLOWED_STAGES:
            problems.append((f, a['slug'], 'bad stages: ' + a['stages']))
        for s in a['sources']:
            if s not in srcs:
                problems.append((f, a['slug'], 'unknown source: ' + s))
        if not isinstance(a['steps'], list) or len(a['steps']) < 2:
            problems.append((f, a['slug'], 'steps too few'))
        for key in ['documents', 'timing', 'cost', 'note']:
            if key in a and not isinstance(a[key], (str, list)):
                problems.append((f, a['slug'], 'bad type ' + key))
print('total answers:', total)
print('problems:', len(problems))
for p in problems:
    print(' ', p)
