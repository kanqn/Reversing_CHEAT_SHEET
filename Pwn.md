# pwn,reversing,binary  
  
  
  
## bufferoverflow  
### リターンアドレスを書き換える
リターンアドレスは、**rbp+0x8の場所**に位置しているため、0x8分のパディングを忘れないようにすること  
また、32bitアーキテクチャの場合は、  
パディング  
+  
8byte(rbp分のパディング)  
+   
4byte(パディング)   
+  
飛ばしたいアドレス  
の順番になる  
  
  
  
### 引数をつけて関数を飛ばす  
#### 引数のよりも前にリターンアドレスを書き換える！
パディング  
+  
8byte(rbp分のパディング)  
+   
4byte(パディング)   
+  
飛ばしたいアドレス  
+  
4byte(ret分のパディング)  
+  
引数1  
+  
引数2  
の順番になる  
https://tech.kusuwada.com/entry/2019/10/12/023145#section1  
  
  
### シェルコードをインジェクションする  
シェルコード  
+  
本来のパディング数 - シェルコードの文字数  
+  
8byte(パディング)  
+  
バッファーアドレス  


### pwntoolsメモ
#### うまく実行したコードが刺さらないとき  
``` context.log_level = "debug" ```  
にすることで、recvした際にどのようなデータが飛んできているのかがわかる  







### C言語の関数内の脆弱性

#### rand()を呼び出した際に引数に何も渡さない場合の脆弱性
rand()内になにも引数を渡さない場合は、何回プログラムを実行しても同じ値がrandomに代入される。  
また、key^randomの^はXOR演算子と呼ばれるもので特徴として**a^(a^b) == b となる。**  
例:  0xrandomの値が格納されているアドレス ^ 0xdeadbeef を入力すれば、0xdeadbeefが解になる。

```
from pwn import *

payload = 0x6b8b4567 ^ 0xdeadbeef
s1 = ssh(host="pwnable.kr", user="random", password="guest", port=2222)
r = s1.process("./random")
r.sendline(str(payload).encode())
r.interactive()
```
