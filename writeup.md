## PicoCTF

### PIE TIME

プログラムを実行するとmain関数のアドレスが表示される
win関数が存在し、ここに飛べばフラグを取得できる
→main関数とwin関数の差分を計算すれば良い

```
gef➤  b *main
Breakpoint 1 at 0x133d
gef➤  p(*main - *win)
$1 = 0x96
```

オフセットは0x96
