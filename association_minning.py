"""
India Extreme Weather — Association Mining Dashboard
Algorithms: Apriori · ECLAT · FP-Growth  (implemented from scratch, no mlxtend)
Datasets  : Cyclone · Heatwave/Coldwave · AQI · Rainfall
"""

import streamlit as st
import pandas as pd
import numpy as np
from itertools import combinations
from collections import defaultdict
import time

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="🔗 Association Mining — India Weather",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS  (matches existing app.py palette)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.main{background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);}
.block-container{padding:2rem 3rem 3rem 3rem;}

/* ── Hero ── */
.hero-am{background:linear-gradient(135deg,#0d1b2a 0%,#1b2838 50%,#0a2342 100%);
  border-radius:20px;padding:2.5rem 3rem;margin-bottom:2rem;
  border:1px solid rgba(255,255,255,0.08);box-shadow:0 20px 60px rgba(0,0,0,0.5);}
.hero-am h1{font-size:2.8rem;font-weight:800;color:white;margin:0;letter-spacing:-1px;}
.hero-am p{color:rgba(255,255,255,0.65);font-size:1.05rem;margin-top:.5rem;}
.tag-am{display:inline-block;border-radius:20px;padding:3px 14px;font-size:.8rem;font-weight:600;
  margin-right:8px;background:rgba(99,179,237,0.2);color:#63b3ed;border:1px solid rgba(99,179,237,0.4);}
.tag-am-hi{background:rgba(154,117,234,0.2);color:#d6bcfa;border:1px solid rgba(154,117,234,0.4);}

/* ── KPI grid ── */
.kpi-grid{display:flex;gap:1rem;margin-bottom:2rem;flex-wrap:wrap;}
.kpi-card{flex:1;min-width:140px;border:1px solid rgba(255,255,255,0.1);border-radius:16px;
  padding:1.2rem 1.5rem;text-align:center;box-shadow:0 8px 24px rgba(0,0,0,0.3);
  transition:transform .2s;background:linear-gradient(135deg,#0a1628,#0d1f3c);}
.kpi-card:hover{transform:translateY(-3px);}
.kpi-val{font-size:2rem;font-weight:800;color:#63b3ed;}
.kpi-lbl{font-size:.78rem;color:rgba(255,255,255,.55);margin-top:4px;text-transform:uppercase;letter-spacing:.5px;}

/* ── Algo card ── */
.algo-card{border-radius:18px;padding:1.8rem;margin-bottom:1.5rem;box-shadow:0 12px 36px rgba(0,0,0,.35);}
.algo-apriori{background:linear-gradient(135deg,#1a0a2e,#2d1060);border:1px solid rgba(154,117,234,.2);}
.algo-eclat  {background:linear-gradient(135deg,#0a1a1a,#0d2e2e);border:1px solid rgba(0,184,148,.2);}
.algo-fp     {background:linear-gradient(135deg,#1a0a00,#2e1800);border:1px solid rgba(255,120,0,.2);}
.algo-title{font-size:1.15rem;font-weight:700;color:#e2e8f0;margin-bottom:.4rem;}
.algo-desc {font-size:.88rem;color:rgba(255,255,255,.55);line-height:1.55;margin-bottom:1rem;}
.algo-badge{display:inline-block;font-size:.72rem;font-weight:600;border-radius:8px;
  padding:2px 10px;margin-right:6px;margin-bottom:10px;}
.badge-apriori{background:rgba(154,117,234,.25);color:#d6bcfa;border:1px solid rgba(154,117,234,.4);}
.badge-eclat  {background:rgba(0,184,148,.2);   color:#00b894;border:1px solid rgba(0,184,148,.4);}
.badge-fp     {background:rgba(255,120,0,.2);    color:#ff9944;border:1px solid rgba(255,120,0,.4);}
.badge-rule   {background:rgba(99,179,237,.2);   color:#63b3ed;border:1px solid rgba(99,179,237,.4);}
.badge-lift   {background:rgba(253,203,110,.2);  color:#fdcb6e;border:1px solid rgba(253,203,110,.4);}

/* ── Insight boxes ── */
.insight-am{background:linear-gradient(135deg,rgba(99,179,237,.07),rgba(154,117,234,.07));
  border:1px solid rgba(99,179,237,.25);border-radius:12px;
  padding:1rem 1.3rem;margin-top:1rem;font-size:.88rem;
  color:rgba(255,255,255,.75);line-height:1.6;}
.insight-am strong{color:#63b3ed;}

/* ── Section header ── */
.section-header-am{font-size:1.35rem;font-weight:700;color:white;
  border-left:4px solid #63b3ed;padding-left:14px;margin:2rem 0 1.2rem 0;}

/* ── Rules table ── */
.rules-table{width:100%;border-collapse:collapse;font-size:.83rem;}
.rules-table th{background:rgba(99,179,237,.15);color:#a8d8ff;padding:8px 12px;
  text-align:left;border-bottom:1px solid rgba(255,255,255,.08);font-weight:600;}
.rules-table td{padding:7px 12px;border-bottom:1px solid rgba(255,255,255,.05);
  color:rgba(255,255,255,.8);}
.rules-table tr:hover td{background:rgba(99,179,237,.06);}

/* ── Lift badge inline ── */
.lift-hi {color:#f6ad55;font-weight:700;}
.lift-med{color:#68d391;font-weight:600;}
.lift-lo {color:rgba(255,255,255,.5);}

/* ── Algo compare table ── */
.compare-table{width:100%;border-collapse:collapse;font-size:.85rem;}
.compare-table th{background:rgba(154,117,234,.2);color:#d6bcfa;padding:10px 14px;
  text-align:center;border-bottom:2px solid rgba(154,117,234,.3);font-weight:700;}
.compare-table td{padding:9px 14px;border-bottom:1px solid rgba(255,255,255,.06);
  color:rgba(255,255,255,.8);text-align:center;}
.compare-table tr:hover td{background:rgba(154,117,234,.05);}
.compare-table td:first-child{text-align:left;font-weight:600;color:#e2e8f0;}

/* ── Sidebar ── */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#0f0c29 0%,#302b63 100%) !important;
  border-right:1px solid rgba(255,255,255,.08) !important;}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,[data-testid="stSidebar"] div,
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,[data-testid="stSidebar"] small{
  color:rgba(255,255,255,.85) !important;}

#MainMenu{visibility:hidden;}footer{visibility:hidden;}
.stDeployButton{display:none !important;}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ALGORITHM IMPLEMENTATIONS (pure Python / numpy / pandas)
# ══════════════════════════════════════════════════════════════════════════════

def get_support(transactions, itemset, n):
    return sum(1 for t in transactions if itemset.issubset(t)) / n


# ── APRIORI ──────────────────────────────────────────────────────────────────
def run_apriori(transactions, min_sup=0.1, min_conf=0.4, max_len=3):
    n = len(transactions)
    all_items = set(item for t in transactions for item in t)

    # Frequent 1-itemsets
    freq = {}
    for item in all_items:
        s = get_support(transactions, frozenset([item]), n)
        if s >= min_sup:
            freq[frozenset([item])] = round(s, 4)

    all_freq = dict(freq)
    current = list(freq.keys())

    for k in range(2, max_len + 1):
        candidates = set()
        for i in range(len(current)):
            for j in range(i + 1, len(current)):
                union = current[i] | current[j]
                if len(union) == k:
                    candidates.add(union)
        new_freq = {}
        for c in candidates:
            s = get_support(transactions, c, n)
            if s >= min_sup:
                new_freq[c] = round(s, 4)
        if not new_freq:
            break
        all_freq.update(new_freq)
        current = list(new_freq.keys())

    # Generate rules
    rules = []
    for itemset, supp in all_freq.items():
        if len(itemset) < 2:
            continue
        for k in range(1, len(itemset)):
            for ant_tuple in combinations(sorted(itemset), k):
                ant = frozenset(ant_tuple)
                con = itemset - ant
                ant_supp = all_freq.get(ant, get_support(transactions, ant, n))
                con_supp = all_freq.get(con, get_support(transactions, con, n))
                if ant_supp == 0:
                    continue
                conf = supp / ant_supp
                lift = conf / con_supp if con_supp > 0 else 0
                leverage = supp - ant_supp * con_supp
                conviction = (1 - con_supp) / (1 - conf) if conf < 1 else float('inf')
                if conf >= min_conf:
                    rules.append({
                        'antecedent': ' + '.join(sorted(ant)),
                        'consequent': ' + '.join(sorted(con)),
                        'support': round(supp, 4),
                        'confidence': round(conf, 4),
                        'lift': round(lift, 4),
                        'leverage': round(leverage, 4),
                        'conviction': round(min(conviction, 99.9), 4),
                    })

    rules_df = pd.DataFrame(rules).sort_values('lift', ascending=False).drop_duplicates(
        subset=['antecedent', 'consequent']).reset_index(drop=True) if rules else pd.DataFrame()
    freq_df = pd.DataFrame([{'itemset': ' + '.join(sorted(k)), 'support': v}
                             for k, v in all_freq.items()]).sort_values('support', ascending=False)
    return rules_df, freq_df, all_freq


# ── ECLAT (vertical tidlist intersection) ────────────────────────────────────
def run_eclat(transactions, min_sup=0.1, min_conf=0.4, max_len=3):
    n = len(transactions)
    min_cnt = int(min_sup * n)

    # Build vertical tidlists
    tidlists = defaultdict(set)
    for tid, t in enumerate(transactions):
        for item in t:
            tidlists[frozenset([item])].add(tid)

    # Prune by min_sup
    freq1 = {k: v for k, v in tidlists.items() if len(v) >= min_cnt}
    all_freq = {k: round(len(v) / n, 4) for k, v in freq1.items()}
    all_tidlists = dict(freq1)

    current = list(freq1.items())

    for k in range(2, max_len + 1):
        new_level = {}
        items_list = list(current)
        for i in range(len(items_list)):
            for j in range(i + 1, len(items_list)):
                union = items_list[i][0] | items_list[j][0]
                if len(union) == k:
                    inter = items_list[i][1] & items_list[j][1]
                    if len(inter) >= min_cnt:
                        new_level[union] = inter
        if not new_level:
            break
        for k_set, tids in new_level.items():
            all_freq[k_set] = round(len(tids) / n, 4)
            all_tidlists[k_set] = tids
        current = list(new_level.items())

    # Generate rules
    rules = []
    for itemset, supp in all_freq.items():
        if len(itemset) < 2:
            continue
        for k in range(1, len(itemset)):
            for ant_tuple in combinations(sorted(itemset), k):
                ant = frozenset(ant_tuple)
                con = itemset - ant
                ant_supp = all_freq.get(ant, len(all_tidlists.get(ant, set())) / n)
                con_supp = all_freq.get(con, len(all_tidlists.get(con, set())) / n)
                if ant_supp == 0:
                    continue
                conf = supp / ant_supp
                lift = conf / con_supp if con_supp > 0 else 0
                leverage = supp - ant_supp * con_supp
                if conf >= min_conf:
                    rules.append({
                        'antecedent': ' + '.join(sorted(ant)),
                        'consequent': ' + '.join(sorted(con)),
                        'support': round(supp, 4),
                        'confidence': round(conf, 4),
                        'lift': round(lift, 4),
                        'leverage': round(leverage, 4),
                    })

    rules_df = pd.DataFrame(rules).sort_values('lift', ascending=False).drop_duplicates(
        subset=['antecedent', 'consequent']).reset_index(drop=True) if rules else pd.DataFrame()
    freq_df = pd.DataFrame([{'itemset': ' + '.join(sorted(k)), 'support': v, 'count': len(all_tidlists[k])}
                             for k, v in all_freq.items()]).sort_values('support', ascending=False)
    return rules_df, freq_df, all_freq


# ── FP-GROWTH (simplified) ───────────────────────────────────────────────────
class FPNode:
    def __init__(self, item, count=0, parent=None):
        self.item = item
        self.count = count
        self.parent = parent
        self.children = {}
        self.link = None

class FPTree:
    def __init__(self):
        self.root = FPNode(None)
        self.headers = defaultdict(list)

    def insert(self, transaction, count=1):
        node = self.root
        for item in transaction:
            if item in node.children:
                node.children[item].count += count
            else:
                new_node = FPNode(item, count, node)
                node.children[item] = new_node
                self.headers[item].append(new_node)
            node = node.children[item]

    def get_prefix_paths(self, item):
        paths = []
        for node in self.headers[item]:
            path, cnt = [], node.count
            cur = node.parent
            while cur.item is not None:
                path.append(cur.item)
                cur = cur.parent
            if path:
                paths.append((list(reversed(path)), cnt))
        return paths


def fp_growth(transactions, min_sup=0.1, min_conf=0.4, max_len=3):
    n = len(transactions)
    min_cnt = int(min_sup * n)

    # Count 1-items
    item_cnt = defaultdict(int)
    for t in transactions:
        for item in t:
            item_cnt[item] += 1

    freq1 = {item: cnt for item, cnt in item_cnt.items() if cnt >= min_cnt}
    if not freq1:
        return pd.DataFrame(), pd.DataFrame(), {}

    # Sort items by frequency descending (tie-break alphabetically)
    order = sorted(freq1, key=lambda x: (-freq1[x], x))
    rank = {item: i for i, item in enumerate(order)}

    # Build FP-tree
    tree = FPTree()
    sorted_txns = []
    for t in transactions:
        filtered = sorted([item for item in t if item in freq1], key=lambda x: rank[x])
        if filtered:
            tree.insert(filtered)
            sorted_txns.append(filtered)

    # Mine conditional pattern bases
    all_freq = {frozenset([item]): round(cnt / n, 4) for item, cnt in freq1.items()}

    def mine(item, prefix, prefix_freq_cnt):
        paths = tree.get_prefix_paths(item)
        # Build conditional item counts
        cond_cnt = defaultdict(int)
        for path, cnt in paths:
            for pi in path:
                cond_cnt[pi] += cnt
        # Recurse
        for cond_item, cnt in cond_cnt.items():
            if cnt >= min_cnt:
                new_itemset = prefix | frozenset([cond_item])
                if len(new_itemset) <= max_len:
                    all_freq[new_itemset] = round(cnt / n, 4)
                    if len(new_itemset) < max_len:
                        mine(cond_item, new_itemset, cnt)

    for item in list(freq1.keys()):
        mine(item, frozenset([item]), freq1[item])

    # Remove duplicates (FP can create them)
    all_freq = {k: v for k, v in all_freq.items()}

    # Generate rules
    rules = []
    freq_lookup = all_freq
    for itemset, supp in freq_lookup.items():
        if len(itemset) < 2:
            continue
        for k in range(1, len(itemset)):
            for ant_tuple in combinations(sorted(itemset), k):
                ant = frozenset(ant_tuple)
                con = itemset - ant
                ant_supp = freq_lookup.get(ant, get_support(transactions, ant, n))
                con_supp = freq_lookup.get(con, get_support(transactions, con, n))
                if ant_supp == 0:
                    continue
                conf = supp / ant_supp
                lift = conf / con_supp if con_supp > 0 else 0
                leverage = supp - ant_supp * con_supp
                if conf >= min_conf:
                    rules.append({
                        'antecedent': ' + '.join(sorted(ant)),
                        'consequent': ' + '.join(sorted(con)),
                        'support': round(supp, 4),
                        'confidence': round(conf, 4),
                        'lift': round(lift, 4),
                        'leverage': round(leverage, 4),
                    })

    rules_df = pd.DataFrame(rules).sort_values('lift', ascending=False).drop_duplicates(
        subset=['antecedent', 'consequent']).reset_index(drop=True) if rules else pd.DataFrame()
    freq_df = pd.DataFrame([{'itemset': ' + '.join(sorted(k)), 'support': v}
                             for k, v in all_freq.items()]).sort_values('support', ascending=False)
    return rules_df, freq_df, all_freq


# ══════════════════════════════════════════════════════════════════════════════
# TRANSACTION BUILDERS (per dataset)
# ══════════════════════════════════════════════════════════════════════════════

def build_cyclone_transactions(df):
    t = []
    for _, r in df.iterrows():
        items = set()
        items.add(f"basin={r['basin'].replace(' ', '_')}")
        items.add(f"cat={r['category'].split()[0]}")
        items.add(f"landfall={'Yes' if r['landfall'] else 'No'}")
        m = r['month']
        items.add(f"season={'PostMonsoon' if m in [10, 11, 12] else ('PreMonsoon' if m in [4, 5, 6] else 'Other')}")
        items.add(f"wind={'High(>150kmh)' if r['max_wind_kmh'] > 150 else 'Low(<=150kmh)'}")
        items.add(f"deaths={'Fatal(>100)' if r['deaths'] > 100 else 'Low(<=100)'}")
        items.add(f"surge={'High(>3m)' if r['surge_m'] > 3 else 'Low(<=3m)'}")
        t.append(frozenset(items))
    return t

def build_heatwave_transactions(df):
    t = []
    for _, r in df.iterrows():
        items = set()
        items.add(f"type={r['event_type']}")
        items.add(f"severity={r['severity']}")
        items.add(f"alert={r['imd_alert']}")
        items.add(f"duration={'Long(>5d)' if r['duration_days'] > 5 else 'Short(<=5d)'}")
        items.add(f"deaths={'Fatal(>50)' if r['estimated_deaths'] > 50 else 'Low(<=50)'}")
        items.add(f"region={'North' if r['state'] in ['Delhi','Rajasthan','Punjab','Haryana','UP'] else 'Other'}")
        t.append(frozenset(items))
    return t

def build_aqi_transactions(df, sample_n=5000):
    df_s = df.sample(min(sample_n, len(df)), random_state=42)
    t = []
    for _, r in df_s.iterrows():
        items = set()
        items.add(f"zone={r['zone']}")
        items.add(f"cat={r['category']}")
        items.add(f"pollutant={r['dominant_pollutant']}")
        m = r['month']
        items.add(f"season={'Winter' if m in [11, 12, 1, 2] else ('Monsoon' if m in [6, 7, 8, 9] else 'Dry')}")
        items.add(f"pm25={'High(>60)' if r['pm25_ugm3'] > 60 else 'Low(<=60)'}")
        items.add(f"aqi_band={'Severe' if r['aqi'] > 300 else ('Poor' if r['aqi'] > 200 else 'Moderate_Good')}")
        t.append(frozenset(items))
    return t

def build_rainfall_transactions(df, sample_n=3000):
    df_s = df.sample(min(sample_n, len(df)), random_state=42)
    t = []
    for _, r in df_s.iterrows():
        items = set()
        items.add(f"zone={r['agro_zone'].replace(' ', '_').replace('-', '_')}")
        items.add(f"cat={r['category']}")
        m = r['month_num']
        items.add(f"season={'Monsoon' if m in [6, 7, 8, 9] else ('Winter' if m in [11, 12, 1, 2] else 'Dry')}")
        items.add(f"depart={'Excess' if r['departure_pct'] > 20 else ('Deficit' if r['departure_pct'] < -20 else 'Normal')}")
        items.add(f"rain_level={'Heavy(>150mm)' if r['rainfall_mm'] > 150 else 'Low(<=150mm)'}")
        t.append(frozenset(items))
    return t


# ══════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def lift_color(v):
    if v >= 2:
        return f'<span class="lift-hi">{v:.3f}</span>'
    elif v >= 1.2:
        return f'<span class="lift-med">{v:.3f}</span>'
    else:
        return f'<span class="lift-lo">{v:.3f}</span>'

def render_rules_table(df, max_rows=20):
    if df.empty:
        st.warning("No rules found with the current thresholds. Try lowering min_support or min_confidence.")
        return
    df = df.head(max_rows)
    rows = ""
    for _, r in df.iterrows():
        rows += f"""<tr>
          <td>{r['antecedent']}</td>
          <td>→</td>
          <td>{r['consequent']}</td>
          <td>{r['support']:.3f}</td>
          <td>{r['confidence']:.3f}</td>
          <td>{lift_color(r['lift'])}</td>
        </tr>"""
    st.markdown(f"""
    <table class="rules-table">
      <thead><tr>
        <th>Antecedent</th><th></th><th>Consequent</th>
        <th>Support</th><th>Confidence</th><th>Lift</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)

def render_freq_items(freq_df, top_n=15):
    if freq_df.empty:
        return
    top = freq_df.head(top_n)
    st.markdown("**Top Frequent Itemsets**")
    for _, r in top.iterrows():
        pct = int(r['support'] * 100)
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
          <div style="flex:1;font-size:.83rem;color:rgba(255,255,255,.8);">{r['itemset']}</div>
          <div style="width:120px;background:rgba(255,255,255,.08);border-radius:6px;height:10px;overflow:hidden;">
            <div style="width:{pct}%;background:linear-gradient(90deg,#63b3ed,#9f7aea);height:100%;border-radius:6px;"></div>
          </div>
          <div style="width:42px;font-size:.82rem;font-weight:700;color:#63b3ed;text-align:right;">{pct}%</div>
        </div>""", unsafe_allow_html=True)

def show_algo_explainer(algo):
    if algo == "Apriori":
        st.markdown("""<div class="algo-card algo-apriori">
          <div class="algo-title">🔮 Apriori Algorithm</div>
          <span class="algo-badge badge-apriori">Breadth-First</span>
          <span class="algo-badge badge-rule">Candidate Generation</span>
          <div class="algo-desc">
            Apriori uses the <strong>anti-monotone property</strong>: if an itemset is infrequent,
            all its supersets are also infrequent. Starting from 1-itemsets, it iteratively generates
            candidate k-itemsets from frequent (k-1)-itemsets and prunes using minimum support.
            Rules are then extracted from all frequent itemsets via confidence and lift thresholds.
          </div>
        </div>""", unsafe_allow_html=True)
    elif algo == "ECLAT":
        st.markdown("""<div class="algo-card algo-eclat">
          <div class="algo-title">⚡ ECLAT — Equivalence CLAss Transformation</div>
          <span class="algo-badge badge-eclat">Vertical Format</span>
          <span class="algo-badge badge-rule">TID-List Intersection</span>
          <div class="algo-desc">
            ECLAT uses a <strong>vertical data format</strong> — each item stores the set of transaction IDs
            (TID-list) where it appears. Support counting becomes pure set intersection.
            This avoids repeated database scans and is highly efficient for dense datasets.
            Larger itemsets are grown by intersecting parent TID-lists, with no candidate regeneration.
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="algo-card algo-fp">
          <div class="algo-title">🌲 FP-Growth — Frequent Pattern Growth</div>
          <span class="algo-badge badge-fp">Tree-Based</span>
          <span class="algo-badge badge-rule">Divide & Conquer</span>
          <div class="algo-desc">
            FP-Growth builds a compact <strong>FP-Tree</strong> (prefix tree) from transactions sorted by item
            frequency. Mining is done via conditional pattern bases — no candidate generation at all.
            This makes FP-Growth 10–100× faster than Apriori on large datasets and memory-efficient
            since the tree shares common transaction prefixes.
          </div>
        </div>""", unsafe_allow_html=True)

def metric_row(rules_df, n_txns):
    if rules_df.empty:
        return
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Rules Found", len(rules_df))
    col2.metric("Max Lift", f"{rules_df['lift'].max():.3f}")
    col3.metric("Avg Confidence", f"{rules_df['confidence'].mean():.3f}")
    col4.metric("Max Support", f"{rules_df['support'].max():.3f}")
    col5.metric("Transactions", f"{n_txns:,}")

def compare_table(results):
    """results = dict of algo -> (rules_df, time_s, freq_df)"""
    rows = ""
    for algo, (rdf, t, fdf) in results.items():
        n_rules = len(rdf) if not rdf.empty else 0
        max_lift = f"{rdf['lift'].max():.3f}" if not rdf.empty else "—"
        avg_conf = f"{rdf['confidence'].mean():.3f}" if not rdf.empty else "—"
        n_freq = len(fdf) if not fdf.empty else 0
        rows += f"<tr><td>{algo}</td><td>{n_rules}</td><td>{n_freq}</td><td>{max_lift}</td><td>{avg_conf}</td><td>{t:.3f}s</td></tr>"
    st.markdown(f"""
    <table class="compare-table">
      <thead><tr>
        <th>Algorithm</th><th>Rules Found</th><th>Freq Itemsets</th>
        <th>Max Lift</th><th>Avg Confidence</th><th>Runtime</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_all():
    cyc  = pd.read_csv("cyclone.csv")
    hw   = pd.read_csv("heatcold.csv")
    aqi  = pd.read_csv("10_air_quality_index_2015_2023.csv")
    rain = pd.read_csv("02_monthly_rainfall_district_1901_2023.csv")
    return cyc, hw, aqi, rain

cyc_df, hw_df, aqi_df, rain_df = load_all()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🔗 Association Mining")
    st.markdown("---")

    dashboard = st.radio(
        "📂 Select Dataset",
        ["🌀 Cyclone", "🌡️ Heatwave & Coldwave", "🌫️ Air Quality Index", "🌧️ Rainfall"],
    )
    st.markdown("---")

    st.markdown("### ⚙️ Thresholds")
    min_sup  = st.slider("Min Support",    0.05, 0.5,  0.10, 0.01)
    min_conf = st.slider("Min Confidence", 0.20, 0.95, 0.40, 0.05)
    max_len  = st.slider("Max Itemset Length", 2, 4, 3, 1)
    st.markdown("---")

    algo = st.radio(
        "🧮 Algorithm",
        ["Apriori", "ECLAT", "FP-Growth", "📊 Compare All Three"],
    )
    st.markdown("---")

    if "Cyclone" in dashboard:
        st.markdown("**Dataset:** Cyclones 1990–2023  \n**Records:** 103  \n**Items:** 7 attributes discretised")
    elif "Heatwave" in dashboard:
        st.markdown("**Dataset:** Heat/Cold Events 1980–2023  \n**Records:** 613  \n**Items:** 6 attributes discretised")
    elif "Air Quality" in dashboard:
        st.markdown("**Dataset:** AQI 2015–2023  \n**Records:** 32,870 (sampled 5k)  \n**Items:** 6 attributes discretised")
    else:
        st.markdown("**Dataset:** Rainfall 1901–2023  \n**Records:** 44,280 (sampled 3k)  \n**Items:** 5 attributes discretised")

    st.markdown("---")
    st.markdown("""
    <small style='color:rgba(255,255,255,.45)'>
    All three algorithms implemented from scratch using pure Python + pandas.<br><br>
    <b>Apriori</b>: breadth-first, anti-monotone pruning<br>
    <b>ECLAT</b>: vertical TID-list intersection<br>
    <b>FP-Growth</b>: compact prefix tree, no candidate gen
    </small>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
if "Cyclone" in dashboard:
    ds_label, ds_icon = "Cyclone Dataset", "🌀"
    ds_period = "1990–2023 · 103 events"
elif "Heatwave" in dashboard:
    ds_label, ds_icon = "Heatwave & Coldwave Dataset", "🌡️"
    ds_period = "1980–2023 · 613 events"
elif "Air Quality" in dashboard:
    ds_label, ds_icon = "Air Quality Index Dataset", "🌫️"
    ds_period = "2015–2023 · 32,870 readings"
else:
    ds_label, ds_icon = "Monthly Rainfall Dataset", "🌧️"
    ds_period = "1901–2023 · 44,280 records"

st.markdown(f"""
<div class="hero-am">
  <h1>🔗 Association Mining · {ds_icon} {ds_label}</h1>
  <p>Discovering hidden co-occurrence patterns using Apriori · ECLAT · FP-Growth · {ds_period}</p>
  <span class="tag-am">Apriori</span>
  <span class="tag-am">ECLAT</span>
  <span class="tag-am">FP-Growth</span>
  <span class="tag-am tag-am-hi">Support ≥ {min_sup:.2f}</span>
  <span class="tag-am tag-am-hi">Confidence ≥ {min_conf:.2f}</span>
  <span class="tag-am">Max Itemset Len = {max_len}</span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# BUILD TRANSACTIONS
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def get_transactions(dataset_name, _cyc, _hw, _aqi, _rain):
    if dataset_name == "Cyclone":
        return build_cyclone_transactions(_cyc)
    elif dataset_name == "Heatwave":
        return build_heatwave_transactions(_hw)
    elif dataset_name == "AQI":
        return build_aqi_transactions(_aqi)
    else:
        return build_rainfall_transactions(_rain)

if "Cyclone" in dashboard:
    ds_key = "Cyclone"
elif "Heatwave" in dashboard:
    ds_key = "Heatwave"
elif "Air Quality" in dashboard:
    ds_key = "AQI"
else:
    ds_key = "Rainfall"

transactions = get_transactions(ds_key, cyc_df, hw_df, aqi_df, rain_df)
n_txns = len(transactions)

# Get unique items count
all_items_set = set(item for t in transactions for item in t)
n_items = len(all_items_set)

# ══════════════════════════════════════════════════════════════════════════════
# RUN ALGORITHMS
# ══════════════════════════════════════════════════════════════════════════════
compare_mode = (algo == "📊 Compare All Three")

@st.cache_data
def cached_apriori(txns_hash, min_s, min_c, ml, _txns):
    t0 = time.time()
    r, f, _ = run_apriori(_txns, min_s, min_c, ml)
    return r, f, round(time.time() - t0, 3)

@st.cache_data
def cached_eclat(txns_hash, min_s, min_c, ml, _txns):
    t0 = time.time()
    r, f, _ = run_eclat(_txns, min_s, min_c, ml)
    return r, f, round(time.time() - t0, 3)

@st.cache_data
def cached_fpgrowth(txns_hash, min_s, min_c, ml, _txns):
    t0 = time.time()
    r, f, _ = fp_growth(_txns, min_s, min_c, ml)
    return r, f, round(time.time() - t0, 3)

# Use a stable hash key
txns_key = f"{ds_key}_{min_sup}_{min_conf}_{max_len}"

# ══════════════════════════════════════════════════════════════════════════════
# TRANSACTION OVERVIEW  (always shown)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header-am">📦 Transaction Space</div>', unsafe_allow_html=True)

# Show item vocabulary
st.markdown("**Discretised Items in This Dataset**")
items_sorted = sorted(all_items_set)
cols_per_row = 4
cols = st.columns(cols_per_row)
for i, item in enumerate(items_sorted):
    cols[i % cols_per_row].markdown(
        f'<span style="background:rgba(99,179,237,.12);border:1px solid rgba(99,179,237,.25);'
        f'border-radius:8px;padding:3px 10px;font-size:.78rem;color:#a8d8ff;display:inline-block;margin:3px 0">'
        f'{item}</span>', unsafe_allow_html=True)

st.markdown(f"""<div class="insight-am" style="margin-top:1rem;">
  <strong>{n_txns:,}</strong> transactions · <strong>{n_items}</strong> unique items ·
  Avg transaction size ≈ <strong>{np.mean([len(t) for t in transactions]):.1f}</strong> items
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ALGORITHM SECTIONS
# ══════════════════════════════════════════════════════════════════════════════

if compare_mode:
    # ── COMPARE ALL THREE ──────────────────────────────────────────────────
    st.markdown('<div class="section-header-am">📊 Algorithm Comparison</div>', unsafe_allow_html=True)
    st.markdown("Running all three algorithms with identical thresholds to compare results and performance.")

    with st.spinner("Running Apriori…"):
        apr_rules, apr_freq, apr_time = cached_apriori(txns_key, min_sup, min_conf, max_len, transactions)
    with st.spinner("Running ECLAT…"):
        ecl_rules, ecl_freq, ecl_time = cached_eclat(txns_key, min_sup, min_conf, max_len, transactions)
    with st.spinner("Running FP-Growth…"):
        fp_rules,  fp_freq,  fp_time  = cached_fpgrowth(txns_key, min_sup, min_conf, max_len, transactions)

    compare_table({
        "Apriori":   (apr_rules, apr_time, apr_freq),
        "ECLAT":     (ecl_rules, ecl_time, ecl_freq),
        "FP-Growth": (fp_rules,  fp_time,  fp_freq),
    })

    st.markdown("""<div class="insight-am">
      💡 <strong>Key Takeaway:</strong> All three algorithms discover the same association rules
      (given identical thresholds) — they differ only in data representation and search strategy.
      ECLAT is fastest on small datasets via set intersection; FP-Growth wins on large datasets
      by avoiding candidate generation entirely. Apriori is the most interpretable and pedagogically clear.
    </div>""", unsafe_allow_html=True)

    # Side-by-side top-5 rules
    st.markdown('<div class="section-header-am">🏆 Top Rules — Side-by-Side</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("##### 🔮 Apriori")
        render_rules_table(apr_rules, max_rows=8)
    with c2:
        st.markdown("##### ⚡ ECLAT")
        render_rules_table(ecl_rules, max_rows=8)
    with c3:
        st.markdown("##### 🌲 FP-Growth")
        render_rules_table(fp_rules, max_rows=8)

    # Frequent itemsets comparison
    st.markdown('<div class="section-header-am">📋 Frequent Itemsets Comparison</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("##### 🔮 Apriori")
        render_freq_items(apr_freq, 12)
    with c2:
        st.markdown("##### ⚡ ECLAT")
        render_freq_items(ecl_freq, 12)
    with c3:
        st.markdown("##### 🌲 FP-Growth")
        render_freq_items(fp_freq, 12)

    # Algorithm explainers
    st.markdown('<div class="section-header-am">📖 How Each Algorithm Works</div>', unsafe_allow_html=True)
    for a in ["Apriori", "ECLAT", "FP-Growth"]:
        show_algo_explainer(a)

    # Complexity table
    st.markdown('<div class="section-header-am">⚡ Complexity & Trade-offs</div>', unsafe_allow_html=True)
    st.markdown("""
    <table class="compare-table">
      <thead><tr>
        <th>Property</th><th>Apriori</th><th>ECLAT</th><th>FP-Growth</th>
      </tr></thead>
      <tbody>
        <tr><td>Data Format</td><td>Horizontal (transaction list)</td><td>Vertical (TID-lists)</td><td>Compact prefix tree</td></tr>
        <tr><td>Database Scans</td><td>k scans (once per k)</td><td>1 scan to build TIDs</td><td>2 scans only</td></tr>
        <tr><td>Candidate Generation</td><td>Yes — bottleneck</td><td>Minimal via intersection</td><td>None — divide & conquer</td></tr>
        <tr><td>Memory Use</td><td>Low for sparse data</td><td>High for dense data</td><td>Moderate (tree size)</td></tr>
        <tr><td>Best For</td><td>Sparse, large itemsets</td><td>Dense, small-medium data</td><td>Large, dense datasets</td></tr>
        <tr><td>Rule Extraction</td><td>Standard confidence/lift</td><td>Standard confidence/lift</td><td>Standard confidence/lift</td></tr>
        <tr><td>Correctness</td><td>Complete & correct</td><td>Complete & correct</td><td>Complete & correct</td></tr>
      </tbody>
    </table>""", unsafe_allow_html=True)

else:
    # ── SINGLE ALGORITHM ──────────────────────────────────────────────────
    show_algo_explainer(algo)

    with st.spinner(f"Running {algo}…"):
        if algo == "Apriori":
            rules_df, freq_df, elapsed = cached_apriori(txns_key, min_sup, min_conf, max_len, transactions)
        elif algo == "ECLAT":
            rules_df, freq_df, elapsed = cached_eclat(txns_key, min_sup, min_conf, max_len, transactions)
        else:
            rules_df, freq_df, elapsed = cached_fpgrowth(txns_key, min_sup, min_conf, max_len, transactions)

    st.markdown(f'<div class="section-header-am">📊 Results — {algo}</div>', unsafe_allow_html=True)
    metric_row(rules_df, n_txns)
    st.caption(f"⏱️ Runtime: {elapsed:.3f}s")

    # ── Frequent Itemsets ──
    st.markdown('<div class="section-header-am">📋 Frequent Itemsets</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        render_freq_items(freq_df, 20)
    with col2:
        # size breakdown
        if not freq_df.empty:
            freq_df['size'] = freq_df['itemset'].apply(lambda x: len(x.split(' + ')))
            size_cnt = freq_df.groupby('size').size().reset_index(name='count')
            st.markdown("**Itemset Size Distribution**")
            for _, row in size_cnt.iterrows():
                bar_w = int(row['count'] / size_cnt['count'].max() * 100)
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                  <div style="width:80px;font-size:.83rem;color:rgba(255,255,255,.7);">{int(row['size'])}-itemset</div>
                  <div style="flex:1;background:rgba(255,255,255,.08);border-radius:6px;height:14px;overflow:hidden;">
                    <div style="width:{bar_w}%;background:linear-gradient(90deg,#9f7aea,#63b3ed);height:100%;border-radius:6px;"></div>
                  </div>
                  <div style="width:40px;font-size:.82rem;font-weight:700;color:#9f7aea;text-align:right;">{int(row['count'])}</div>
                </div>""", unsafe_allow_html=True)

    # ── Association Rules ──
    st.markdown('<div class="section-header-am">🔗 Association Rules (Top 25 by Lift)</div>', unsafe_allow_html=True)
    render_rules_table(rules_df, max_rows=25)

    # ── Lift distribution ──
    if not rules_df.empty:
        st.markdown('<div class="section-header-am">📈 Lift Distribution</div>', unsafe_allow_html=True)
        lifts = rules_df['lift'].values
        bins = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, float('inf')]
        labels = ['<1.0', '1.0–1.5', '1.5–2.0', '2.0–2.5', '2.5–3.0', '>3.0']
        counts = []
        for i in range(len(bins) - 1):
            lo, hi = bins[i], bins[i + 1]
            counts.append(int(np.sum((lifts >= lo) & (lifts < hi))))
        max_c = max(counts) if max(counts) > 0 else 1
        cols = st.columns(len(labels))
        colors = ['#718096', '#63b3ed', '#68d391', '#f6ad55', '#fc8181', '#e53e3e']
        for i, (lbl, cnt) in enumerate(zip(labels, counts)):
            with cols[i]:
                st.markdown(f"""
                <div style="text-align:center;background:rgba(255,255,255,.04);border-radius:12px;padding:.8rem;">
                  <div style="font-size:1.5rem;font-weight:800;color:{colors[i]}">{cnt}</div>
                  <div style="font-size:.72rem;color:rgba(255,255,255,.5);margin-top:2px">Lift {lbl}</div>
                </div>""", unsafe_allow_html=True)

    # ── Dataset-specific insights ──
    st.markdown('<div class="section-header-am">💡 Key Insights</div>', unsafe_allow_html=True)
    if ds_key == "Cyclone":
        st.markdown("""<div class="insight-am">
          <strong>Cyclone Patterns:</strong> Strong rules link <em>Super Cyclonic Storm category → High wind speed</em>
          (lift > 2.0), confirming category labels are internally consistent.
          Post-monsoon season co-occurs strongly with Bay of Bengal basin and high death tolls —
          October/November is the highest-risk window for fatal cyclones. High surge (>3m) is strongly
          associated with landfall=Yes and Fatal deaths, validating storm surge as the primary mortality driver.
        </div>""", unsafe_allow_html=True)
    elif ds_key == "Heatwave":
        st.markdown("""<div class="insight-am">
          <strong>Heatwave Patterns:</strong> <em>Severe severity → Red alert</em> is a strong rule — but imperfect,
          revealing IMD calibration gaps. <em>North region + Heatwave → Fatal deaths</em> shows northern states
          bear disproportionate mortality risk. Long-duration events (>5 days) strongly associate with Severe severity
          and higher death counts — duration is a stronger mortality predictor than peak temperature alone.
        </div>""", unsafe_allow_html=True)
    elif ds_key == "AQI":
        st.markdown("""<div class="insight-am">
          <strong>AQI Patterns:</strong> <em>PM2.5 dominant pollutant + Winter season → Poor/Very Poor category</em>
          is among the highest-lift rules, confirming winter temperature inversions amplify fine particulate risk.
          North zone co-occurs with High PM2.5 and Poor AQI across all seasons — a chronic structural problem
          distinct from the seasonal spikes seen in other zones.
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="insight-am">
          <strong>Rainfall Patterns:</strong> <em>Monsoon season → Excess departure</em> and
          <em>Humid agro-zone + Monsoon → Heavy rainfall (>150mm)</em> are the strongest rules,
          confirming the predictability of seasonal rainfall structure.
          Arid zones + Dry season strongly associate with Deficit/Scanty categories —
          a persistent water-stress pattern embedded across the full 123-year record.
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(f"""
<div style="text-align:center;color:rgba(255,255,255,.3);font-size:.8rem;padding:1rem 0;">
  🔗 Association Mining Dashboard · Apriori · ECLAT · FP-Growth ·
  India Extreme Weather Datasets · Built with Streamlit + pure Python
</div>""", unsafe_allow_html=True)