# QASAS Kobe Ver 1.0

QASAS（Quantification of Antigen-Specific Antibody Sequences）は、検体のBCRレパトアを、抗原結合性が既知のBCR／抗体配列データベースと照合するWindowsアプリです。IGHV、IGHJ、CDR3アミノ酸配列を用い、CDR3の完全一致（LV0）、Levenshtein距離1（LV1）、距離2（LV2）を区別して、一致ユニーククローン数、総Read数、頻度を表示・Excel保存します。

SARS-CoV-2専用ではありません。必要な列を持つCSVへ差し替えることで、別の抗原特異的抗体データベースも使用できます。現在は1検体ずつ解析する版で、時系列統合は次期拡張です。

## 3つの照合方式

画面の「照合方式」で、次のいずれかを解析前に選択します。既定値はKobe Ver 1.0方式です。

| 方式 | CLI指定 | 検体クローンの単位 | V/Jの条件 | 主な用途 |
|---|---|---|---|---|
| 旧QASAS方式 | `legacy` | 入力IGHV文字列 × 入力IGHJ文字列 × 入力CDR3文字列 | 文字列完全一致 | QASAS2の照合中核との比較・再現 |
| Kobe Ver 1.0方式 | `kobe` | 正規化V候補集合 × 正規化J候補集合 × 正規化CDR3 | 候補のV/J組合せが1つ以上一致 | 表記揺れや複数V/J候補を許容する標準解析 |
| CDR3のみ方式 | `cdr3-only` | 正規化CDR3のみ | V/Jを照合条件に使わない | V/Jコール差に依存しない感度解析 |

3方式は同じ「LV0」「LV1」「LV2」という名称を使いますが、クローン定義と候補選択が異なります。方式間の結果を同一手法として混合・合算しないでください。CDR3のみ方式では同じCDR3を持つReadをV/Jに関係なく合算するため、ユニーククローン数の母集団も他方式と異なります。

固定された詳細仕様、疑似コード、旧QASAS2との互換範囲は [docs/MATCHING_METHODS.md](docs/MATCHING_METHODS.md) に記載しています。

## 対応入力

### CPM様式

CSV／TSVを読み込みます。列名は大文字・小文字や記号を除いて照合し、次の別名に対応します。

| 内容 | 対応列名 |
|---|---|
| IGHV | `Vseg`, `V gene`, `IGHV` |
| IGHJ | `Jseg`, `J gene`, `IGHJ` |
| CDR3アミノ酸 | `CDR3`, `CDR3 AA`, `junction_aa` |
| Read数 | `Counts`, `Count`, `Reads`, `Read count`, `DUPCOUNT` |

正のRead数を持つ行だけを使います。頻度の分母は、採用された全クローンのRead合計です。

### RG様式

Excel（`.xlsx`／`.xlsm`）の `Back_data` シートを読み込みます。

| Excel列 | 内容 | 使用方法 |
|---|---|---|
| G | IGHV | 照合または表示 |
| K | IGHJ | 照合または表示 |
| O | CDR3 | Levenshtein距離 |
| P | frame | `in-frame`だけ採用 |
| Q | Reads | クローン量・頻度 |

Excelに古い使用範囲情報が残っていても途中で切れないよう、`Back_data` の実セルを通常モードで全件走査します。レポート記載の `In-frame reads` に対して列挙Readが95%未満の場合は、途中読込みの疑いとして解析を停止します。

頻度分母は方式により異なります。

- 旧QASAS方式: 採用された `in-frame` クローンのRead合計。旧 `readreport2()` の計算に合わせます。
- Kobe Ver 1.0／CDR3のみ方式: 利用可能で矛盾がなければレポート記載の `In-frame reads`。それ以外は採用クローンのRead合計。

### 抗体データベース

CSV／TSVで、少なくとも次の3列が必要です。

| 内容 | 対応列名 |
|---|---|
| IGHV | `Heavy V Gene`, `IGHV`, `V gene`, `Vseg` |
| IGHJ | `Heavy J Gene`, `IGHJ`, `J gene`, `Jseg` |
| CDR3アミノ酸 | `CDRH3`, `CDR3`, `CDR3 AA`, `junction_aa` |

その他の列は注釈として保持され、同じ照合キーに属する複数行の値を統合してExcelへ出力します。CoV-AbDabの `Name`、`Binds to`、`Protein + Epitope` 等は優先して表示します。

旧QASAS方式では、旧 `createdb2.base()` に合わせて、Human表記を含むDBではIGHV・IGHJの両方がHumanの行だけを使い、末尾の正確な文字列 ` (Human)` だけを除去します。また結合・中和列が存在するDBでは、結合または中和の正味注釈が残る行だけを使います。

旧QASAS方式の「文字列完全一致」には、`*01`、`*02`などのアレル表記も含まれます。コードがアレルを別項目として判定するのではなく、生のIGHV・IGHJ文字列全体をそのまま結合キーに使うためです。検体とDBのアレルが違う場合や、一方だけにアレル表記がある場合は一致しません。IGHJにも同じ規則を適用します。

| 検体IGHV | DB IGHV | 旧QASAS方式の判定 |
|---|---|---|
| `IGHV3-53*01` | `IGHV3-53*01` | 一致 |
| `IGHV3-53*01` | `IGHV3-53*02` | 不一致 |
| `IGHV3-53` | `IGHV3-53*01` | 不一致 |
| `IGHV3-53` | `IGHV3-53` | 一致 |

## インストールと起動

WindowsでPython 3.11以降を推奨します。

1. 初回だけ `QASAS_セットアップ.cmd` をダブルクリックします。
2. `QASASを開く.cmd` をダブルクリックします。
3. 検体、入力様式、照合方式、抗体DBを選択します。
4. 「QASAS解析を実行」を押します。
5. 必要に応じて「結果をExcel保存…」を押します。

手動セットアップは次のとおりです。

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe QASAS_app.pyw
```

## コマンドライン実行

GUIと同じエンジンをコマンドラインから実行できます。`--mode` は `legacy`、`kobe`、`cdr3-only` のいずれかです。

```powershell
python qasas_cli.py `
  --sample "QASAS レパトアデータ\KKF103hG_human_igh_report.xlsx" `
  --database "QASAS データベース CoV-AbDab\CoV-AbDab_080224.csv" `
  --format RG `
  --mode kobe `
  --output "QASAS 結果\KKF103_kobe.xlsx"
```

3方式を同じ入力で連続検証する場合は、同梱スクリプトを使います。

```powershell
python scripts\validate_three_modes.py `
  --sample "QASAS レパトアデータ\KKF103hG_human_igh_report.xlsx" `
  --database "QASAS データベース CoV-AbDab\CoV-AbDab_080224.csv" `
  --format RG `
  --output-dir "QASAS 結果\KKF103_3mode_validation"
```

このスクリプトは3つのExcel結果に加え、アルゴリズム版、入力SHA-256、DB SHA-256、全集計値を含む `validation_summary.json` を保存します。

## LV距離と集計値

CDR3アミノ酸配列のLevenshtein距離は、1文字の置換・挿入・削除を各コスト1として計算します。各検体クローンは候補DB配列との最小距離で1回だけ分類されます。

- 個別: `LV0`、`LV1`、`LV2` は最小距離が正確に0、1、2のクローン。
- 累積: `≤LV0`、`≤LV1`、`≤LV2` は最小距離が閾値以下のクローン。
- ユニーククローン数: 選択方式のクローンキーで一意化された検体クローン数。
- 総Read数: 該当クローンのRead合計。
- 頻度: 各クローンの `100 × Read / 方式別分母` の合計。

旧QASAS方式だけは、旧 `findcov2()` の挙動を再現するため、距離0～2のDB候補注釈をすべて保持しながら、検体クローンのLV区分を候補中の最小距離で決めます。Kobe Ver 1.0方式とCDR3のみ方式は最小距離のDB候補だけを保持します。

## Excel出力

| シート | 内容 |
|---|---|
| `Summary` | 入力情報、方式、個別LV0/1/2、累積≤LV0/1/2、グラフ |
| `Method` | アルゴリズム版と、その結果に適用された固定規則 |
| `Input QC` | 採用・除外行数、Read分母、RGメタデータ、DB処理情報 |
| `Matched Clones` | 一致クローン、Read、頻度、元表記、保持DB数・各距離、DB注釈 |

結果を第三者へ渡すときは、少なくとも `Method`、`Input QC`、入力ファイルとDBのSHA-256、使用したGitコミットを一緒に保存してください。

## 再現性

現在のアルゴリズム識別子は `QASAS-Kobe-three-mode-1.0` です。再現手順、SHA-256の取得法、受入試験、保存すべき監査情報は [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) を参照してください。今回使用した実検体による基準値は [docs/VALIDATION_RESULTS.md](docs/VALIDATION_RESULTS.md) に固定しています。

旧QASAS2互換仕様は、研究グループの `takajim/QASAS2` の `main`、コミット `b1987209a7b2fb5bc0a55360654b79d01384dccb` を参照して実装しました。旧リポジトリは閲覧だけに使用し、変更していません。

## テスト

```powershell
python -m compileall -q qasas qasas_cli.py QASAS_app.pyw
python -m unittest discover -v
```

テストには、3方式のV/J候補規則、旧方式の全候補保持、CDR3のみ方式のV/J横断集約、RGの全件読込み、DB前処理、Excel `Method` 記録、CDR3高速索引と総当たりLevenshtein判定の一致を含みます。

## データ保護

アプリは入力ファイルを読取り専用で扱い、元の検体・DBを変更しません。次の利用者データ／生成物は `.gitignore` の対象です。

- `QASAS レパトアデータ/`
- `QASAS データベース CoV-AbDab/`
- `QASAS 論文集/`
- `QASAS 結果/`
- `validation/`

公開GitHubへ検体、DB、論文PDF、解析結果を誤って登録しないでください。
