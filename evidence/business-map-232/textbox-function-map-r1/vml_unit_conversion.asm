0041a204 push ebp
0041a205 mov ebp, esp
0041a207 add esp, -0x38
0041a20a mov byte ptr [ebp - 0x2d], cl
0041a20d mov dword ptr [ebp - 0x2c], edx
0041a210 mov dword ptr [ebp - 0x28], eax
0041a213 mov eax, 0x6c8ec4
0041a218 call 0x6ad68c
0041a21d mov edx, dword ptr [0x6c1168]
0041a223 mov dword ptr [ebp - 0x34], edx
0041a226 mov dx, word ptr [0x6c116c]
0041a22d mov word ptr [ebp - 0x30], dx
0041a231 lea ecx, [ebp - 0x33]
0041a234 push ecx
0041a235 lea eax, [ebp - 0x34]
0041a238 push eax
0041a239 lea edx, [ebp - 0x38]
0041a23c push edx
0041a23d push 0x6c2bc8
0041a242 mov eax, dword ptr [ebp - 0x2c]
0041a245 call 0x409454
0041a24a push eax
0041a24b call 0x6b21a8
0041a250 add esp, 0x14
0041a253 test eax, eax
0041a255 jne 0x41a26c
0041a257 fld dword ptr [0x41a3a4]
0041a25d mov edx, dword ptr [ebp - 0x24]
0041a260 mov dword ptr fs:[0], edx
0041a267 jmp 0x41a39e
0041a26c push 0x6c2bcf
0041a271 lea ecx, [ebp - 0x34]
0041a274 push ecx
0041a275 call 0x6ad0dc
0041a27a add esp, 8
0041a27d test eax, eax
0041a27f jne 0x41a292
0041a281 fld dword ptr [0x41a3a8]
0041a287 fmul dword ptr [ebp - 0x38]
0041a28a fstp dword ptr [ebp - 0x38]
0041a28d jmp 0x41a392
0041a292 push 0x6c2bd2
0041a297 lea eax, [ebp - 0x34]
0041a29a push eax
0041a29b call 0x6ad0dc
0041a2a0 add esp, 8
0041a2a3 test eax, eax
0041a2a5 jne 0x41a2b8
0041a2a7 fld dword ptr [0x41a3ac]
0041a2ad fmul dword ptr [ebp - 0x38]
0041a2b0 fstp dword ptr [ebp - 0x38]
0041a2b3 jmp 0x41a392
0041a2b8 push 0x6c2bd5
0041a2bd lea edx, [ebp - 0x34]
0041a2c0 push edx
0041a2c1 call 0x6ad0dc
0041a2c6 add esp, 8
0041a2c9 test eax, eax
0041a2cb je 0x41a392
0041a2d1 push 0x6c2bd8
0041a2d6 lea ecx, [ebp - 0x34]
0041a2d9 push ecx
0041a2da call 0x6ad0dc
0041a2df add esp, 8
0041a2e2 test eax, eax
0041a2e4 jne 0x41a2f7
0041a2e6 fld dword ptr [0x41a3b0]
0041a2ec fmul dword ptr [ebp - 0x38]
0041a2ef fstp dword ptr [ebp - 0x38]
0041a2f2 jmp 0x41a392
0041a2f7 push 0x6c2bdb
0041a2fc lea eax, [ebp - 0x34]
0041a2ff push eax
0041a300 call 0x6ad0dc
0041a305 add esp, 8
0041a308 test eax, eax
0041a30a jne 0x41a31a
0041a30c fld dword ptr [0x41a3b4]
0041a312 fmul dword ptr [ebp - 0x38]
0041a315 fstp dword ptr [ebp - 0x38]
0041a318 jmp 0x41a392
0041a31a push 0x6c2bde
0041a31f lea edx, [ebp - 0x34]
0041a322 push edx
0041a323 call 0x6ad0dc
0041a328 add esp, 8
0041a32b test eax, eax
0041a32d jne 0x41a33d
0041a32f fld dword ptr [0x41a3b8]
0041a335 fmul dword ptr [ebp - 0x38]
0041a338 fstp dword ptr [ebp - 0x38]
0041a33b jmp 0x41a392
0041a33d cmp byte ptr [ebp - 0x2d], 0
0041a341 je 0x41a36b
0041a343 mov ecx, dword ptr [ebp - 0x28]
0041a346 push dword ptr [ecx + 0xd8]
0041a34c mov eax, dword ptr [ebp - 0x28]
0041a34f add eax, 0xd4
0041a354 push eax
0041a355 call 0x403c58
0041a35a add esp, 8
0041a35d fld dword ptr [eax + 0x10c]
0041a363 fmul dword ptr [ebp - 0x38]
0041a366 fstp dword ptr [ebp - 0x38]
0041a369 jmp 0x41a392
0041a36b mov edx, dword ptr [ebp - 0x28]
0041a36e push dword ptr [edx + 0xd8]
0041a374 mov ecx, dword ptr [ebp - 0x28]
0041a377 add ecx, 0xd4
0041a37d push ecx
0041a37e call 0x403c58
0041a383 add esp, 8
0041a386 fld dword ptr [eax + 0x108]
0041a38c fmul dword ptr [ebp - 0x38]
0041a38f fstp dword ptr [ebp - 0x38]
0041a392 fld dword ptr [ebp - 0x38]
0041a395 mov eax, dword ptr [ebp - 0x24]
0041a398 mov dword ptr fs:[0], eax
0041a39e mov esp, ebp
0041a3a0 pop ebp
0041a3a1 ret 
