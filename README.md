# aributil

ARIB-STD B10, ARIB-STD-B24 の Python 3 での簡単な実装です。
簡単な TS をパースするコードと、それらを利用したスクリプトからなります。

簡単にパースする事、コードが見やすいこと、参考にしやすいこと、移植しやすい事に重点を置いています。
速度やメモリ効率に関しては度外視ですので、ご利用なさる方がいましたら、その点だけ注意してください。

## スクリプト

### segmenter.py

TS 内の EIT[p/f] にある現在放送中の番組情報から番組単位で TS を分割するスクリプトです。

#### オプション

* -i, --input: 入力 TS ファイルを指定します。省略された場合は標準入力になります。
* -o, --output_path: 出力先のパスを指定します。省略された場合はカレントディレクトリになります。
* -s, --SID: 対象の サービスID を指定します。 (必須)

### splitter.py

TS 内のストリームのうち対象の SID に紐付くストリームを抜き出すスクリプトです。

#### オプション

* -i, --input: 入力 TS ファイルを指定します。省略された場合は標準入力になります。
* -o, --output_path: 出力先の TS ファイルを指定します。省略された場合は標準出力になります。
* -s, --SID: 対象の サービスID を指定します。 (必須)
* -p, --PID: 出力 TS に別途含める PID を指定します。

### renderer.py

TS 内のAプロファイルの字幕をレンダリングするスクリプトです。

#### オプション

* -i, --input: 入力 TS ファイルを指定します。省略された場合は標準入力になります。
* -o, --output_path: 出力先のパスを指定します。省略された場合はカレントディレクトリになります。
* -s, --SID: 対象の サービスID を指定します。 (必須)
* -f, --ffmpeg: ffmpeg を利用してスクリーンショットを取り、その上に字幕を描画します。
