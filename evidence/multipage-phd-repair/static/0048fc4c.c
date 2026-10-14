/* ENTRY 0048fc4c NAME FUN_0048fc4c */

void FUN_0048fc4c(int param_1)

{
  char cVar1;
  ushort *puVar2;
  undefined2 *puVar3;
  short *psVar4;
  int iVar5;
  int *piVar6;
  int *piVar7;
  undefined4 *in_FS_OFFSET;
  byte bVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  undefined1 *puVar11;
  int local_374 [100];
  ushort auStack_1e4 [100];
  int local_11c;
  int local_118;
  int local_114;
  int local_110;
  char local_101;
  int local_100;
  int local_fc;
  int local_f8;
  int *local_f4;
  int local_f0;
  int local_ec;
  int local_e8;
  int local_e4;
  int local_e0;
  int local_dc;
  char local_d5;
  int local_d4;
  char local_cd;
  undefined4 local_cc;
  int local_c8;
  int local_c4;
  int local_c0;
  ushort local_bc;
  ushort local_ba;
  int local_b8;
  undefined4 local_b4;
  undefined2 local_a4;
  int local_98;
  undefined4 local_90;
  undefined1 local_8c [4];
  undefined1 local_88 [4];
  undefined1 local_84 [4];
  undefined1 local_80 [4];
  undefined1 local_7c [4];
  undefined1 local_78 [4];
  undefined1 local_74 [4];
  undefined1 local_70 [4];
  int *local_6c;
  int local_68;
  undefined1 local_64 [4];
  undefined1 local_60 [4];
  undefined1 local_5c [4];
  undefined1 local_58 [4];
  undefined1 local_54 [4];
  undefined1 local_50 [4];
  undefined1 local_4c [4];
  undefined4 local_48;
  undefined1 local_44 [4];
  undefined4 local_40;
  undefined1 local_3c [4];
  undefined1 local_38 [4];
  undefined1 local_34 [4];
  undefined1 local_30 [4];
  undefined1 local_2c [4];
  undefined1 local_28 [4];
  undefined1 local_24 [4];
  undefined1 local_20 [4];
  undefined1 local_1c [4];
  undefined1 local_18 [4];
  undefined1 local_14 [4];
  undefined1 local_10 [4];
  undefined1 local_c [4];
  undefined1 local_8 [4];
  
  bVar8 = 0;
  local_b8 = param_1;
  FUN_006ad628(&DAT_006e0abc);
  local_ba = 0x2d;
  piVar6 = &DAT_006dd02c;
  piVar7 = local_374;
  for (iVar5 = 100; iVar5 != 0; iVar5 = iVar5 + -1) {
    *piVar7 = *piVar6;
    piVar6 = piVar6 + (uint)bVar8 * -2 + 1;
    piVar7 = piVar7 + (uint)bVar8 * -2 + 1;
  }
  local_c0 = 0;
  local_a4 = 0x18;
  FUN_0046fa54(local_8);
  local_98 = local_98 + 1;
  local_a4 = 0x30;
  FUN_0046fa54(local_c);
  local_98 = local_98 + 1;
  local_a4 = 0x3c;
  FUN_0046fa54(local_10);
  local_98 = local_98 + 1;
  local_a4 = 0x48;
  FUN_0046fa54(local_14);
  local_98 = local_98 + 1;
  local_d4 = 0;
  local_a4 = 0x24;
  while (iVar5 = (**(code **)(**(int **)(local_b8 + 0x924) + 0x14))(), local_d4 < iVar5 + -1) {
    local_a4 = 0x54;
    uVar9 = FUN_0046fa54(local_18);
    local_98 = local_98 + 1;
    (**(code **)(**(int **)(local_b8 + 0x924) + 0xc))(*(int **)(local_b8 + 0x924),local_d4,uVar9);
    FUN_006bf0d8(local_8,local_18);
    local_98 = local_98 + -1;
    FUN_006bf0b0(local_18,2);
    iVar5 = FUN_00476b14(local_8);
    if (9 < iVar5) {
      uVar9 = FUN_00476b14(local_8);
      puVar2 = (ushort *)FUN_0047699c(local_8,uVar9);
      local_bc = *puVar2;
      if ((((local_bc < 0x20) || (0x7d < local_bc)) && ((local_bc < 0x410 || (0x44f < local_bc))))
         || (local_bc == 0x2d)) {
        local_cd = '\x01';
      }
      else {
        local_cd = '\0';
      }
      if (local_cd != '\0') {
        uVar9 = FUN_00476b14(local_8);
        FUN_006bf280(local_8,uVar9,1);
        for (local_c4 = FUN_00476b14(local_8); 0 < local_c4; local_c4 = local_c4 + -1) {
          puVar3 = (undefined2 *)FUN_0047699c(local_8,local_c4);
          cVar1 = FUN_0049fa04(*puVar3);
          if (cVar1 == '\0') break;
        }
        local_a4 = 0x60;
        uVar9 = FUN_0046fa54(local_1c);
        local_98 = local_98 + 1;
        FUN_006bf458(local_8,local_c4 + 1,100,uVar9);
        FUN_006bf0d8(local_10,local_1c);
        local_98 = local_98 + -1;
        FUN_006bf0b0(local_1c,2);
        cVar1 = FUN_00476b58(local_10);
        if (cVar1 == '\0') {
          local_a4 = 0x6c;
          uVar9 = FUN_0046fa54(local_20);
          local_98 = local_98 + 1;
          (**(code **)(**(int **)(local_b8 + 0x924) + 0xc))
                    (*(int **)(local_b8 + 0x924),local_d4 + 1,uVar9);
          FUN_006bf0d8(local_c,local_20);
          local_98 = local_98 + -1;
          FUN_006bf0b0(local_20,2);
          cVar1 = FUN_00476b58(local_c);
          if (cVar1 == '\0') {
            local_c4 = 1;
            while (iVar5 = FUN_00476b14(local_c), local_c4 <= iVar5) {
              puVar3 = (undefined2 *)FUN_0047699c(local_c,local_c4);
              cVar1 = FUN_0049fa04(*puVar3);
              if (cVar1 == '\0') break;
              local_c4 = local_c4 + 1;
            }
            if (local_c4 != 1) {
              local_a4 = 0x78;
              uVar9 = FUN_0046fa54(local_24);
              local_98 = local_98 + 1;
              FUN_006bf458(local_c,1,local_c4 + -1,uVar9);
              FUN_006bf0ec(local_10,local_24);
              local_98 = local_98 + -1;
              FUN_006bf0b0(local_24,2);
              local_a4 = 0x84;
              uVar9 = FUN_0046fa54(local_28);
              local_98 = local_98 + 1;
              FUN_006bf2b4(local_10,uVar9);
              FUN_006bf0d8(local_10,local_28);
              local_98 = local_98 + -1;
              FUN_006bf0b0(local_28,2);
              local_cc = 0;
              local_c8 = FUN_004d2310(&DAT_00734cb0,local_10,local_14,&local_cc);
              if (local_c8 != 0) {
                local_d5 = '\0';
                local_dc = 0;
                local_a4 = 0x24;
                if (0 < local_c0) {
                  do {
                    if (auStack_1e4[local_dc] == local_bc) {
                      local_374[local_dc] = local_374[local_dc] + 1;
                      local_d5 = '\x01';
                      break;
                    }
                    local_dc = local_dc + 1;
                  } while (local_dc < local_c0);
                }
                if ((local_d5 == '\0') && (local_c0 < 100)) {
                  auStack_1e4[local_c0] = local_bc;
                  local_c0 = local_c0 + 1;
                }
              }
            }
          }
        }
      }
    }
    local_d4 = local_d4 + 1;
  }
  local_e0 = 0;
  local_e4 = 0;
  local_a4 = 0x24;
  if (0 < local_c0) {
    do {
      if (local_e0 < local_374[local_e4]) {
        (**(code **)(**(int **)(local_b8 + 0x924) + 0x14))();
        iVar5 = FUN_006b7054();
        if (iVar5 < local_374[local_e4]) {
          local_e0 = local_374[local_e4];
          local_ba = auStack_1e4[local_e4];
        }
      }
      local_e4 = local_e4 + 1;
    } while (local_e4 < local_c0);
  }
  if (local_ba != 0) {
    local_e8 = 0;
    local_a4 = 0x24;
    while (iVar5 = (**(code **)(**(int **)(local_b8 + 0x924) + 0x14))(), local_e8 < iVar5 + -1) {
      local_a4 = 0x90;
      uVar9 = FUN_0046fa54(local_2c);
      local_98 = local_98 + 1;
      (**(code **)(**(int **)(local_b8 + 0x924) + 0xc))(*(int **)(local_b8 + 0x924),local_e8,uVar9);
      FUN_006bf0d8(local_8,local_2c);
      local_98 = local_98 + -1;
      FUN_006bf0b0(local_2c,2);
      cVar1 = FUN_00476b58(local_8);
      if (cVar1 == '\0') {
        uVar9 = FUN_00476b14(local_8);
        puVar2 = (ushort *)FUN_0047699c(local_8,uVar9);
        if (*puVar2 == local_ba) {
          uVar9 = FUN_00476b14(local_8);
          FUN_006bf280(local_8,uVar9,1);
          for (local_c4 = FUN_00476b14(local_8); 0 < local_c4; local_c4 = local_c4 + -1) {
            puVar3 = (undefined2 *)FUN_0047699c(local_8,local_c4);
            cVar1 = FUN_0049fa04(*puVar3);
            if (cVar1 == '\0') break;
          }
          local_a4 = 0x9c;
          uVar9 = FUN_0046fa54(local_30);
          local_98 = local_98 + 1;
          FUN_006bf458(local_8,local_c4 + 1,100,uVar9);
          FUN_006bf0d8(local_10,local_30);
          local_98 = local_98 + -1;
          FUN_006bf0b0(local_30,2);
          cVar1 = FUN_00476b58(local_10);
          if (cVar1 == '\0') {
            local_a4 = 0x24;
            local_ec = local_e8;
            do {
              do {
                local_ec = local_ec + 1;
                iVar5 = (**(code **)(**(int **)(local_b8 + 0x924) + 0x14))();
                if (iVar5 <= local_ec) goto LAB_00490545;
                local_a4 = 0xa8;
                uVar9 = FUN_0046fa54(local_34);
                local_98 = local_98 + 1;
                (**(code **)(**(int **)(local_b8 + 0x924) + 0xc))
                          (*(int **)(local_b8 + 0x924),local_ec,uVar9);
                FUN_006bf0d8(local_c,local_34);
                local_98 = local_98 + -1;
                FUN_006bf0b0(local_34,2);
                if (local_e8 + 3 < local_ec) goto LAB_00490545;
                cVar1 = FUN_00476b58(local_c);
              } while (cVar1 != '\0');
              local_c4 = 1;
              while (iVar5 = FUN_00476b14(local_c), local_c4 <= iVar5) {
                puVar3 = (undefined2 *)FUN_0047699c(local_c,local_c4);
                cVar1 = FUN_0049fa04(*puVar3);
                if (cVar1 == '\0') break;
                local_c4 = local_c4 + 1;
              }
            } while (local_c4 == 1);
            local_a4 = 0xb4;
            uVar9 = FUN_0046fa54(local_38);
            local_98 = local_98 + 1;
            FUN_006bf458(local_c,1,local_c4 + -1,uVar9);
            FUN_006bf0ec(local_10,local_38);
            local_98 = local_98 + -1;
            FUN_006bf0b0(local_38,2);
            local_a4 = 0xc0;
            uVar9 = FUN_0046fa54(local_3c);
            local_98 = local_98 + 1;
            FUN_006bf2b4(local_10,uVar9);
            FUN_006bf0d8(local_10,local_3c);
            local_98 = local_98 + -1;
            FUN_006bf0b0(local_3c,2);
            local_cc = 0;
            local_c8 = FUN_004d2310(&DAT_00734cb0,local_10,local_14,&local_cc);
            if (local_c8 != 0) {
              local_f0 = local_e8 + 1;
              local_a4 = 0x24;
              if (local_f0 < local_ec) {
                do {
                  (**(code **)(**(int **)(local_b8 + 0x924) + 0x48))
                            (*(int **)(local_b8 + 0x924),local_e8 + 1);
                  local_f0 = local_f0 + 1;
                } while (local_f0 < local_ec);
              }
              local_a4 = 0xcc;
              uVar9 = FUN_0046fa54(&local_40);
              local_98 = local_98 + 1;
              FUN_006bf100(local_8,local_c,uVar9);
              (**(code **)(**(int **)(local_b8 + 0x924) + 0x20))
                        (*(int **)(local_b8 + 0x924),local_e8,local_40);
              local_98 = local_98 + -1;
              FUN_006bf0b0(&local_40,2);
              iVar5 = local_e8 + 1;
              local_e8 = local_e8 + -1;
              (**(code **)(**(int **)(local_b8 + 0x924) + 0x48))(*(int **)(local_b8 + 0x924),iVar5);
            }
          }
        }
      }
LAB_00490545:
      local_e8 = local_e8 + 1;
    }
  }
  local_f4 = (int *)FUN_005405fc(PTR_PTR_00534324,1);
  local_f8 = 0;
  local_a4 = 0x24;
  while (iVar5 = (**(code **)(**(int **)(local_b8 + 0x924) + 0x14))(), local_f8 < iVar5) {
    local_a4 = 0xd8;
    uVar9 = FUN_0046fa54(local_44);
    local_98 = local_98 + 1;
    (**(code **)(**(int **)(local_b8 + 0x924) + 0xc))(*(int **)(local_b8 + 0x924),local_f8,uVar9);
    puVar11 = local_44;
    uVar9 = FUN_0046fa54(&local_48);
    local_98 = local_98 + 1;
    FUN_006bf2b4(puVar11,uVar9);
    (**(code **)(*local_f4 + 0x38))(local_f4,local_48);
    local_98 = local_98 + -1;
    FUN_006bf0b0(&local_48,2);
    local_98 = local_98 + -1;
    FUN_006bf0b0(local_44,2);
    local_f8 = local_f8 + 1;
  }
  local_a4 = 0xe4;
  FUN_006bf04c(local_4c,&DAT_006de020);
  local_98 = local_98 + 1;
  puVar11 = local_4c;
  uVar10 = 0;
  uVar9 = 1;
  iVar5 = (**(code **)(*local_f4 + 0x14))();
  local_fc = FUN_00495ee8(local_f4,iVar5 + -1,0,uVar9,uVar10,puVar11);
  local_98 = local_98 + -1;
  FUN_006bf0b0(local_4c,2);
  local_100 = -1;
  if (local_fc != -1) {
    local_a4 = 0xf0;
    FUN_0046fa54(local_50);
    local_98 = local_98 + 1;
    local_a4 = 0x108;
    FUN_0046fa54(local_54);
    local_98 = local_98 + 1;
    local_a4 = 0xfc;
    local_101 = '\0';
    local_110 = (**(code **)(*local_f4 + 0x14))();
    local_110 = local_110 + -1;
    while( true ) {
      local_a4 = 0x114;
      FUN_006bf04c(local_58,&DAT_006de062);
      local_98 = local_98 + 1;
      local_100 = FUN_00495ee8(local_f4,local_110,local_fc,1,1,local_58);
      local_98 = local_98 + -1;
      FUN_006bf0b0(local_58,2);
      if (local_100 == -1) break;
      local_a4 = 0x120;
      uVar9 = FUN_0046fa54(local_60);
      local_98 = local_98 + 1;
      uVar10 = FUN_0046fa54(local_5c);
      local_98 = local_98 + 1;
      (**(code **)(*local_f4 + 0xc))(local_f4,local_100,uVar10,uVar9);
      FUN_006bf458(local_5c,0xb,0x14,uVar9);
      puVar11 = local_60;
      uVar9 = FUN_0046fa54(local_64);
      local_98 = local_98 + 1;
      FUN_006bf3cc(puVar11,uVar9);
      FUN_006bf0d8(local_50,local_64);
      local_98 = local_98 + -1;
      FUN_006bf0b0(local_64,2);
      local_98 = local_98 + -1;
      FUN_006bf0b0(local_60,2);
      local_98 = local_98 + -1;
      FUN_006bf0b0(local_5c,2);
      iVar5 = FUN_00476b14(local_50);
      if (iVar5 == 1) {
        psVar4 = (short *)FUN_0047699c(local_50,1);
        if ((*psVar4 == 0x430) || (psVar4 = (short *)FUN_0047699c(local_50,1), *psVar4 == 0x61)) {
          local_101 = '\x01';
        }
        else {
          local_110 = local_100 + -1;
        }
      }
      else {
        local_110 = local_100 + -1;
      }
      if ((local_110 < 1) || (local_101 != '\0')) break;
    }
    if (local_100 == -1) {
      local_100 = (**(code **)(*local_f4 + 0x14))();
    }
    local_98 = local_98 + -1;
    FUN_006bf0b0(local_54,2);
    local_98 = local_98 + -1;
    FUN_006bf0b0(local_50,2);
  }
  local_a4 = 0x24;
  local_6c = local_f4;
  if (local_f4 != (int *)0x0) {
    local_68 = *local_f4;
    local_a4 = 0x144;
    (**(code **)(*local_f4 + -4))(local_f4,3);
    local_a4 = 300;
  }
  if (((0 < local_fc) && (0 < local_100)) && (local_fc < local_100)) {
    local_a4 = 0x150;
    FUN_0046fa54(local_70);
    local_98 = local_98 + 1;
    local_a4 = 0x168;
    FUN_0046fa54(local_74);
    local_98 = local_98 + 1;
    local_a4 = 0x15c;
    local_11c = local_fc;
    while (local_11c = local_11c + 1, local_11c < local_100 + -1) {
      local_a4 = 0x174;
      uVar9 = FUN_0046fa54(local_78);
      local_98 = local_98 + 1;
      (**(code **)(**(int **)(local_b8 + 0x924) + 0xc))(*(int **)(local_b8 + 0x924),local_11c,uVar9)
      ;
      puVar11 = local_78;
      uVar9 = FUN_0046fa54(local_7c);
      local_98 = local_98 + 1;
      FUN_006bf3cc(puVar11,uVar9);
      FUN_006bf0d8(local_70,local_7c);
      local_98 = local_98 + -1;
      FUN_006bf0b0(local_7c,2);
      local_98 = local_98 + -1;
      FUN_006bf0b0(local_78,2);
      cVar1 = FUN_00476b58(local_70);
      if (cVar1 == '\0') {
        FUN_00476b38(local_70);
        local_114 = FUN_006b8b30();
        if (local_114 != 0) {
          local_a4 = 0x180;
          uVar9 = FUN_0046fa54(local_80);
          local_98 = local_98 + 1;
          (**(code **)(**(int **)(local_b8 + 0x924) + 0xc))
                    (*(int **)(local_b8 + 0x924),local_11c + 1,uVar9);
          puVar11 = local_80;
          uVar9 = FUN_0046fa54(local_84);
          local_98 = local_98 + 1;
          FUN_006bf3cc(puVar11,uVar9);
          FUN_006bf0d8(local_74,local_84);
          local_98 = local_98 + -1;
          FUN_006bf0b0(local_84,2);
          local_98 = local_98 + -1;
          FUN_006bf0b0(local_80,2);
          cVar1 = FUN_00476b58(local_74);
          if (cVar1 == '\0') {
            uVar9 = FUN_00476b38(local_74);
            local_118 = FUN_006b8b30();
            if ((local_118 < 1) ||
               (iVar5 = FUN_00490c94(local_118,(local_114 + 1) - local_118,uVar9), 2 < iVar5)) {
              local_a4 = 0x18c;
              uVar9 = FUN_0046fa54(local_8c);
              local_98 = local_98 + 1;
              FUN_006bf04c(local_88,&DAT_006de078);
              local_98 = local_98 + 1;
              FUN_006bf100(local_70,local_88,uVar9);
              puVar11 = local_8c;
              uVar9 = FUN_0046fa54(&local_90);
              local_98 = local_98 + 1;
              FUN_006bf100(puVar11,local_74,uVar9);
              (**(code **)(**(int **)(local_b8 + 0x924) + 0x20))
                        (*(int **)(local_b8 + 0x924),local_11c,local_90);
              local_98 = local_98 + -1;
              FUN_006bf0b0(&local_90,2);
              local_98 = local_98 + -1;
              FUN_006bf0b0(local_8c,2);
              local_98 = local_98 + -1;
              FUN_006bf0b0(local_88,2);
              (**(code **)(**(int **)(local_b8 + 0x924) + 0x48))
                        (*(int **)(local_b8 + 0x924),local_11c + 1);
              local_11c = local_11c + -1;
              local_100 = local_100 + -1;
            }
          }
        }
      }
    }
    local_98 = local_98 + -1;
    FUN_006bf0b0(local_74,2);
    local_98 = local_98 + -1;
    FUN_006bf0b0(local_70,2);
    local_a4 = 0x24;
  }
  local_98 = local_98 + -1;
  FUN_006bf0b0(local_14,2);
  local_98 = local_98 + -1;
  FUN_006bf0b0(local_10,2);
  local_98 = local_98 + -1;
  FUN_006bf0b0(local_c,2);
  local_98 = local_98 + -1;
  FUN_006bf0b0(local_8,2);
  *in_FS_OFFSET = local_b4;
  return;
}


