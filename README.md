### よく使うコマンド

```
./rp-lin -f /home/kali/pwn/wanictf2023-writeup/pwn/ret2libc/src/libc.so.6 --rop=2 --unique | grep 'pop rcx'
```

### RELRO無効化

```
gcc -Wl,-z,norelro -o target example.c
```

### SSP無効化

```
-fno-stack-protector
```

### NXbit無効化

```
-z execstack
```

### ASLR無効化

```
sudo sysctl kernel.randomize_va_space=0
```

### PIE無効化

```
-no-pie
```

# PWNやBinaryについてのメモ

### 読むべき記事

glibcでRIP取得に使えるシンボルまとめ  
https://kam1tsur3.org/2022/06/22/get-rip-in-libc/  

https://megalodon.jp/2025-0929-0233-52/https://kam1tsur3.org:443/2022/06/22/get-rip-in-libc/  
  
glibc heap問で個人的によく使うテクニックについて  
https://hama.hatenadiary.jp:443/entry/2018/12/08/142437  
  
https://megalodon.jp/2025-0929-0232-39/https://hama.hatenadiary.jp:443/entry/2018/12/08/142437
  
Xornet氏のpwnまとめ  
https://hackmd.io/@Xornet/BkemeSAhU  
  
Learning ARM Exploit Development  
http://www.alicemacs.com/ARM_Exploit/    
  
StackPivotやROPについての日本語記事を書いている  
https://sh0ebill.hatenablog.com/entry/2022/10/06/225144  
  

セキュリティ機構について  
https://miso-24.hatenablog.com/entry/2019/10/16/021321  
  
pwn入門編  
https://hackmd.io/@xk4KNXQvTxu07bQ0WJ7FUQ/rJTiw9Ww4?type=view  
  
x64でpwnする際の注意点  
https://qiita.com/4hiziri/items/298539ed8c945e8e6329  



### Writeup置き場

  
pwn100本ノック  
https://zenn.dev/musacode/scraps/7fc68fd44283b8  

### 解けなかったけど解きたいpwn問題
Ricerca2023 ctf nemu
https://hjmsan.hatenablog.com/entry/2023/04/23/122516
