#HEAP EXPLOIT MEMO

## tcache Poisoning
tcacheは、malloc時にchunksizeを確認しない。fastbinsから割当てを行う場合はその領域のchunksizeからfastbin_indexを再計算してindexが正しいかを確認する処理が入っているが、  
tcacheのときにはなぜかこれがなくて、現状最新のglibc.2.29でもやはりこのチェックは導入されていない  

## Unsorted bin
Unsorted Binに入るチャンクはメモリ上でその下のチャンク(と更にその下)のPREV_INUSEが立っているかを確認している  
これに引っかかるとtopに繋がれる  
