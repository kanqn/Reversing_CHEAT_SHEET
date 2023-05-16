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
