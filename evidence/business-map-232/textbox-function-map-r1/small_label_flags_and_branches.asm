0041d645 mov ecx, dword ptr [ebp - 0xbc]
0041d64b push dword ptr [ecx + 0xd8]
0041d651 mov eax, dword ptr [ebp - 0xbc]
0041d657 add eax, 0xd4
0041d65c push eax
0041d65d call 0x403c58
0041d662 add esp, 8
0041d665 cmp byte ptr [eax + 0xfc], 0
0041d66c jne 0x41d866
0041d672 mov edx, dword ptr [ebp - 0xbc]
0041d678 fld dword ptr [edx + 0x100]
0041d67e fld dword ptr [0x41dc14]
0041d684 fxch st(1)
0041d686 fucompp 
0041d688 fnstsw ax
0041d68a test ah, 5
0041d68d jp 0x41d757
0041d693 mov word ptr [ebp - 0xa8], 0xf0
0041d69c mov edx, 0x6c2fd9
0041d6a1 lea eax, [ebp - 0x70]
0041d6a4 call 0x4038a8
0041d6a9 add dword ptr [ebp - 0x9c], 2
0041d6b0 lea edx, [ebp - 0x70]
0041d6b3 push edx
0041d6b4 mov ecx, dword ptr [ebp - 0xbc]
0041d6ba push dword ptr [ecx + 0xd8]
0041d6c0 mov eax, dword ptr [ebp - 0xbc]
0041d6c6 add eax, 0xd4
0041d6cb push eax
0041d6cc call 0x403c58
0041d6d1 add esp, 8
0041d6d4 add eax, 0xec
0041d6d9 pop edx
0041d6da call 0x405438
0041d6df sub dword ptr [ebp - 0x9c], 2
0041d6e6 lea eax, [ebp - 0x70]
0041d6e9 mov edx, 2
0041d6ee call 0x4038e8
0041d6f3 push 1
0041d6f5 mov word ptr [ebp - 0xa8], 0xfc
0041d6fe mov edx, 0x6c2fdd
0041d703 lea eax, [ebp - 0x74]
0041d706 call 0x6bf0b0
0041d70b inc dword ptr [ebp - 0x9c]
0041d711 lea ecx, [ebp - 0x74]
0041d714 push ecx
0041d715 mov edx, dword ptr [ebp - 0xbc]
0041d71b add edx, 0x210
0041d721 mov eax, dword ptr [ebp - 0xbc]
0041d727 add eax, 0x158
0041d72c call 0x402ca8
0041d731 mov edx, eax
0041d733 mov eax, dword ptr [ebp - 0xbc]
0041d739 pop ecx
0041d73a call 0x403318
0041d73f dec dword ptr [ebp - 0x9c]
0041d745 lea eax, [ebp - 0x74]
0041d748 mov edx, 2
0041d74d call 0x6bf114
0041d752 jmp 0x41d866
0041d757 mov ecx, dword ptr [ebp - 0xbc]
0041d75d fld dword ptr [ecx + 0x104]
0041d763 fld dword ptr [0x41dc14]
0041d769 fxch st(1)
0041d76b fucompp 
0041d76d fnstsw ax
0041d76f test ah, 5
0041d772 jp 0x41d866
0041d778 mov edx, dword ptr [ebp - 0xbc]
0041d77e push dword ptr [edx + 0xd8]
0041d784 mov ecx, dword ptr [ebp - 0xbc]
0041d78a add ecx, 0xd4
0041d790 push ecx
0041d791 call 0x403c58
0041d796 add esp, 8
0041d799 cmp byte ptr [eax + 0xfe], 0
0041d7a0 jne 0x41d866
0041d7a6 mov word ptr [ebp - 0xa8], 0x108
0041d7af mov edx, 0x6c2fdf
0041d7b4 lea eax, [ebp - 0x78]
0041d7b7 call 0x4038a8
0041d7bc add dword ptr [ebp - 0x9c], 2
0041d7c3 lea ecx, [ebp - 0x78]
0041d7c6 push ecx
0041d7c7 mov eax, dword ptr [ebp - 0xbc]
0041d7cd push dword ptr [eax + 0xd8]
0041d7d3 mov edx, dword ptr [ebp - 0xbc]
0041d7d9 add edx, 0xd4
0041d7df push edx
0041d7e0 call 0x403c58
0041d7e5 add esp, 8
0041d7e8 add eax, 0xec
0041d7ed pop edx
0041d7ee call 0x405438
0041d7f3 sub dword ptr [ebp - 0x9c], 2
0041d7fa lea eax, [ebp - 0x78]
0041d7fd mov edx, 2
0041d802 call 0x4038e8
0041d807 push 1
0041d809 mov word ptr [ebp - 0xa8], 0x114
0041d812 mov edx, 0x6c2fe3
0041d817 lea eax, [ebp - 0x7c]
0041d81a call 0x6bf0b0
0041d81f inc dword ptr [ebp - 0x9c]
0041d825 lea ecx, [ebp - 0x7c]
0041d828 push ecx
0041d829 mov edx, dword ptr [ebp - 0xbc]
0041d82f add edx, 0x210
0041d835 mov eax, dword ptr [ebp - 0xbc]
0041d83b add eax, 0x158
0041d840 call 0x402ca8
0041d845 mov edx, eax
0041d847 mov eax, dword ptr [ebp - 0xbc]
0041d84d pop ecx
0041d84e call 0x403318
0041d853 dec dword ptr [ebp - 0x9c]
0041d859 lea eax, [ebp - 0x7c]
0041d85c mov edx, 2
0041d861 call 0x6bf114
