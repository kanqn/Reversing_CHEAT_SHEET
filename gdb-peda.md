## gdp-peda CHEAT SHEET


#### 指定した関数がどこから始まっているかを表示する
``` p 関数名 ```
※なお、同様の動作をobjdump -d -M intel ./ファイル名　でも再現可能

#### ブレークポイントの設定
``` b *ブレークポイントのアドレス ```



#### プログラムの実行
``` run ``` or ``` r ```


####  コマンドでレジスタの中身を詳しく表示する
``` i r ```
また、フラグレジスタの種類と意味については以下のサイトを参考にすると良い

X86アセンブラ/x86アーキテクチャ - Wikibooks
https://ja.wikibooks.org/wiki/X86%E3%82%A2%E3%82%BB%E3%83%B3%E3%83%96%E3%83%A9/x86%E3%82%A2%E3%83%BC%E3%82%AD%E3%83%86%E3%82%AF%E3%83%81%E3%83%A3

#### レジスタの値を変更する
``` set $レジスタの変数=0xフラグレジスタの値 ```

#### フレームの情報を表示 - info frame
