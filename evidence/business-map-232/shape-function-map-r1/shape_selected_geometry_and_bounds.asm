004389ab mov ecx, dword ptr [ebp - 0x74]
004389ae mov eax, dword ptr [ecx + 0x120]
004389b4 mov dword ptr [ebp - 0xa0], eax
004389ba mov word ptr [ebp - 0x5c], 0xc
004389c0 mov edx, dword ptr [ebp - 0x74]
004389c3 mov ecx, dword ptr [edx + 0x124]
004389c9 mov dword ptr [ebp - 0xa4], ecx
004389cf fld xword ptr [0x438ea4]
004389d5 mov eax, dword ptr [ebp - 0x74]
004389d8 fmul dword ptr [eax + 0x148]
004389de add esp, -8
004389e1 fstp qword ptr [esp]
004389e4 call 0x6b7074
004389e9 add esp, 8
004389ec fadd dword ptr [0x438eb0]
004389f2 call 0x6b70b8
004389f7 mov dword ptr [ebp - 0xa8], eax
004389fd mov edx, dword ptr [ebp - 0xa8]
00438a03 and edx, 0x80000001
00438a09 jns 0x438a10
00438a0b dec edx
00438a0c or edx, 0xfffffffe
00438a0f inc edx
00438a10 test edx, edx
00438a12 je 0x438a32
00438a14 mov ecx, dword ptr [ebp - 0x74]
00438a17 mov eax, dword ptr [ecx + 0x124]
00438a1d mov dword ptr [ebp - 0xa0], eax
00438a23 mov edx, dword ptr [ebp - 0x74]
00438a26 mov ecx, dword ptr [edx + 0x120]
00438a2c mov dword ptr [ebp - 0xa4], ecx
00438a32 mov eax, dword ptr [ebp - 0x74]
00438a35 fld dword ptr [eax + 0x140]
00438a3b mov edx, dword ptr [ebp - 0x74]
00438a3e fadd dword ptr [edx + 0x138]
00438a44 fsubr dword ptr [ebp - 0xa0]
00438a4a fld dword ptr [ebp - 0x90]
00438a50 fadd dword ptr [0x438eb4]
00438a56 fcompp 
00438a58 fnstsw ax
00438a5a test ah, 0x41
00438a5d jnp 0x438a90
00438a5f mov edx, dword ptr [ebp - 0x74]
00438a62 fld dword ptr [edx + 0x13c]
00438a68 mov ecx, dword ptr [ebp - 0x74]
00438a6b fadd dword ptr [ecx + 0x144]
00438a71 fsubr dword ptr [ebp - 0xa4]
00438a77 fld dword ptr [ebp - 0x94]
00438a7d fsub dword ptr [0x438eb8]
00438a83 fcompp 
00438a85 fnstsw ax
00438a87 test ah, 0x41
00438a8a jp 0x438b3d
00438a90 cmp byte ptr [ebp - 0x95], 0
00438a97 je 0x438aeb
00438a99 push 1
00438a9b mov word ptr [ebp - 0x5c], 0x54
00438aa1 mov edx, 0x6cf00a
00438aa6 lea eax, [ebp - 0x18]
00438aa9 call 0x6bf0b0
00438aae inc dword ptr [ebp - 0x50]
00438ab1 lea edx, [ebp - 0x18]
00438ab4 push edx
00438ab5 mov edx, dword ptr [ebp - 0x70]
00438ab8 add edx, 0x200
00438abe mov eax, dword ptr [ebp - 0x70]
00438ac1 add eax, 0x158
00438ac6 call 0x402ca8
00438acb mov edx, eax
00438acd mov eax, dword ptr [ebp - 0x70]
00438ad0 pop ecx
00438ad1 call 0x403318
00438ad6 dec dword ptr [ebp - 0x50]
00438ad9 lea eax, [ebp - 0x18]
00438adc mov edx, 2
00438ae1 call 0x6bf114
00438ae6 jmp 0x438bd0
00438aeb push 1
00438aed mov word ptr [ebp - 0x5c], 0x60
00438af3 mov edx, 0x6cf00c
00438af8 lea eax, [ebp - 0x1c]
00438afb call 0x6bf0b0
00438b00 inc dword ptr [ebp - 0x50]
00438b03 lea ecx, [ebp - 0x1c]
00438b06 push ecx
00438b07 mov edx, dword ptr [ebp - 0x70]
00438b0a add edx, 0x1e4
00438b10 mov eax, dword ptr [ebp - 0x70]
00438b13 add eax, 0x158
00438b18 call 0x402ca8
00438b1d mov edx, eax
00438b1f mov eax, dword ptr [ebp - 0x70]
00438b22 pop ecx
00438b23 call 0x403318
00438b28 dec dword ptr [ebp - 0x50]
00438b2b lea eax, [ebp - 0x1c]
00438b2e mov edx, 2
00438b33 call 0x6bf114
00438b38 jmp 0x438bd0
