; TestVkr232.exe SHA-256 5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0
; Decoded from complete FUN_00437374 entry; only addresses 00437b69-00437cfc shown.
00437b69 mov     ecx, dword ptr [ebp - 0x90]
00437b6f fld     dword ptr [ecx + 0x10]
00437b72 fld     dword ptr [0x438050]
00437b78 fxch    st(1)
00437b7a fucompp
00437b7c fnstsw  ax
00437b7e test    ah, 5
00437b81 jp      0x437be5
00437b83 lea     eax, [ebp - 0x1c]
00437b86 call    0x4032dc
00437b8b test    al, al
00437b8d jne     0x437be5
00437b8f push    1
00437b91 mov     word ptr [ebp - 0x74], 0xa8
00437b97 mov     edx, 0x6cefea
00437b9c lea     eax, [ebp - 0x48]
00437b9f call    0x6bf0b0
00437ba4 inc     dword ptr [ebp - 0x68]
00437ba7 lea     edx, [ebp - 0x48]
00437baa push    edx
00437bab mov     edx, dword ptr [ebp - 0x88]
00437bb1 add     edx, 0x290
00437bb7 mov     eax, dword ptr [ebp - 0x88]
00437bbd add     eax, 0x158
00437bc2 call    0x402ca8
00437bc7 mov     edx, eax
00437bc9 mov     eax, dword ptr [ebp - 0x88]
00437bcf pop     ecx
00437bd0 call    0x403318
00437bd5 dec     dword ptr [ebp - 0x68]
00437bd8 lea     eax, [ebp - 0x48]
00437bdb mov     edx, 2
00437be0 call    0x6bf114
00437be5 mov     ecx, dword ptr [ebp - 0x90]
00437beb fld     dword ptr [ecx + 8]
00437bee fld     dword ptr [0x438050]
00437bf4 fxch    st(1)
00437bf6 fucompp
00437bf8 fnstsw  ax
00437bfa test    ah, 5
00437bfd jp      0x437c61
00437bff lea     eax, [ebp - 0x1c]
00437c02 call    0x4032dc
00437c07 test    al, al
00437c09 jne     0x437c61
00437c0b push    1
00437c0d mov     word ptr [ebp - 0x74], 0xb4
00437c13 mov     edx, 0x6cefec
00437c18 lea     eax, [ebp - 0x4c]
00437c1b call    0x6bf0b0
00437c20 inc     dword ptr [ebp - 0x68]
00437c23 lea     edx, [ebp - 0x4c]
00437c26 push    edx
00437c27 mov     edx, dword ptr [ebp - 0x88]
00437c2d add     edx, 0x294
00437c33 mov     eax, dword ptr [ebp - 0x88]
00437c39 add     eax, 0x158
00437c3e call    0x402ca8
00437c43 mov     edx, eax
00437c45 mov     eax, dword ptr [ebp - 0x88]
00437c4b pop     ecx
00437c4c call    0x403318
00437c51 dec     dword ptr [ebp - 0x68]
00437c54 lea     eax, [ebp - 0x4c]
00437c57 mov     edx, 2
00437c5c call    0x6bf114
00437c61 mov     byte ptr [ebp - 0xb1], 0
00437c68 mov     word ptr [ebp - 0x74], 0x6c
00437c6e mov     ecx, dword ptr [ebp - 0x90]
00437c74 fld     dword ptr [ecx + 0x20]
00437c77 fmul    dword ptr [0x43802c]
00437c7d fadd    dword ptr [0x438054]
00437c83 call    0x6b70b8
00437c88 mov     dword ptr [ebp - 0xb8], eax
00437c8e cmp     dword ptr [ebp - 0xb8], 0xb4
00437c98 jge     0x437ca1
00437c9a mov     byte ptr [ebp - 0xb1], 1
00437ca1 cmp     byte ptr [ebp - 0xb1], 0
00437ca8 je      0x437d0c
00437caa lea     eax, [ebp - 0x1c]
00437cad call    0x4032dc
00437cb2 test    al, al
00437cb4 jne     0x437d0c
00437cb6 push    1
00437cb8 mov     word ptr [ebp - 0x74], 0xc0
00437cbe mov     edx, 0x6cefee
00437cc3 lea     eax, [ebp - 0x50]
00437cc6 call    0x6bf0b0
00437ccb inc     dword ptr [ebp - 0x68]
00437cce lea     edx, [ebp - 0x50]
00437cd1 push    edx
00437cd2 mov     edx, dword ptr [ebp - 0x88]
00437cd8 add     edx, 0x298
00437cde mov     eax, dword ptr [ebp - 0x88]
00437ce4 add     eax, 0x158
00437ce9 call    0x402ca8
00437cee mov     edx, eax
00437cf0 mov     eax, dword ptr [ebp - 0x88]
00437cf6 pop     ecx
00437cf7 call    0x403318
