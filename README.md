# 行政法過去問帳

ロースクール既修者入試（行政法）の過去問を、**行政法の単元ごとに**引ける学習帳。

**https://law-kakomon.github.io/gyosei-kakomon/**

- **単元から引く** — 行政法総論／行政作用／行政手続／情報公開／行政不服申立て／取消訴訟／その他の訴訟／仮の救済／国家補償／地方自治
- **条文から引く** — 検索欄に `14` と入れると、行政手続法14条などが論じられた回が並ぶ
- **論点・判例で探す** — 「行政裁量」「理由の提示」「最判平成23年6月7日」などで検索
- **問題と解説をその場で読む** — PDF をページ内に表示
- **解いた回に印をつける** — チェックはこの端末のブラウザにだけ残る

収録は同志社・立命館の2校、計 40 回（2008〜2027年度）。

**行政法を課しているのはこの2校だけです。** 関学・慶應・中央は既修者入試の科目にありません。立命館は憲法と合わせた「公法」で出題しており、行政法の講評があるのは2018・2019年度だけなので、その6回を収録しています。

行政法には単一の法典がないため、条文は**法令名つき**で示しています（行手法＝行政手続法、行訴法＝行政事件訴訟法、行審法＝行政不服審査法、国賠法＝国家賠償法、自治法＝地方自治法）。

**PDF は各大学の公式ページをそのまま開きます**（このリポジトリに複製は置いていません）。

## 使い方

```bash
open 開く.command
```

## 更新

```bash
python3 tools/fetch_sources.py
python3 tools/digest.py <新しいID>
# tools/classify.py に単元・論点を追記
python3 tools/build_data.py
```

くわしくは [CLAUDE.md](CLAUDE.md)。

## 出典

- [同志社大学法科大学院 過去の入試・履修免除試験問題](https://law-school.doshisha.ac.jp/entrance_ex/question/)
- [立命館大学法科大学院 過去の入試問題・講評](https://www.ritsumei.ac.jp/lawschool/admission/past.html/)

## 姉妹サイト

科目の入口は **https://law-kakomon.github.io/** 。

- [民法過去問帳](https://law-kakomon.github.io/minpo-kakomon/)
- [民事訴訟法過去問帳](https://law-kakomon.github.io/minso-kakomon/)
- [会社法過去問帳](https://law-kakomon.github.io/kaisha-kakomon/)
- [憲法過去問帳](https://law-kakomon.github.io/kenpo-kakomon/)
- [刑法過去問帳](https://law-kakomon.github.io/keiho-kakomon/)
- [刑事訴訟法過去問帳](https://law-kakomon.github.io/keiso-kakomon/)
