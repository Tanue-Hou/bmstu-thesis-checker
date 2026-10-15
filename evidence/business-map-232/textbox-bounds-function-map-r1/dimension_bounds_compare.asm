0041d537 fld dword ptr [ebp - 0xcc]
0041d53d fadd dword ptr [0x41dc10]
0041d543 mov eax, dword ptr [ebp - 0xbc]
0041d549 fld dword ptr [eax + 0x100]
0041d54f fxch st(1)
0041d551 fucompp 
0041d553 fnstsw ax
0041d555 test ah, 5
0041d558 jnp 0x41d581
0041d55a fld dword ptr [ebp - 0xd0]
0041d560 fsub dword ptr [0x41dc10]
0041d566 mov edx, dword ptr [ebp - 0xbc]
0041d56c fld dword ptr [edx + 0x104]
0041d572 fxch st(1)
0041d574 fucompp 
0041d576 fnstsw ax
0041d578 test ah, 5
0041d57b jp 0x41d645
