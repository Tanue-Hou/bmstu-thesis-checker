00409a8b mov eax, dword ptr [ebp - 0x3c]
00409a8e cmp dword ptr [eax + 0x94], 0
00409a95 jle 0x409b84
00409a9b mov edx, dword ptr [ebp - 0x3c]
00409a9e cmp dword ptr [edx + 0x94], 0
00409aa5 jle 0x409b1f
00409aa7 mov ecx, dword ptr [0x6e519c]
00409aad add ecx, ecx
00409aaf mov ebx, dword ptr [ebp - 0x3c]
00409ab2 cmp ecx, dword ptr [ebx + 0x94]
00409ab8 jle 0x409b1f
00409aba mov eax, dword ptr [ebp - 0x34]
00409abd cmp byte ptr [eax + 0x11d], 0
00409ac4 je 0x409b1f
00409ac6 mov edx, dword ptr [ebp - 0x3c]
00409ac9 mov ecx, dword ptr [edx + 0x94]
00409acf cmp ecx, dword ptr [0x6e519c]
00409ad5 jle 0x409afc
00409ad7 mov edx, dword ptr [ebp - 0x34]
00409ada add edx, 0x184
00409ae0 mov eax, dword ptr [ebp - 0x34]
00409ae3 add eax, 0x158
00409ae8 call 0x402ca8
00409aed mov edx, eax
00409aef mov ecx, dword ptr [ebp - 0x38]
00409af2 mov eax, dword ptr [ebp - 0x34]
00409af5 call 0x402f08
00409afa jmp 0x409b1f
00409afc mov edx, dword ptr [ebp - 0x34]
00409aff add edx, 0x188
00409b05 mov eax, dword ptr [ebp - 0x34]
00409b08 add eax, 0x158
00409b0d call 0x402ca8
00409b12 mov edx, eax
00409b14 mov ecx, dword ptr [ebp - 0x38]
00409b17 mov eax, dword ptr [ebp - 0x34]
00409b1a call 0x402f08
00409b1f mov eax, dword ptr [0x6e51a0]
00409b24 add eax, eax
00409b26 mov edx, dword ptr [ebp - 0x3c]
00409b29 cmp eax, dword ptr [edx + 0x94]
00409b2f jge 0x409b84
00409b31 mov ecx, dword ptr [ebp - 0x34]
00409b34 cmp byte ptr [ecx + 0x11d], 0
00409b3b je 0x409b84
00409b3d mov eax, dword ptr [ebp - 0x34]
00409b40 cmp dword ptr [eax + 0xc8], 0
00409b47 jne 0x409b84
00409b49 mov edx, dword ptr [ebp - 0x34]
00409b4c cmp dword ptr [edx + 0xf0], 0
00409b53 je 0x409b61
00409b55 mov ecx, dword ptr [ebp - 0x34]
00409b58 cmp dword ptr [ecx + 0x110], 0x64
00409b5f jle 0x409b84
00409b61 mov edx, dword ptr [ebp - 0x34]
00409b64 add edx, 0x18c
00409b6a mov eax, dword ptr [ebp - 0x34]
00409b6d add eax, 0x158
00409b72 call 0x402ca8
00409b77 mov edx, eax
00409b79 mov ecx, dword ptr [ebp - 0x38]
00409b7c mov eax, dword ptr [ebp - 0x34]
00409b7f call 0x402f08
