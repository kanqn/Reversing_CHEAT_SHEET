# HEAP EXPLOIT MEMO

## tcache Poisoning
tcacheは、malloc時にchunksizeを確認しない。fastbinsから割当てを行う場合はその領域のchunksizeからfastbin_indexを再計算して  
indexが正しいかを確認する処理が入っているが、  
tcacheのときにはなぜかこれがなくて、現状最新のglibc.2.29でもやはりこのチェックは導入されていない  
  
## Unsorted bin
・Unsorted Binに入るチャンクはメモリ上でその下のチャンク(と更にその下)のPREV_INUSEが立っているかを確認している  
　これに引っかかるとtopに繋がれる  

## global_max_fast
global_max_fastはlibc内の静的変数で、free時にchunkをfastbinに登録するかの判断に用いられている  
https://zenn.dev/ri5255/articles/7fc2bcbea22b11#1.-unsorted-bin-attack%E3%81%AB%E3%82%88%E3%82%8Bglobal_max_fast%E3%81%AE%E6%94%B9%E7%AB%84
