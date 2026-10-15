00409b84 mov eax, dword ptr [ebp - 0x3c]
00409b87 cmp dword ptr [eax + 0xa0], 0x46
00409b8e jge 0x409bfc
00409b90 mov edx, dword ptr [ebp - 0x34]
00409b93 cmp byte ptr [edx + 0x11d], 0
00409b9a je 0x409bfc
00409b9c mov ecx, dword ptr [ebp - 0x3c]
00409b9f cmp dword ptr [ecx + 0xa0], 0x1e
00409ba6 jle 0x409bcd
00409ba8 mov edx, dword ptr [ebp - 0x34]
00409bab add edx, 0x198
00409bb1 mov eax, dword ptr [ebp - 0x34]
00409bb4 add eax, 0x158
00409bb9 call 0x402ca8
00409bbe mov edx, eax
00409bc0 mov ecx, dword ptr [ebp - 0x38]
00409bc3 mov eax, dword ptr [ebp - 0x34]
00409bc6 call 0x402f08
00409bcb jmp 0x409bfc
00409bcd mov eax, dword ptr [ebp - 0x3c]
00409bd0 cmp dword ptr [eax + 0xa0], 1
00409bd7 jle 0x409bfc
00409bd9 mov edx, dword ptr [ebp - 0x34]
00409bdc add edx, 0x19c
00409be2 mov eax, dword ptr [ebp - 0x34]
00409be5 add eax, 0x158
00409bea call 0x402ca8
00409bef mov edx, eax
00409bf1 mov ecx, dword ptr [ebp - 0x38]
00409bf4 mov eax, dword ptr [ebp - 0x34]
00409bf7 call 0x402f08
00409bfc mov edx, dword ptr [ebp - 0x3c]
00409bff fld dword ptr [edx + 0xa4]
00409c05 fld dword ptr [0x409fb8]
00409c0b fxch st(1)
00409c0d fucompp 
00409c0f fnstsw ax
00409c11 test ah, 5
00409c14 jp 0x409cc0
00409c1a mov edx, dword ptr [ebp - 0x34]
00409c1d cmp byte ptr [edx + 0x11d], 0
00409c24 je 0x409cc0
00409c2a mov ecx, dword ptr [ebp - 0x3c]
00409c2d fld dword ptr [ecx + 0xa4]
00409c33 fld dword ptr [0x409fbc]
00409c39 fxch st(1)
00409c3b fucompp 
00409c3d fnstsw ax
00409c3f test ah, 5
00409c42 jnp 0x409cc0
00409c44 mov edx, dword ptr [ebp - 0x3c]
00409c47 fld dword ptr [edx + 0xa4]
00409c4d fld qword ptr [0x409fc0]
00409c53 fxch st(1)
00409c55 fucompp 
00409c57 fnstsw ax
00409c59 test ah, 5
00409c5c jp 0x409c83
00409c5e mov edx, dword ptr [ebp - 0x34]
00409c61 add edx, 0x194
00409c67 mov eax, dword ptr [ebp - 0x34]
00409c6a add eax, 0x158
00409c6f call 0x402ca8
00409c74 mov edx, eax
00409c76 mov ecx, dword ptr [ebp - 0x38]
00409c79 mov eax, dword ptr [ebp - 0x34]
00409c7c call 0x402f08
00409c81 jmp 0x409cc0
00409c83 mov edx, dword ptr [ebp - 0x3c]
00409c86 fld dword ptr [edx + 0xa4]
00409c8c fld qword ptr [0x409fc8]
00409c92 fxch st(1)
00409c94 fucompp 
00409c96 fnstsw ax
00409c98 test ah, 5
00409c9b jp 0x409cc0
00409c9d mov edx, dword ptr [ebp - 0x34]
00409ca0 add edx, 0x190
00409ca6 mov eax, dword ptr [ebp - 0x34]
00409ca9 add eax, 0x158
00409cae call 0x402ca8
00409cb3 mov edx, eax
00409cb5 mov ecx, dword ptr [ebp - 0x38]
00409cb8 mov eax, dword ptr [ebp - 0x34]
00409cbb call 0x402f08
00409cc0 mov edx, dword ptr [ebp - 0x3c]
00409cc3 cmp dword ptr [edx + 0xa0], 0x82
00409ccd jle 0x409cfe
00409ccf mov ecx, dword ptr [ebp - 0x34]
00409cd2 cmp byte ptr [ecx + 0x11d], 0
00409cd9 je 0x409cfe
00409cdb mov edx, dword ptr [ebp - 0x34]
00409cde add edx, 0x1a0
00409ce4 mov eax, dword ptr [ebp - 0x34]
00409ce7 add eax, 0x158
00409cec call 0x402ca8
00409cf1 mov edx, eax
00409cf3 mov ecx, dword ptr [ebp - 0x38]
00409cf6 mov eax, dword ptr [ebp - 0x34]
00409cf9 call 0x402f08
