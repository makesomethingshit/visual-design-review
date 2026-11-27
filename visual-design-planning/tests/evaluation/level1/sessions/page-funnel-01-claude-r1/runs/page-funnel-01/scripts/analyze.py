import csv, sys, collections
m = sys.argv[1]
rows = list(csv.DictReader(open(m+'/amplitude_funnel_2025-05_2025-10.csv')))
d = collections.defaultdict(int)
for r in rows: d[(r['month'],r['channel'],r['step'])] = int(r['users'])
months = sorted({r['month'] for r in rows}); chans=['organic_search','paid_social','referral','content_blog']; steps=['signup','first_book','trial_end','subscribe']
print("rows",len(rows))
def rat(a,b): return f"{a/b*100:.1f}%"
print("== total by step (6mo sum, NOT unique users)")
tot={s:sum(d[(mo,c,s)] for mo in months for c in chans) for s in steps}
print(tot, "sub/signup",rat(tot['subscribe'],tot['signup']), "fb/su",rat(tot['first_book'],tot['signup']),"te/fb",rat(tot['trial_end'],tot['first_book']),"sub/te",rat(tot['subscribe'],tot['trial_end']))
print("== by channel")
for c in chans:
    t={s:sum(d[(mo,c,s)] for mo in months) for s in steps}
    print(c,t,"fb/su",rat(t['first_book'],t['signup']),"te/fb",rat(t['trial_end'],t['first_book']),"sub/te",rat(t['subscribe'],t['trial_end']),"sub/su",rat(t['subscribe'],t['signup']), "share_signup",rat(t['signup'],tot['signup']),"share_sub",rat(t['subscribe'],tot['subscribe']))
print("== by month")
for mo in months:
    t={s:sum(d[(mo,c,s)] for c in chans) for s in steps}
    print(mo,t,"fb/su",rat(t['first_book'],t['signup']),"te/fb",rat(t['trial_end'],t['first_book']),"sub/te",rat(t['subscribe'],t['trial_end']),"sub/su",rat(t['subscribe'],t['signup']))
print("== month x channel sub/su, te/fb")
for c in chans:
    print(c,[ (mo[5:], rat(d[(mo,c,'subscribe')],d[(mo,c,'signup')]), rat(d[(mo,c,'trial_end')],d[(mo,c,'first_book')])) for mo in months])
# tickets
t = list(csv.DictReader(open(m+'/support_tickets_sample.csv')))
print("tickets",len(t))
print(collections.Counter(r['category'] for r in t))
print(collections.Counter(r['screen'] for r in t))
print(collections.Counter(r['channel'] for r in t))
bc=collections.Counter(r['body_excerpt'] for r in t)
print("unique bodies",len(bc)); 
for b,n in bc.most_common(): print(n,b,[r['ticket_id'] for r in t if r['body_excerpt']==b])
# id order vs date
prev=None
for r in t:
    pass
s = list(csv.DictReader(open(m+'/survey_responses_sample.csv')))
print("survey",len(s))
print("dates out of 03-02..03-20:",[ (r['respondent_id'],r['submitted_at'][:10]) for r in s if not ('2025-03-02'<=r['submitted_at'][:10]<='2025-03-20')])
for q in ['plan','Q1','Q2','Q3','Q4','Q5','Q6','Q7','Q8']:
    print(q, collections.Counter(r[q] if r[q] else '(무응답)' for r in s))
print("Q4==Q3-1:",sum(int(r['Q4'])==int(r['Q3'])-1 for r in s),"/",len(s))
print("plan x Q2:",collections.Counter((r['plan'],r['Q2']) for r in s))
print("plan x Q7:",collections.Counter((r['plan'],r['Q7']) for r in s))
print("plan x Q8:",collections.Counter((r['plan'],r['Q8'] or '-') for r in s))
for p in ['무료','체험 종료','월 구독','연 구독']:
    g=[r for r in s if r['plan']==p]
    print(p,len(g),"Q5 mean",sum(int(r['Q5']) for r in g)/len(g),"Q3 mean",sum(int(r['Q3']) for r in g)/len(g),"Q4 mean",sum(int(r['Q4']) for r in g)/len(g),"Q6",collections.Counter(r['Q6'] or '-' for r in g))
ns=[r for r in s if r['plan'] in ('무료','체험 종료')]
print("nonsub Q6",collections.Counter(r['Q6'] or '-' for r in ns), len(ns))
print("Q5>=4 all:",sum(int(r['Q5'])>=4 for r in s))
