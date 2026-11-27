import csv,sys,collections
m=sys.argv[1]
rows=list(csv.DictReader(open(m+'/amplitude_funnel_2025-05_2025-10.csv')))
S=['signup','first_book','trial_end','subscribe']
agg=collections.defaultdict(int); bym=collections.defaultdict(int); bc=collections.defaultdict(int)
for r in rows:
    u=int(r['users']); agg[r['step']]+=u; bym[(r['month'],r['step'])]+=u; bc[(r['channel'],r['step'])]+=u
print('total',dict(agg))
for a,b in zip(S,S[1:]): print(a,'->',b, round(agg[b]/agg[a]*100,1))
print('sub/signup',round(agg['subscribe']/agg['signup']*100,2))
for mo in sorted(set(r['month'] for r in rows)):
    v=[bym[(mo,s)] for s in S]; print(mo,v,[round(v[i+1]/v[i]*100,1) for i in range(3)], round(v[3]/v[0]*100,1))
for ch in ['organic_search','paid_social','referral','content_blog']:
    v=[bc[(ch,s)] for s in S]; print(ch,v,[round(v[i+1]/v[i]*100,1) for i in range(3)], round(v[3]/v[0]*100,1), 'share signup',round(v[0]/agg['signup']*100,1))
# month x channel stability
for ch in ['organic_search','paid_social','referral','content_blog']:
    out=[]
    for mo in sorted(set(r['month'] for r in rows)):
        d={r['step']:int(r['users']) for r in rows if r['month']==mo and r['channel']==ch}
        out.append((mo,round(d['first_book']/d['signup']*100,1),round(d['trial_end']/d['first_book']*100,1),round(d['subscribe']/d['trial_end']*100,1)))
    print(ch,out)
# tickets
t=list(csv.DictReader(open(m+'/support_tickets_sample.csv')))
print(len(t), collections.Counter(x['category'] for x in t))
print(collections.Counter(x['screen'] for x in t))
print(collections.Counter(x['body_excerpt'] for x in t).most_common())
s=list(csv.DictReader(open(m+'/survey_responses_sample.csv')))
print(len(s), collections.Counter(x['plan'] for x in s))
for q in ['Q2','Q6','Q7','Q8']:
    print(q, collections.Counter(x[q] or '(무응답)' for x in s))
for q in ['Q1','Q3','Q4','Q5']:
    vals=[int(x[q]) for x in s]; print(q, round(sum(vals)/len(vals),2), collections.Counter(vals))
for p in ['무료','체험 종료','월 구독','연 구독']:
    g=[x for x in s if x['plan']==p]
    print(p,len(g),{q:round(sum(int(x[q]) for x in g)/len(g),2) for q in ['Q3','Q4','Q5']}, collections.Counter(x['Q6'] or '(무응답)' for x in g))
print('dates',min(x['submitted_at'] for x in s),max(x['submitted_at'] for x in s))
print('outside period',[x['respondent_id'] for x in s if not ('2025-03-02'<=x['submitted_at'][:10]<='2025-03-20')])
# Q2 vs plan crosstab
print(collections.Counter((x['Q2'],x['plan']) for x in s))
print(collections.Counter((x['Q2'],x['Q7']) for x in s))
