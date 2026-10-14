/* ENTRY 0049c3ec NAME FUN_0049c3ec */

void FUN_0049c3ec(int *param_1,int *param_2,int *param_3)

{
  short sVar1;
  bool bVar2;
  char cVar3;
  undefined4 uVar4;
  int iVar5;
  short *psVar6;
  int iVar7;
  undefined4 *puVar8;
  uint uVar9;
  undefined4 *in_FS_OFFSET;
  undefined1 *puVar10;
  int local_e4;
  int local_c8;
  int local_c4;
  int local_c0;
  int local_bc;
  int local_b8;
  undefined4 local_a8;
  undefined1 local_84 [4];
  undefined1 local_80 [4];
  undefined1 local_7c [4];
  undefined1 local_78 [4];
  undefined1 local_74 [4];
  undefined1 local_70 [4];
  undefined1 local_6c [4];
  undefined1 local_68 [4];
  undefined1 local_64 [4];
  undefined1 local_60 [4];
  undefined1 local_5c [4];
  undefined1 local_58 [4];
  undefined1 local_54 [4];
  undefined1 local_50 [4];
  undefined1 local_4c [4];
  undefined1 local_48 [4];
  undefined1 local_44 [4];
  undefined1 local_40 [4];
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
  
  FUN_006ad628(&DAT_006e6ec0);
  local_b8 = 0x3c;
  local_bc = 0;
  do {
    uVar4 = FUN_0046fa54(local_10);
    (**(code **)(*param_1 + 0xc))(param_1,local_bc,uVar4);
    puVar10 = local_10;
    uVar4 = FUN_0046fa54(local_14);
    FUN_006bf3cc(puVar10,uVar4);
    puVar10 = local_14;
    FUN_006bf04c(local_18,&DAT_006e495c);
    cVar3 = FUN_006bf184(puVar10,local_18);
    if (cVar3 == '\0') {
      uVar4 = FUN_0046fa54(local_1c);
      (**(code **)(*param_1 + 0xc))(param_1,local_bc,uVar4);
      puVar10 = local_1c;
      uVar4 = FUN_0046fa54(local_20);
      FUN_006bf3cc(puVar10,uVar4);
      puVar10 = local_20;
      FUN_006bf04c(local_24,&DAT_006e4972);
      cVar3 = FUN_006bf184(puVar10,local_24);
      uVar9 = (uint)(cVar3 != '\0');
      FUN_006bf0b0(local_24,2);
      FUN_006bf0b0(local_20,2);
      FUN_006bf0b0(local_1c,2);
      if (uVar9 != 0) goto LAB_0049c6ac;
      uVar4 = FUN_0046fa54(local_28);
      (**(code **)(*param_1 + 0xc))(param_1,local_bc,uVar4);
      puVar10 = local_28;
      uVar4 = FUN_0046fa54(local_2c);
      FUN_006bf3cc(puVar10,uVar4);
      puVar10 = local_2c;
      FUN_006bf04c(local_30,&DAT_006e4982);
      cVar3 = FUN_006bf184(puVar10,local_30);
      uVar9 = (uint)(cVar3 != '\0');
      FUN_006bf0b0(local_30,2);
      FUN_006bf0b0(local_2c,2);
      FUN_006bf0b0(local_28,2);
      if (uVar9 != 0) goto LAB_0049c6ac;
      uVar4 = FUN_0046fa54(local_34);
      (**(code **)(*param_1 + 0xc))(param_1,local_bc,uVar4);
      puVar10 = local_34;
      uVar4 = FUN_0046fa54(local_38);
      FUN_006bf3cc(puVar10,uVar4);
      puVar10 = local_38;
      FUN_006bf04c(local_3c,&DAT_006e4996);
      cVar3 = FUN_006bf184(puVar10,local_3c);
      uVar9 = (uint)(cVar3 != '\0');
      FUN_006bf0b0(local_3c,2);
      FUN_006bf0b0(local_38,2);
      FUN_006bf0b0(local_34,2);
      if (uVar9 != 0) goto LAB_0049c6ac;
      cVar3 = '\0';
    }
    else {
LAB_0049c6ac:
      cVar3 = '\x01';
    }
    FUN_006bf0b0(local_18,2);
    FUN_006bf0b0(local_14,2);
    FUN_006bf0b0(local_10,2);
    if (cVar3 != '\0') {
      local_b8 = local_bc;
      break;
    }
    local_bc = local_bc + 1;
  } while (local_bc < 100);
  FUN_0046fa54(local_8);
  FUN_0046fa54(local_c);
  FUN_006bf04c(local_40,&DAT_006e49a8);
  cVar3 = FUN_006bf184(param_2 + 0x20,local_40);
  FUN_006bf0b0(local_40,2);
  if (cVar3 == '\0') {
    FUN_006bf04c(local_48,&DAT_006e49be);
    FUN_006bf0d8(local_8,local_48);
    FUN_006bf0b0(local_48,2);
  }
  else {
    FUN_006bf04c(local_44,&DAT_006e49ac);
    FUN_006bf0d8(local_8,local_44);
    FUN_006bf0b0(local_44,2);
  }
  local_c8 = 0;
  if (0 < local_b8) {
    do {
      uVar4 = FUN_0046fa54(local_4c);
      (**(code **)(*param_1 + 0xc))(param_1,local_c8,uVar4);
      iVar5 = FUN_006bf2a8(local_4c,local_8);
      cVar3 = iVar5 != 0;
      FUN_006bf0b0(local_4c,2);
      if (cVar3 != '\0') {
        local_c0 = local_c8 + -1;
        break;
      }
      local_c8 = local_c8 + 1;
    } while (local_c8 < local_b8);
  }
  FUN_006bf04c(local_50,&DAT_006e49ce);
  FUN_006bf0d8(local_c,local_50);
  FUN_006bf0b0(local_50,2);
  for (iVar5 = local_c0; iVar5 < local_b8; iVar5 = iVar5 + 1) {
    uVar4 = FUN_0046fa54(local_54);
    (**(code **)(*param_1 + 0xc))(param_1,iVar5,uVar4);
    cVar3 = FUN_0049c37c(local_54,local_c);
    FUN_006bf0b0(local_54,2);
    if (cVar3 != '\0') {
      local_c4 = iVar5;
      if (param_2[0x2e] == 0) {
        param_2[0xb] = iVar5 + 3;
      }
      break;
    }
  }
  if (param_2[0x2e] == 0) {
    FUN_006bf04c(local_58,&DAT_006e49e8);
    FUN_006bf0d8(local_c,local_58);
    FUN_006bf0b0(local_58,2);
    for (iVar5 = local_c0; iVar5 < local_b8; iVar5 = iVar5 + 1) {
      uVar4 = FUN_0046fa54(local_5c);
      (**(code **)(*param_1 + 0xc))(param_1,iVar5,uVar4);
      cVar3 = FUN_0049c37c(local_5c,local_c);
      FUN_006bf0b0(local_5c,2);
      if (cVar3 != '\0') {
        param_2[0xb] = iVar5 + 3;
        break;
      }
    }
    FUN_006bf04c(local_60,&DAT_006e4a00);
    FUN_006bf0d8(local_c,local_60);
    FUN_006bf0b0(local_60,2);
    for (iVar5 = local_c0; iVar5 < local_b8; iVar5 = iVar5 + 1) {
      uVar4 = FUN_0046fa54(local_64);
      (**(code **)(*param_1 + 0xc))(param_1,iVar5,uVar4);
      cVar3 = FUN_0049c37c(local_64,local_c);
      FUN_006bf0b0(local_64,2);
      if (cVar3 != '\0') {
        param_2[0xb] = iVar5 + 3;
        break;
      }
    }
    FUN_006bf04c(local_68,&DAT_006e4a1e);
    FUN_006bf0d8(local_c,local_68);
    FUN_006bf0b0(local_68,2);
    for (iVar5 = local_c0; iVar5 < local_b8; iVar5 = iVar5 + 1) {
      uVar4 = FUN_0046fa54(local_6c);
      (**(code **)(*param_1 + 0xc))(param_1,iVar5,uVar4);
      cVar3 = FUN_0049c37c(local_6c,local_c);
      FUN_006bf0b0(local_6c,2);
      if (cVar3 != '\0') {
        param_2[0xb] = iVar5 + 3;
        break;
      }
    }
  }
  cVar3 = FUN_00476b58(param_2 + 1);
  if (cVar3 == '\0') {
    uVar4 = FUN_0046fa54(local_70);
    FUN_00496980(param_2 + 1,uVar4);
    bVar2 = false;
    for (; local_c0 < local_c4; local_c0 = local_c0 + 1) {
      uVar4 = FUN_0046fa54(local_74);
      (**(code **)(*param_1 + 0xc))(param_1,local_c0,uVar4);
      iVar5 = FUN_006bf2a8(local_74,local_70);
      cVar3 = iVar5 != 0;
      FUN_006bf0b0(local_74,2);
      if (cVar3 != '\0') {
        uVar4 = FUN_0046fa54(local_78);
        (**(code **)(*param_1 + 0xc))(param_1,local_c0,uVar4);
        iVar5 = FUN_00476b14(local_70);
        for (local_e4 = 1; iVar7 = FUN_00476b14(local_78), local_e4 + iVar5 + -1 <= iVar7;
            local_e4 = local_e4 + 1) {
          psVar6 = (short *)FUN_0047699c(local_78,local_e4);
          sVar1 = *psVar6;
          psVar6 = (short *)FUN_0047699c(local_70,1);
          if ((sVar1 == *psVar6) &&
             (((iVar7 = FUN_00476b14(local_78), iVar7 == local_e4 + iVar5 + -1 ||
               (psVar6 = (short *)FUN_0047699c(local_78,local_e4 + iVar5), *psVar6 == 0x20)) ||
              (psVar6 = (short *)FUN_0047699c(local_78,local_e4 + iVar5), *psVar6 == 0x5f)))) {
            uVar4 = FUN_0046fa54(local_7c);
            FUN_006bf458(local_78,local_e4,iVar5,uVar4);
            cVar3 = FUN_006bf184(local_7c,local_70);
            uVar9 = (uint)(cVar3 != '\0');
            FUN_006bf0b0(local_7c,2);
            if (uVar9 != 0) break;
          }
        }
        iVar7 = FUN_00476b14(local_78);
        if (local_e4 + iVar5 + -1 <= iVar7) {
          uVar4 = FUN_0046fa54(local_80);
          FUN_006bf458(local_78,local_e4,100,uVar4);
          FUN_006bf0d8(local_78,local_80);
          FUN_006bf0b0(local_80,2);
          FUN_006bf294(local_78,iVar5);
        }
        cVar3 = FUN_006bf184(local_78,local_70);
        if (cVar3 != '\0') {
          bVar2 = true;
          FUN_006bf0b0(local_78,2);
          break;
        }
        FUN_006bf0b0(local_78,2);
      }
    }
    if (!bVar2) {
      *(int *)(*param_2 + 0x16c) = *(int *)(*param_2 + 0x16c) + 1;
      puVar8 = (undefined4 *)FUN_006bf04c(local_84,PTR_DAT_006e1fd0);
      (**(code **)(*param_3 + 0x38))(param_3,*puVar8);
      FUN_006bf0b0(local_84,2);
    }
    FUN_006bf0b0(local_70,2);
  }
  FUN_006bf0b0(local_c,2);
  FUN_006bf0b0(local_8,2);
  *in_FS_OFFSET = local_a8;
  return;
}


