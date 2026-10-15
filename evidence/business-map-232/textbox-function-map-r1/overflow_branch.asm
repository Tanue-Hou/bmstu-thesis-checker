0041d581 mov word ptr [ebp - 0xa8], 0xd8
0041d58a mov edx, 0x6c2fd3
0041d58f lea eax, [ebp - 0x68]
0041d592 call 0x4038a8
0041d597 add dword ptr [ebp - 0x9c], 2
0041d59e lea edx, [ebp - 0x68]
0041d5a1 push edx
0041d5a2 mov ecx, dword ptr [ebp - 0xbc]
0041d5a8 push dword ptr [ecx + 0xd8]
0041d5ae mov eax, dword ptr [ebp - 0xbc]
0041d5b4 add eax, 0xd4
0041d5b9 push eax
0041d5ba call 0x403c58
0041d5bf add esp, 8
0041d5c2 add eax, 0xec
0041d5c7 pop edx
0041d5c8 call 0x405438
0041d5cd sub dword ptr [ebp - 0x9c], 2
0041d5d4 lea eax, [ebp - 0x68]
0041d5d7 mov edx, 2
0041d5dc call 0x4038e8
0041d5e1 push 1
0041d5e3 mov word ptr [ebp - 0xa8], 0xe4
0041d5ec mov edx, 0x6c2fd7
0041d5f1 lea eax, [ebp - 0x6c]
0041d5f4 call 0x6bf0b0
0041d5f9 inc dword ptr [ebp - 0x9c]
0041d5ff lea ecx, [ebp - 0x6c]
0041d602 push ecx
0041d603 mov edx, dword ptr [ebp - 0xbc]
0041d609 add edx, 0x214
0041d60f mov eax, dword ptr [ebp - 0xbc]
0041d615 add eax, 0x158
0041d61a call 0x402ca8
0041d61f mov edx, eax
0041d621 mov eax, dword ptr [ebp - 0xbc]
0041d627 pop ecx
0041d628 call 0x403318
0041d62d dec dword ptr [ebp - 0x9c]
0041d633 lea eax, [ebp - 0x6c]
0041d636 mov edx, 2
0041d63b call 0x6bf114
0041d640 jmp 0x41d866
