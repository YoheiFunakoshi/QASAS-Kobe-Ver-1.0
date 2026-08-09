# QASAS Kobe Ver 1.0

QASAS（Quantification of Antigen-specific Antibody Sequence）は、検体のBCRレパトアと、抗原結合性が既知のBCR／抗体配列データベースを照合するWindowsアプリです。

このVer 1.0は、1回につき1検体を解析します。時系列検体の統合表示は次期拡張で対応します。

## Ver 1.0の機能

- CPM様式CSVを読み込みます。
  - `Vseg`、`Jseg`、`CDR3`、`Counts`を使用します。
- RG様式Excelを読み込みます。
  - `Back_data`の`7:All Data`全件領域を使用します。
  - G列=IGHV、K列=IGHJ、O列=CDR3、P列=frame、Q列=Readsとして、`in-frame`のみを解析します。
  - レポート内に全in-frameクローンが列挙されていない場合も、頻度の分母にはレポート記載の`In frame`総リード数を使用し、列挙されたリード数と分けて表示します。
- 抗原結合性データベースCSVを選択できます。
  - CoV-AbDabでは`Heavy V Gene`、`Heavy J Gene`、`CDRH3`を使用します。
  - 同等の3列を持つ別データベースへ交換できます。
- IGHV・IGHJが一致する配列間でCDR3アミノ酸Levenshtein距離を計算します。
- LV0、LV1、LV2を個別に集計し、同時に累積の≤LV0、≤LV1、≤LV2も表示します。
- 一致ユニーククローン数、総リード数、頻度（%）を表とグラフで表示します。
- 一致クローンとデータベース注釈をExcelへ保存します。

## 起動方法

1. 初回のみ`QASAS_セットアップ.cmd`をダブルクリックします。
2. `QASASを開く.cmd`をダブルクリックします。
3. 検体レパトア、入力様式、抗体データベースを選択します。
4. `QASAS解析を実行`を押します。
5. 必要に応じて`結果をExcel保存…`を押します。

Python 3.11以降を推奨します。必要パッケージは`openpyxl`と`matplotlib`です。

## 配列の正規化

- IGHV／IGHJのアレル番号（例:`*01`）と`(Human)`表記を除去します。
- 複数候補の遺伝子表記は候補ごとに照合します。
- CPM／RGで保存されるCDR3の保存的な先頭`C`・末尾`W`は、両方がある場合に除去してデータベースCDRH3と揃えます。
- データベースはV/J/CDR3の同一キーで重複排除し、注釈は統合します。
- 1検体クローンが複数のDB配列に一致した場合、最小距離のクラスへ1回だけ計上します。

## 出力Excel

- `Summary`: 入力情報、個別LV0/1/2、累積≤LV0/1/2、棒グラフ
- `Input QC`: 読込行数、除外行数、正規化後クローン数など
- `Matched Clones`: 一致クローン、Reads、頻度、データベース注釈

## データ保護

解析は入力ファイルを読み取るだけで、元データを変更しません。次の利用者データは`.gitignore`でGit対象外です。

- `QASAS レパトアデータ/`
- `QASAS データベース CoV-AbDab/`
- `QASAS 論文集/`
- `QASAS 結果/`
