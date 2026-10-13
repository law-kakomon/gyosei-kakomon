#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""単元判定の下ごしらえ。

data/sources.json の PDF を取ってきてテキスト化し、対象科目の節だけ切り出して、
引用条文・判例・論点文を一覧にする。この出力を見ながら tools/classify.py を書く。

    python3 tools/digest.py            # 全件
    python3 tools/digest.py dos-2026-zenki kei-2025-honshi   # 指定した回だけ

PDF とテキストは .cache/ に置く（git 管理外）。リポジトリに PDF は入れない。
"""
import json, re, subprocess, sys, urllib.request, unicodedata as ud
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
CACHE = ROOT / '.cache'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'

import classify as C
SUBJECT = C.SUBJECT_NAME            # 試験科目名（節の切り出しに使う）
TARGET  = getattr(C, 'TARGET_LAW', C.SUBJECT_NAME)   # 条文を数える対象法令
AMAX    = getattr(C, 'ART_MAX', 405)


def fetch(url, path):
    if path.exists() and path.stat().st_size > 0:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        path.write_bytes(r.read())
    return path


def to_text(pdf, txt):
    txt.parent.mkdir(parents=True, exist_ok=True)
    if not txt.exists() or txt.stat().st_size == 0:
        subprocess.run(['pdftotext', '-enc', 'UTF-8', str(pdf), str(txt)],
                       check=False, capture_output=True)
    return txt.read_text(encoding='utf-8', errors='replace') if txt.exists() else ''


def norm(t):
    t = ud.normalize('NFKC', t.replace('⺠', '民'))
    t = re.sub(r'[ \t　]+', ' ', t)
    return re.sub(r'\n{3,}', '\n\n', t)


def jp_len(t):
    return len(re.findall(r'[ぁ-んァ-ヶ一-龥]', t))


SUBJECTS_ALL = ['憲法', '民法', '刑法', '商法', '民事訴訟法', '刑事訴訟法', '行政法', '小論文']


def section(t, univ):
    """合冊 PDF から対象科目の節だけ取り出す。単独 PDF はそのまま返す。"""
    others = [s for s in SUBJECTS_ALL if s != SUBJECT]
    # 慶應・中央の出題趣旨は【科目】、慶應の問題は 科目〔問題〕
    flat, idx = [], []
    for i, ch in enumerate(t):
        if not ch.isspace():
            flat.append(ch); idx.append(i)
    flat = ''.join(flat)
    ms = [m for m in re.finditer(r'(' + '|'.join(SUBJECTS_ALL) + r')〔問題〕', flat)]
    for j, m in enumerate(ms):
        if m.group(1) == SUBJECT:
            e = idx[ms[j + 1].start()] if j + 1 < len(ms) else len(t)
            return t[idx[m.start()]:e]
    m = re.search(r'【\s*' + SUBJECT + r'\s*】', t)
    if m:
        nxt = re.search(r'【\s*(' + '|'.join(others) + r')\s*】', t[m.end():])
        return t[m.start(): m.end() + (nxt.start() if nxt else len(t))]
    # 立命館の入試講評は「商 法」のように科目名だけの行が見出しになっている。
    # 冒頭に目次（「商法 9ページ」）があるので、見出しは「その行が科目名だけ」であることを条件にする。
    head = re.compile(r'^\s*[<＜]?\s*(公\s*法\s*\([^)]*\)|' +
                      '|'.join(r'\s*'.join(s) for s in SUBJECTS_ALL) + r')\s*[>＞]?\s*$')
    marks, pos = [], 0
    for line in t.split('\n'):
        mm = head.match(line)
        if mm:
            name = re.sub(r'\s', '', mm.group(1))
            # 立命館の「公法（憲法）」「公法（行政法）」は括弧の中が科目名
            km = re.fullmatch(r'公法\(([^)]+)\)', name)
            if km:
                name = km.group(1)
            marks.append((pos, name, pos + len(line) + 1))
        pos += len(line) + 1
    if marks and any(n == SUBJECT for _, n, _ in marks):
        parts = []
        for i, (st, name, after) in enumerate(marks):
            if name != SUBJECT:
                continue
            end = marks[i + 1][0] if i + 1 < len(marks) else len(t)
            seg = t[after:end].strip()
            if jp_len(seg) > 50:
                parts.append(seg)
        if parts:
            return '\n\n'.join(parts)
    return t          # 単独 PDF（同志社など）


LAW_PAT = '|'.join(sorted(C.ALIASES, key=len, reverse=True))


def articles(t):
    """行政法は複数の法令にまたがるので、(法令名, 条文) の組で数える。
    「行訴法9条」「行政手続法第14条」「行訴法37条の2」などを拾う。
    法令名のない裸の『NNN条』は、直前に出た法令名のものとみなす。"""
    t = re.sub(r'(?<=[0-9])\s+(?=[0-9])', '', t)
    out, last = {}, None
    pat = re.compile(r'(?:(' + LAW_PAT + r')\s*)?(?:第\s*)?(\d{1,3})\s*条(\s*の\s*(\d{1,2}))?')
    for m in pat.finditer(t):
        law = m.group(1) or last
        if m.group(1):
            last = m.group(1)
        if not law:
            continue
        art = m.group(2) + ('の' + m.group(4) if m.group(4) else '')
        key = (C.ALIASES.get(law, law), art)
        out[key] = out.get(key, 0) + 1
    return out


HANREI = re.compile(r'(最大判|最大決|最判|最決|大判|大連判|大決|高判|高決)\s*'
                    r'((?:明治|大正|昭和|平成|令和)?\s*(?:\d{1,2}|元)\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)')
CUE = re.compile(r'[^。\n]{6,170}?(?:問題となる|問題である|が問われ|を問うもの|を問う問題|問うている|'
                 r'出題意図|出題趣旨|検討を求め|論ずべき|論じる必要|理解を問う|ポイントとなる|'
                 r'が争点|答えさせる|求められる)[^。\n]{0,60}。')


def main():
    src = json.load(open(ROOT / 'data' / 'sources.json', encoding='utf-8'))
    want = set(sys.argv[1:])
    for it in src['items']:
        if want and it['id'] not in want:
            continue
        # 解説を優先し、それが画像 PDF なら問題文で代用する
        t, kind = '', None
        for k in ('kaisetsu', 'mondai'):
            if not it.get(k): continue
            try:
                pdf = fetch(it[k], CACHE / 'pdf' / f"{it['id']}_{k}.pdf")
            except Exception as e:
                print(f"===== {it['id']}  [{k} 取得失敗 {e}]"); continue
            cand = norm(to_text(pdf, CACHE / 'txt' / f"{it['id']}_{k}.txt"))
            if jp_len(cand) >= 100:
                t, kind = cand, k
                break
        if not kind:
            print(f"===== {it['id']}  [画像 PDF のみ・本文を取り出せない]")
            continue
        sec = section(t, it['univ'])
        arts = articles(sec)
        han, cues = [], []
        for m in HANREI.finditer(sec):
            h = re.sub(r'\s+', '', m.group(0))
            if h not in han: han.append(h)
        for m in CUE.finditer(sec):
            c = re.sub(r'\s+', '', m.group(0))
            if c not in cues: cues.append(c)
        units = {}
        for (law, art), c in arts.items():
            u = C.unit_of(law, art)
            if u: units[u] = units.get(u, 0) + c
        print(f"===== {it['id']}  [{kind}] {jp_len(sec)}字  {it['univ']} {it['year']} {it['term']}")
        print(f"  冒頭: {re.sub(chr(10), '/', sec[:110])}")
        print(f"  単元候補: {sorted(units.items(), key=lambda x: -x[1])[:8]}")
        top = sorted(arts.items(), key=lambda x: -x[1])[:16]
        print(f"  条文: {[f'{l}{a}条' for (l, a), _ in top]}")
        oth = sorted(set(re.findall(r'(民法|刑法|会社法|民事訴訟法|個人情報保護法|都市計画法|建築基準法|食品衛生法|道路法|河川法|土地収用法)\s*(?:第\s*)?\d{1,4}\s*条', sec)))
        if oth: print(f"  関係する個別法: {oth}")
        if han: print(f"  判例: {han[:8]}")
        for c in cues[:6]: print(f"  ◆ {c[:150]}")
        print()


if __name__ == '__main__':
    main()
