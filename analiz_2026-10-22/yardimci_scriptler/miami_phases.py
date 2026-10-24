# Miami (Codex) phase table transcribed from Miami_Uretim_Sure_Token_Raporu_20261020.pdf pp.7-8
P = [  # name, seconds, input, noncached, output, reasoning, group
("00_setup",296,3071793,106929,5981,1689,"setup"),
("01_places_plan",87,241819,13467,3711,487,"places"),
("02_shared_research",118,361933,41293,5295,369,"content"),
("03_resmi",53,240895,16255,2488,239,"content"),
("04_ev",83,256528,9360,3982,45,"content"),
("05_fatura",90,419657,12873,3646,266,"content"),
("06_para",48,298658,7330,2092,58,"content"),
("07_saglik",68,310768,6256,3093,51,"content"),
("08_is",70,325175,7607,3299,109,"content"),
("09_aile",91,339922,7506,4199,55,"content"),
("10_ulasim",98,356766,8862,4497,202,"content"),
("11_gunluk",70,374157,8973,3168,158,"content"),
("12_haklar",72,388609,7297,3543,134,"content"),
("13_turkiye",62,403158,7382,2689,153,"content"),
("14_sosyal",88,415942,6854,3951,93,"content"),
("15_photo_review",774,3823890,186258,21101,6045,"photo"),
("16_page",34,448414,14878,1680,321,"content"),
("17_weather",6,231426,1666,153,86,"content"),
("18_journey",7,231656,360,183,0,"content"),
("19_budget",8,231916,364,312,0,"content"),
("20_glossary",47,466480,2480,2249,157,"content"),
("21_neighborhoods",93,432565,14517,3115,337,"places"),
("22_routes",51,180820,8404,2630,85,"places"),
("23_venues",66,401449,5801,2309,541,"places"),
("23b_parks",62,219888,2032,1988,459,"places"),
("23c_sports_stage",51,227932,8156,2591,34,"places"),
("23d_shopping_food",33,230665,2825,1789,151,"places"),
("23e_heritage",216,536466,24850,5434,113,"places"),
("24_media_final",158,1599707,62299,4858,476,"photo"),
("25_local_import",83,1051827,39091,2669,239,"mechanical"),
("27_content_qa",69,963011,27459,1882,186,"qa"),
("26_workbook",131,2589960,43784,4345,661,"mechanical"),
("28_drive",51,763153,10257,1116,282,"mechanical"),
("30_metrics_pdf",267,2564142,25774,11669,1865,"reporting"),
("29_panel",208,2157610,32554,2935,395,"mechanical"),
]
T_IN, T_NC, T_OUT, T_SEC = 27158757, 782053, 130642, 63*60+48
s = lambda k: sum(p[k] for p in P)
print("check sums: in", s(2), "vs", T_IN, "| nc", s(3), "vs", T_NC, "| out", s(4), "vs", T_OUT, "| sec", s(1), "vs", T_SEC)
from collections import defaultdict
g = defaultdict(lambda: [0,0,0,0,0])
for n,sec,i,nc,o,r,grp in P:
    a=g[grp]; a[0]+=sec; a[1]+=i; a[2]+=nc; a[3]+=o; a[4]+=1
# cost-equivalent (Claude ratios): cache read 0.1x, uncached input 1x, output 5x
def ceq(i,nc,o): return nc + 0.1*(i-nc) + 5*o
tot_ceq = ceq(T_IN,T_NC,T_OUT)
print(f"\nTOTAL cost-eq (Claude ratios) = {tot_ceq/1e6:.2f}M  (uncached {T_NC/1e6:.2f}M + cachedx0.1 {(T_IN-T_NC)*0.1/1e6:.2f}M + outx5 {T_OUT*5/1e6:.2f}M)")
print(f"\n{'group':12} {'phases':>6} {'min':>6} {'time%':>6} {'input':>11} {'in%':>6} {'noncach':>9} {'out':>8} {'out%':>6} {'cost-eq%':>8}")
for k,(sec,i,nc,o,n) in sorted(g.items(), key=lambda kv:-kv[1][1]):
    print(f"{k:12} {n:6} {sec/60:6.1f} {100*sec/T_SEC:6.1f} {i:11,} {100*i/T_IN:6.1f} {nc:9,} {o:8,} {100*o/T_OUT:6.1f} {100*ceq(i,nc,o)/tot_ceq:8.1f}")
# implied context per call: phases with tiny output ~ single call
print("\nsingle-call proxies (context size at that moment):")
for n,sec,i,nc,o,r,grp in P:
    if o < 400: print(f"  {n}: input {i:,} with output {o} -> ~{i/1000:.0f}K context")
print("\navg input per token event (177 events):", round(T_IN/177/1000), "K")
cards_in = sum(p[2] for p in P if p[0][:2] in [f"{x:02d}" for x in range(3,15)])
cards_out = sum(p[4] for p in P if p[0][:2] in [f"{x:02d}" for x in range(3,15)])
print(f"240 cards (03-14): input {cards_in:,}  output {cards_out:,}  -> {cards_out/240:.0f} out tok/card, {cards_in/240/1000:.1f}K in/card")
late = [p for p in P if p[0][:2] in ("24","25","26","27","28","29","30")]
print("late phases 24-30 input:", f"{sum(p[2] for p in late):,}", f"{100*sum(p[2] for p in late)/T_IN:.1f}%", "time", f"{sum(p[1] for p in late)/60:.1f} min")
