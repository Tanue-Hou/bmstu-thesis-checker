/* ENTRY 0049e6d0 NAME FUN_0049e6d0 */

void FUN_0049e6d0(int *param_1,int *param_2,int *param_3)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  undefined4 *in_FS_OFFSET;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined1 *puVar7;
  int aiStack_114 [12];
  int local_e4;
  int local_e0;
  int local_dc;
  int local_d8;
  int local_d4;
  int local_d0;
  int local_cc;
  uint local_c8;
  int local_c4;
  int *local_c0;
  int *local_bc;
  int *local_b8;
  int *local_b4;
  undefined4 local_b0;
  undefined2 local_a0;
  int local_94;
  int *local_8c;
  int local_88;
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
  undefined4 local_8;
  
  local_bc = param_3;
  local_b8 = param_2;
  local_b4 = param_1;
  FUN_006ad628(&DAT_006e783c);
  local_c0 = (int *)0x0;
  local_a0 = 0x18;
  FUN_006bf04c(local_c,&DAT_006e4bb2);
  local_94 = local_94 + 1;
  cVar1 = FUN_006bf190(local_b8 + 0x1b,local_c);
  local_94 = local_94 + -1;
  FUN_006bf0b0(local_c,2);
  if (cVar1 != '\0') {
    cVar1 = FUN_00476b58(local_b8 + 0x1d);
    if (cVar1 == '\0') {
      FUN_00495584(local_b8);
    }
    else {
      FUN_00494dd0(local_b8);
    }
  }
  local_c0 = (int *)FUN_005405fc(PTR_PTR_00534324,1);
  local_a0 = 0x24;
  FUN_0046fa54(&local_8);
  local_94 = local_94 + 1;
  local_c4 = 0;
  local_a0 = 0x30;
  while (iVar2 = (**(code **)(*local_b4 + 0x14))(), local_c4 < iVar2) {
    local_a0 = 0x3c;
    uVar3 = FUN_0046fa54(local_10);
    local_94 = local_94 + 1;
    (**(code **)(*local_b4 + 0xc))(local_b4,local_c4,uVar3);
    puVar7 = local_10;
    uVar3 = FUN_0046fa54(local_14);
    local_94 = local_94 + 1;
    FUN_006bf2b4(puVar7,uVar3);
    puVar7 = local_14;
    uVar3 = FUN_0046fa54(local_18);
    local_94 = local_94 + 1;
    FUN_006bf3cc(puVar7,uVar3);
    FUN_006bf0d8(&local_8,local_18);
    local_94 = local_94 + -1;
    FUN_006bf0b0(local_18,2);
    local_94 = local_94 + -1;
    FUN_006bf0b0(local_14,2);
    local_94 = local_94 + -1;
    FUN_006bf0b0(local_10,2);
    (**(code **)(*local_c0 + 0x38))(local_c0,local_8);
    uVar3 = (**(code **)(*local_b4 + 0x18))(local_b4,local_c4);
    iVar2 = (**(code **)(*local_c0 + 0x14))();
    (**(code **)(*local_c0 + 0x24))(local_c0,iVar2 + -1,uVar3);
    local_c4 = local_c4 + 1;
  }
  local_a0 = 0x48;
  FUN_006bf04c(local_1c,&DAT_006e4bb4 /* UTF16 "реферат" */);
  local_94 = local_94 + 1;
  puVar7 = local_1c;
  uVar6 = 0;
  uVar5 = 0;
  uVar3 = (**(code **)(*local_c0 + 0x14))();
  iVar2 = FUN_00495ee8(local_c0,0,uVar3,uVar5,uVar6,puVar7);
  local_b8[7] = iVar2;
  local_94 = local_94 + -1;
  FUN_006bf0b0(local_1c,2);
  local_a0 = 0x54;
  FUN_006bf04c(local_20,&DAT_006e4bc4 /* UTF16 "аннотация" */);
  local_94 = local_94 + 1;
  puVar7 = local_20;
  uVar6 = 0;
  uVar5 = 0;
  uVar3 = (**(code **)(*local_c0 + 0x14))();
  iVar2 = FUN_00495ee8(local_c0,0,uVar3,uVar5,uVar6,puVar7);
  local_b8[9] = iVar2;
  local_94 = local_94 + -1;
  FUN_006bf0b0(local_20,2);
  local_a0 = 0x60;
  FUN_006bf04c(local_24,u_abstract_006e4bd8);
  local_94 = local_94 + 1;
  puVar7 = local_24;
  uVar6 = 0;
  uVar5 = 0;
  uVar3 = (**(code **)(*local_c0 + 0x14))();
  iVar2 = FUN_00495ee8(local_c0,0,uVar3,uVar5,uVar6,puVar7);
  local_b8[10] = iVar2;
  local_94 = local_94 + -1;
  FUN_006bf0b0(local_24,2);
  local_a0 = 0x6c;
  FUN_006bf04c(local_28,u_synopsis_006e4bea);
  local_94 = local_94 + 1;
  puVar7 = local_28;
  uVar6 = 0;
  uVar5 = 0;
  uVar3 = (**(code **)(*local_c0 + 0x14))();
  iVar2 = FUN_00495ee8(local_c0,0,uVar3,uVar5,uVar6,puVar7);
  local_b8[8] = iVar2;
  local_94 = local_94 + -1;
  FUN_006bf0b0(local_28,2);
  if (local_b8[7] < local_b8[9]) {
    iVar2 = local_b8[7];
  }
  else {
    iVar2 = local_b8[9];
  }
  local_b8[0xb] = iVar2;
  if (local_b8[0xb] < 0) {
    if (local_b8[9] < local_b8[7]) {
      iVar2 = local_b8[7];
    }
    else {
      iVar2 = local_b8[9];
    }
    local_b8[0xb] = iVar2;
  }
  if (local_b8[0xb] < 0) {
    uVar5 = 1;
    local_a0 = 0x78;
    FUN_006bf04c(local_2c,&DAT_006e4bfc /* UTF16 "РЕФЕРАТ (АННОТАЦИЯ)" */,local_b8,1);
    local_94 = local_94 + 1;
    puVar7 = local_2c;
    uVar3 = FUN_0047cf34(*local_b8,*local_b8 + 0x170);
    FUN_004c17c4(local_b8,uVar3,puVar7,uVar5);
    local_94 = local_94 + -1;
    FUN_006bf0b0(local_2c,2);
  }
  local_a0 = 0x84;
  FUN_006bf04c(local_30,&DAT_006e4c24);
  local_94 = local_94 + 1;
  cVar1 = FUN_006bf184(local_b8 + 0x20,local_30);
  local_94 = local_94 + -1;
  FUN_006bf0b0(local_30,2);
  if (cVar1 == '\0') {
    local_a0 = 0x9c;
    FUN_006bf04c(local_38,&DAT_006e4c3e /* UTF16 "содержание" */);
    local_94 = local_94 + 1;
    puVar7 = local_38;
    uVar6 = 0;
    uVar5 = 0;
    uVar3 = (**(code **)(*local_c0 + 0x14))();
    iVar2 = FUN_00495ee8(local_c0,0,uVar3,uVar5,uVar6,puVar7);
    local_b8[0xc] = iVar2;
    local_94 = local_94 + -1;
    FUN_006bf0b0(local_38,2);
  }
  else {
    local_a0 = 0x90;
    FUN_006bf04c(local_34,&DAT_006e4c28 /* UTF16 "оглавление" */);
    local_94 = local_94 + 1;
    puVar7 = local_34;
    uVar6 = 0;
    uVar5 = 0;
    uVar3 = (**(code **)(*local_c0 + 0x14))();
    iVar2 = FUN_00495ee8(local_c0,0,uVar3,uVar5,uVar6,puVar7);
    local_b8[0xc] = iVar2;
    local_94 = local_94 + -1;
    FUN_006bf0b0(local_34,2);
  }
  if (local_b8[0xc] == -1) {
    local_a0 = 0xa8;
    FUN_006bf04c(local_3c,&DAT_006e4c54);
    local_94 = local_94 + 1;
    uVar3 = FUN_006bf184(local_b8 + 0x20,local_3c);
    local_94 = local_94 + -1;
    FUN_006bf0b0(local_3c,2);
    if ((char)uVar3 == '\0') {
      uVar5 = 1;
      local_a0 = 0xc0;
      FUN_006bf04c(local_44,&DAT_006e4c6e /* UTF16 "СОДЕРЖАНИЕ" */,uVar3,1);
      local_94 = local_94 + 1;
      puVar7 = local_44;
      uVar3 = FUN_0047cf34(*local_b8,*local_b8 + 0x170);
      FUN_004c17c4(local_b8,uVar3,puVar7,uVar5);
      local_94 = local_94 + -1;
      FUN_006bf0b0(local_44,2);
    }
    else {
      uVar5 = 1;
      local_a0 = 0xb4;
      FUN_006bf04c(local_40,&DAT_006e4c58 /* UTF16 "ОГЛАВЛЕНИЕ" */,uVar3,1);
      local_94 = local_94 + 1;
      puVar7 = local_40;
      uVar3 = FUN_0047cf34(*local_b8,*local_b8 + 0x170);
      FUN_004c17c4(local_b8,uVar3,puVar7,uVar5);
      local_94 = local_94 + -1;
      FUN_006bf0b0(local_40,2);
    }
  }
  local_a0 = 0xcc;
  FUN_006bf04c(local_48,&DAT_006e4c84 /* UTF16 "нормативные ссылки" */);
  local_94 = local_94 + 1;
  puVar7 = local_48;
  uVar6 = 0;
  uVar5 = 0;
  uVar3 = (**(code **)(*local_c0 + 0x14))();
  iVar2 = FUN_00495ee8(local_c0,0,uVar3,uVar5,uVar6,puVar7);
  local_b8[0xd] = iVar2;
  local_94 = local_94 + -1;
  FUN_006bf0b0(local_48,2);
  local_a0 = 0xd8;
  FUN_006bf04c(local_4c,&DAT_006e4caa /* UTF16 "определения" */);
  local_94 = local_94 + 1;
  puVar7 = local_4c;
  uVar6 = 0;
  uVar5 = 0;
  uVar3 = (**(code **)(*local_c0 + 0x14))();
  iVar2 = FUN_00495ee8(local_c0,0,uVar3,uVar5,uVar6,puVar7);
  local_b8[0xe] = iVar2;
  local_94 = local_94 + -1;
  FUN_006bf0b0(local_4c,2);
  local_a0 = 0xe4;
  FUN_006bf04c(local_50,&DAT_006e4cc2 /* UTF16 "обозначения и сокращения" */);
  local_94 = local_94 + 1;
  puVar7 = local_50;
  uVar6 = 0;
  uVar5 = 0;
  uVar3 = (**(code **)(*local_c0 + 0x14))();
  iVar2 = FUN_00495ee8(local_c0,0,uVar3,uVar5,uVar6,puVar7);
  local_b8[0xf] = iVar2;
  local_94 = local_94 + -1;
  FUN_006bf0b0(local_50,2);
  local_a0 = 0xf0;
  FUN_006bf04c(local_54,&DAT_006e4cf4 /* UTF16 "введение" */);
  local_94 = local_94 + 1;
  puVar7 = local_54;
  uVar6 = 0;
  uVar5 = 0;
  uVar3 = (**(code **)(*local_c0 + 0x14))();
  iVar2 = FUN_00495ee8(local_c0,local_b8[0xc],uVar3,uVar5,uVar6,puVar7);
  local_b8[0x10] = iVar2;
  local_94 = local_94 + -1;
  FUN_006bf0b0(local_54,2);
  if (local_b8[0x10] == -1) {
    uVar5 = 1;
    local_a0 = 0xfc;
    FUN_006bf04c(local_58,&DAT_006e4d06 /* UTF16 "ВВЕДЕНИЕ" */,local_b8,1);
    local_94 = local_94 + 1;
    puVar7 = local_58;
    uVar3 = FUN_0047cf34(*local_b8,*local_b8 + 0x170);
    FUN_004c17c4(local_b8,uVar3,puVar7,uVar5);
    local_94 = local_94 + -1;
    FUN_006bf0b0(local_58,2);
  }
  local_a0 = 0x108;
  FUN_006bf04c(local_5c,&DAT_006e4d18 /* UTF16 "заключение" */);
  local_94 = local_94 + 1;
  puVar7 = local_5c;
  uVar5 = 0;
  uVar3 = 1;
  iVar2 = (**(code **)(*local_c0 + 0x14))();
  iVar2 = FUN_00495ee8(local_c0,iVar2 + -1,0,uVar3,uVar5,puVar7);
  local_b8[0x12] = iVar2;
  local_94 = local_94 + -1;
  FUN_006bf0b0(local_5c,2);
  if (local_b8[0x12] == -1) {
    uVar5 = 1;
    local_a0 = 0x114;
    FUN_006bf04c(local_60,&DAT_006e4d2e /* UTF16 "ЗАКЛЮЧЕНИЕ" */);
    local_94 = local_94 + 1;
    puVar7 = local_60;
    uVar3 = FUN_0047cf34(*local_b8,*local_b8 + 0x170,local_b8,puVar7,uVar5);
    FUN_004c17c4(local_b8,uVar3,puVar7,uVar5);
    local_94 = local_94 + -1;
    FUN_006bf0b0(local_60,2);
  }
  FUN_0049d1ec(local_c0,local_b8,local_bc);
  local_c8 = 0;
  if (local_b8[0xb] != -1) {
    aiStack_114[0] = local_b8[0xb];
    local_c8 = 1;
  }
  local_c8 = (uint)(local_b8[0xb] != -1);
  if (local_b8[0xc] != -1) {
    aiStack_114[local_c8] = local_b8[0xc];
    local_c8 = local_c8 + 1;
  }
  if (local_b8[0xd] != -1) {
    aiStack_114[local_c8] = local_b8[0xd];
    local_c8 = local_c8 + 1;
  }
  if (local_b8[0xe] != -1) {
    aiStack_114[local_c8] = local_b8[0xe];
    local_c8 = local_c8 + 1;
  }
  if (local_b8[0xf] != -1) {
    aiStack_114[local_c8] = local_b8[0xf];
    local_c8 = local_c8 + 1;
  }
  if (local_b8[0x10] != -1) {
    aiStack_114[local_c8] = local_b8[0x10];
    local_c8 = local_c8 + 1;
  }
  if (local_b8[0x12] != -1) {
    aiStack_114[local_c8] = local_b8[0x12];
    local_c8 = local_c8 + 1;
  }
  if (local_b8[0x13] != -1) {
    aiStack_114[local_c8] = local_b8[0x13];
    local_c8 = local_c8 + 1;
  }
  if (local_b8[0x15] < local_b8[0x14]) {
    local_cc = local_b8[0x14];
  }
  else {
    local_cc = local_b8[0x15];
  }
  if (local_cc != -1) {
    aiStack_114[local_c8] = local_cc;
    local_c8 = local_c8 + 1;
  }
  local_d0 = 0;
  local_a0 = 0x30;
  do {
    if ((int)(local_c8 - 1) <= local_d0) {
LAB_0049f1e7:
      FUN_0049771c(local_c0,local_b8,local_bc);
      FUN_00499268(local_c0,local_b8,local_bc);
      local_d4 = 1000;
      local_d8 = 1000;
      local_dc = 900;
      local_e0 = 0;
      local_a0 = 300;
      FUN_006bf04c(local_68,&DAT_006e4d44);
      local_94 = local_94 + 1;
      cVar1 = FUN_006bf184(local_b8 + 0x20,local_68);
      local_94 = local_94 + -1;
      FUN_006bf0b0(local_68,2);
      if (cVar1 == '\0') {
        local_a0 = 0x138;
        FUN_006bf04c(local_6c,&DAT_006e4d48);
        local_94 = local_94 + 1;
        cVar1 = FUN_006bf184(local_b8 + 0x20,local_6c);
        local_94 = local_94 + -1;
        FUN_006bf0b0(local_6c,2);
        if (cVar1 == '\0') {
          local_a0 = 0x144;
          FUN_006bf04c(local_70,&DAT_006e4d4c);
          local_94 = local_94 + 1;
          cVar1 = FUN_006bf184(local_b8 + 0x20,local_70);
          local_94 = local_94 + -1;
          FUN_006bf0b0(local_70,2);
          if (cVar1 != '\0') {
            local_e0 = 0x38;
          }
        }
        else {
          local_e0 = 0x30;
        }
      }
      else {
        local_e0 = 0x28;
      }
      if ((0 < local_b8[0x38]) && (local_b8[0x38] < local_e0)) {
        local_d4 = local_b8[0x38];
      }
      if ((0 < local_dc) && ((local_b8[0x39] + *(int *)(*local_b8 + 0x1b0)) / local_dc < local_e0))
      {
        local_d8 = (local_b8[0x39] + *(int *)(*local_b8 + 0x1b0)) / local_dc;
      }
      local_e4 = local_d8;
      if (local_d4 < local_d8) {
        local_e4 = local_d4;
      }
      local_a0 = 0x30;
      if (local_e4 == 1000) {
        local_e4 = -1;
      }
      if ((-1 < local_e4) && (local_e4 - local_e0 < 0)) {
        *(undefined4 *)(*local_b8 + 0x1ac) = 1;
        local_a0 = 0x150;
        uVar3 = FUN_0046fa54(local_7c);
        local_94 = local_94 + 1;
        FUN_0046fa84(local_78,local_e0 - local_e4);
        local_94 = local_94 + 1;
        puVar7 = local_78;
        uVar5 = FUN_006bf04c(local_74,&DAT_006e4d50 /* UTF16 "Не хватает " */);
        local_94 = local_94 + 1;
        FUN_006bf100(uVar5,puVar7,uVar3);
        puVar7 = local_7c;
        uVar3 = FUN_0046fa54(local_84);
        local_94 = local_94 + 1;
        FUN_006bf04c(local_80,&DAT_006e4d68 /* UTF16 " стр. (сначала исправьте остальные замечания, если они есть)" */);
        local_94 = local_94 + 1;
        FUN_006bf100(puVar7,local_80,uVar3);
        puVar7 = local_84;
        iVar2 = FUN_0047cf34(*local_b8,*local_b8 + 0x1ac);
        FUN_006bf0d8(iVar2 * 4 + *local_b8 + 0x1d0,puVar7);
        local_94 = local_94 + -1;
        FUN_006bf0b0(local_84,2);
        local_94 = local_94 + -1;
        FUN_006bf0b0(local_80,2);
        local_94 = local_94 + -1;
        FUN_006bf0b0(local_7c,2);
        local_94 = local_94 + -1;
        FUN_006bf0b0(local_78,2);
        local_94 = local_94 + -1;
        FUN_006bf0b0(local_74,2);
      }
      *(int *)(*local_b8 + 0x1bc) = (local_b8[0x39] + *(int *)(*local_b8 + 0x1b0)) / local_dc;
      FUN_0049e2c4(local_b4,local_b8,local_bc);
      local_94 = local_94 + -1;
      FUN_006bf0b0(&local_8,2);
      if ((local_c0 != (int *)0x0) && (local_8c = local_c0, local_c0 != (int *)0x0)) {
        local_88 = *local_c0;
        local_a0 = 0x180;
        (**(code **)(*local_c0 + -4))(local_c0,3);
      }
      *in_FS_OFFSET = local_b0;
      return;
    }
    if (aiStack_114[local_d0 + 1] <= aiStack_114[local_d0]) {
      local_a0 = 0x120;
      puVar4 = (undefined4 *)FUN_006bf04c(local_64,PTR_DAT_006e1fb8);
      local_94 = local_94 + 1;
      (**(code **)(*local_bc + 0x38))(local_bc,*puVar4);
      local_94 = local_94 + -1;
      FUN_006bf0b0(local_64,2);
      goto LAB_0049f1e7;
    }
    local_d0 = local_d0 + 1;
  } while( true );
}


