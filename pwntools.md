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
