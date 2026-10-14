/* ENTRY 00495584 NAME FUN_00495584 */

/* WARNING: Removing unreachable block (ram,0x00495e67) */
/* WARNING: Removing unreachable block (ram,0x00495e85) */
/* WARNING: Removing unreachable block (ram,0x00495eb2) */

undefined4 FUN_00495584(int param_1)

{
  char cVar1;
  int *piVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  int *piVar6;
  int iVar7;
  undefined4 *in_FS_OFFSET;
  undefined1 *puVar8;
  undefined4 local_ac [4];
  undefined2 local_9c;
  int local_90;
  int *local_80;
  int local_7c;
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
  undefined4 local_c [2];
  
  FUN_006ad628(&DAT_006e53d0);
  cVar1 = FUN_00476b58(&DAT_00734c90);
  if (cVar1 == '\0') {
    EnterCriticalSection((LPCRITICAL_SECTION)&DAT_00734c5c);
    local_9c = 0xc;
    piVar2 = (int *)FUN_0062e938(PTR_PTR_0061f3b8,
                                 CONCAT31((int3)((uint)*(int *)PTR_DAT_0073431c >> 8),1),
                                 *(undefined4 *)(*(int *)PTR_DAT_0073431c + 0x44));
    local_9c = 0x18;
    uVar3 = FUN_0046fa54(local_14);
    local_90 = local_90 + 1;
    uVar4 = FUN_006bf04c(local_10,u_FILE_NAME__006e3a46);
    local_90 = local_90 + 1;
    FUN_006bf100(uVar4,&DAT_00734c90,uVar3);
    puVar8 = local_14;
    uVar3 = FUN_0046fa54(local_1c);
    local_90 = local_90 + 1;
    FUN_006bf04c(local_18,u_StudWorks_dsn__006e3a5c);
    local_90 = local_90 + 1;
    FUN_006bf100(puVar8,local_18,uVar3);
    puVar5 = (undefined4 *)FUN_006bed74(local_20,local_1c);
    local_90 = local_90 + 1;
    FUN_0062c640(piVar2,*puVar5);
    local_90 = local_90 + -1;
    FUN_006bedd4(local_20,2);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_1c,2);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_18,2);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_14,2);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_10,2);
    local_9c = 0x24;
    FUN_0046fa54(local_c);
    local_90 = local_90 + 1;
    local_9c = 0x30;
    FUN_00476b38(param_1 + 0x6c);
    FUN_006bf1f8();
    piVar6 = (int *)FUN_0062eacc(piVar2);
    (**(code **)(*piVar6 + 0x2c))(piVar6,local_c[0]);
    (**(code **)(*piVar2 + 0x1a8))(piVar2,1);
    iVar7 = (**(code **)(*piVar2 + 0x17c))();
    if (iVar7 == 0) {
      local_9c = 0x3c;
      puVar5 = (undefined4 *)
               FUN_006bf04c(local_24,&DAT_006e3c4c,local_ac,0,FUN_0046fb30,1,0,0,0,local_ac);
      local_90 = local_90 + 1;
      FUN_0055e6e8(PTR_PTR_00553904,1,*puVar5);
      FUN_006bd4ac();
    }
    local_9c = 0x48;
    puVar5 = (undefined4 *)FUN_006bf04c(local_28,&DAT_006e3c4e);
    local_90 = local_90 + 1;
    piVar6 = (int *)FUN_00614d88(piVar2,*puVar5);
    uVar3 = FUN_0046fa54(local_2c);
    local_90 = local_90 + 1;
    (**(code **)(*piVar6 + 0x74))(piVar6,uVar3);
    puVar8 = local_2c;
    uVar3 = FUN_0046fa54(local_30);
    local_90 = local_90 + 1;
    FUN_006bf2b4(puVar8,uVar3);
    FUN_006bf0d8(param_1 + 4,local_30);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_30,2);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_2c,2);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_28,2);
    local_9c = 0x54;
    FUN_006bf04c(local_34,&DAT_006e3c54);
    local_90 = local_90 + 1;
    iVar7 = FUN_006bf2a8(param_1 + 4,local_34);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_34,2);
    local_9c = 0x30;
    if (iVar7 != 0) {
      FUN_006bf294(param_1 + 4,iVar7 + -1);
    }
    local_9c = 0x60;
    puVar5 = (undefined4 *)FUN_006bf04c(local_38,u_DepID_006e3c58);
    local_90 = local_90 + 1;
    piVar6 = (int *)FUN_00614d88(piVar2,*puVar5);
    (**(code **)(*piVar6 + 100))();
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_38,2);
    local_9c = 0x30;
    FUN_006bf1f8();
    piVar6 = (int *)FUN_0062eacc(piVar2);
    (**(code **)(*piVar6 + 0x2c))(piVar6,local_c[0]);
    (**(code **)(*piVar2 + 0x1a8))(piVar2,1);
    iVar7 = (**(code **)(*piVar2 + 0x17c))();
    if (iVar7 == 0) {
      local_9c = 0x6c;
      puVar5 = (undefined4 *)
               FUN_006bf04c(local_3c,&DAT_006e3ede,local_ac,0,FUN_0046fb30,1,0,0,0,local_ac);
      local_90 = local_90 + 1;
      FUN_0055e6e8(PTR_PTR_00553904,1,*puVar5);
      FUN_006bd4ac();
    }
    local_9c = 0x78;
    puVar5 = (undefined4 *)FUN_006bf04c(local_40,u_FacName_006e3ee0);
    local_90 = local_90 + 1;
    piVar6 = (int *)FUN_00614d88(piVar2,*puVar5);
    uVar3 = FUN_0046fa54(local_44);
    local_90 = local_90 + 1;
    (**(code **)(*piVar6 + 0x74))(piVar6,uVar3);
    FUN_006bf0d8(param_1 + 8,local_44);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_44,2);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_40,2);
    local_9c = 0x84;
    puVar5 = (undefined4 *)FUN_006bf04c(local_48,u_DepName_006e3ef0);
    local_90 = local_90 + 1;
    piVar6 = (int *)FUN_00614d88(piVar2,*puVar5);
    uVar3 = FUN_0046fa54(local_4c);
    local_90 = local_90 + 1;
    (**(code **)(*piVar6 + 0x74))(piVar6,uVar3);
    FUN_006bf0d8(param_1 + 0xc,local_4c);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_4c,2);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_48,2);
    local_9c = 0x90;
    puVar5 = (undefined4 *)FUN_006bf04c(local_50,u_DepAbbr_006e3f00);
    local_90 = local_90 + 1;
    piVar6 = (int *)FUN_00614d88(piVar2,*puVar5);
    uVar3 = FUN_0046fa54(local_54);
    local_90 = local_90 + 1;
    (**(code **)(*piVar6 + 0x74))(piVar6,uVar3);
    FUN_006bf0d8(param_1 + 0x10,local_54);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_54,2);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_50,2);
    local_9c = 0x9c;
    puVar5 = (undefined4 *)FUN_006bf04c(local_58,u_DepVkr_use_006e3f10);
    local_90 = local_90 + 1;
    piVar6 = (int *)FUN_00614d88(piVar2,*puVar5);
    uVar3 = (**(code **)(*piVar6 + 100))();
    *(undefined4 *)(param_1 + 0x144) = uVar3;
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_58,2);
    local_9c = 0xa8;
    puVar5 = (undefined4 *)FUN_006bf04c(local_5c,u_DepR_006e3f26);
    local_90 = local_90 + 1;
    piVar6 = (int *)FUN_00614d88(piVar2,*puVar5);
    uVar3 = FUN_0046fa54(local_60);
    local_90 = local_90 + 1;
    (**(code **)(*piVar6 + 0x74))(piVar6,uVar3);
    puVar8 = local_60;
    FUN_006bf04c(local_64,u_00000000000000000000000000000000_006e3f30);
    local_90 = local_90 + 1;
    cVar1 = FUN_006bf190(puVar8,local_64);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_64,2);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_60,2);
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_5c,2);
    if (cVar1 != '\0') {
      local_9c = 0xb4;
      puVar5 = (undefined4 *)FUN_006bf04c(local_68,u_DepReal_006e3fec);
      local_90 = local_90 + 1;
      piVar6 = (int *)FUN_00614d88(piVar2,*puVar5);
      uVar3 = FUN_0046fa54(local_6c);
      local_90 = local_90 + 1;
      (**(code **)(*piVar6 + 0x74))(piVar6,uVar3);
      FUN_00476b38(local_6c);
      FUN_006bf1f8();
      local_90 = local_90 + -1;
      FUN_006bf0b0(local_6c,2);
      local_90 = local_90 + -1;
      FUN_006bf0b0(local_68,2);
      piVar6 = (int *)FUN_0062eacc(piVar2);
      (**(code **)(*piVar6 + 0x2c))(piVar6,local_c[0]);
      (**(code **)(*piVar2 + 0x1a8))(piVar2,1);
      iVar7 = (**(code **)(*piVar2 + 0x17c))();
      if (iVar7 == 0) {
        local_9c = 0xc0;
        puVar5 = (undefined4 *)
                 FUN_006bf04c(local_70,&DAT_006e3ffc,local_ac,0,FUN_0046fb30,1,0,0,0,local_ac);
        local_90 = local_90 + 1;
        FUN_0055e6e8(PTR_PTR_00553904,1,*puVar5);
        FUN_006bd4ac();
      }
      local_9c = 0xcc;
      puVar5 = (undefined4 *)FUN_006bf04c(local_74,u_Name_006e3ffe);
      local_90 = local_90 + 1;
      piVar6 = (int *)FUN_00614d88(piVar2,*puVar5);
      uVar3 = FUN_0046fa54(local_78);
      local_90 = local_90 + 1;
      (**(code **)(*piVar6 + 0x74))(piVar6,uVar3);
      FUN_006bf0d8(param_1 + 0xc,local_78);
      local_90 = local_90 + -1;
      FUN_006bf0b0(local_78,2);
      local_90 = local_90 + -1;
      FUN_006bf0b0(local_74,2);
    }
    local_80 = piVar2;
    if (piVar2 != (int *)0x0) {
      local_7c = *piVar2;
      local_9c = 0xf0;
      (**(code **)(*piVar2 + -4))(piVar2,3);
      local_9c = 0xd8;
    }
    local_90 = local_90 + -1;
    FUN_006bf0b0(local_c,2);
    local_9c = 0;
    LeaveCriticalSection((LPCRITICAL_SECTION)&DAT_00734c5c);
    *in_FS_OFFSET = local_ac[0];
  }
  else {
    *in_FS_OFFSET = local_ac[0];
  }
  return local_ac[0];
}


