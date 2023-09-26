## pwntools  
  
### ライブラリのインポート  
``` from pwn import * ```  


### おまじない



```

from pwn import *

warnings.simplefilter('ignore',category=BytesWarning)
bin_file = './vuln'
binf = ELF(bin_file,checksec = False)
context.binary = binf
context.log_level = 'debug'

conn = process(bin_file)

```

libcが配布された形の場合は以下も追加をすることで  
実行するバイナリとlibcを別々でしていしてプログラムを走らせることができる    

```
lib = './libc.so.6'  # libc ライブラリを設定します
libc = context.binary = ELF(lib, checksec= False )
```

### オフセットを調べる

```
offset = cyclic(100)
conn.sendlineafter('Enter details' , offset)
conn.wait()

#x86
result_offset = cyclic_find(conn.corefile.pc)

#x64
result_offset = cyclic_find(conn.corefile.read(conn.corefile.sp, 4))

print(result_offset)
```

### 文字列を検索する

以下の例はlibcライブラリからbin/shを検索する

```
shell = next(libc.search(b'/bin/sh\x00'))
```


### リトルエンディアンに変換する - p32()
```
from pwn import *

p32(0xcafebabe) # '\xef\xbe\xad\xde'
hex(u32('\xef\xbe\xad\xde')) # 0xcafebabe
```

### 標準入出力  
### データの受信  
``` recv(n) ```: nバイト分のデータを受け取る  
``` recvline() ```: 一行分(改行が来るまで)のデータを受け取る  
``` recvuntil(hoge) ```: hogeが来るまでデータを受け取る  
``` recvregex(pattern) ```: patternで指定された正規表現にマッチするまでデータを受け取る  
``` recvrepeat(timeout) ```: タイムアウトになるかEOFに達するまでデータを受け取る  
``` clean() ```: バッファリングされたデータを破棄する  
データの送信  
``` send(data) ```: dataを送信する  
``` sendline(line) ```: 引数に与えたデータに「\n」を付けて送信する  


### プロセスとのやりとりを行う - process()
```
from pwn import *

io = process('sh')
io.sendline('echo Hello, world')
io.recvline()
# 'Hello, world\n'
```

### 対話モードでの通信 - interactive()
```
from pwn import *

io = process('sh')

io.interactive()
```
### ネットワーク通信 - remote()
```
from pwn import *

io = remote('google.com', 80)
io.send('GET /\r\n\r\n')
io.recv(8)
# 'HTTP/1.0'
```
