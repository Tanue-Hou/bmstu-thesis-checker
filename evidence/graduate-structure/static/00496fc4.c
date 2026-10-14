/* ENTRY 00496fc4 NAME FUN_00496fc4 */

undefined4 FUN_00496fc4(int *param_1,int *param_2,int *param_3)

{
  bool bVar1;
  bool bVar2;
  char cVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  undefined4 *in_FS_OFFSET;
  int local_b4;
  int local_ac;
  undefined4 local_9c;
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
  
  FUN_006ad628(&DAT_006e5d2c);
  local_ac = param_2[0xb];
  if (local_ac == -1) {
    local_ac = param_2[0xc];
  }
  if (local_ac == -1) {
    local_ac = param_2[0x10];
  }
  if (local_ac == -1) {
    *in_FS_OFFSET = local_9c;
    uVar4 = local_9c;
  }
  else {
    FUN_0046fa54(local_8);
    FUN_0046fa54(local_c);
    FUN_006bf04c(local_10,&DAT_006e4236);
    cVar3 = FUN_006bf190(param_2 + 0x1d,local_10);
    FUN_006bf0b0(local_10,2);
    if (cVar3 == '\0') {
      FUN_006bf04c(local_38,&DAT_006e434a);
      cVar3 = FUN_006bf184(param_2 + 0x20,local_38);
      FUN_006bf0b0(local_38,2);
      if (cVar3 == '\0') {
        FUN_006bf04c(local_40,&DAT_006e438c);
        FUN_006bf0d8(local_8,local_40);
        FUN_006bf0b0(local_40,2);
        FUN_006bf04c(local_44,&DAT_006e43d0);
        FUN_006bf0d8(local_c,local_44);
        FUN_006bf0b0(local_44,2);
      }
      else {
        FUN_006bf04c(local_3c,&DAT_006e434e);
        FUN_006bf0d8(local_8,local_3c);
        FUN_006bf0b0(local_3c,2);
      }
    }
    else {
      FUN_006bf04c(local_14,&DAT_006e4238);
      cVar3 = FUN_006bf184(param_2 + 0x1f,local_14);
      FUN_006bf0b0(local_14,2);
      if (cVar3 != '\0') {
        FUN_006bf04c(local_18,&DAT_006e4240);
        FUN_006bf0d8(local_8,local_18);
        FUN_006bf0b0(local_18,2);
      }
      FUN_006bf04c(local_1c,&DAT_006e4264);
      cVar3 = FUN_006bf184(param_2 + 0x1f,local_1c);
      FUN_006bf0b0(local_1c,2);
      if (cVar3 != '\0') {
        FUN_006bf04c(local_20,&DAT_006e426c);
        FUN_006bf0d8(local_8,local_20);
        FUN_006bf0b0(local_20,2);
      }
      FUN_006bf04c(local_24,&DAT_006e428c);
      cVar3 = FUN_006bf184(param_2 + 0x1f,local_24);
      FUN_006bf0b0(local_24,2);
      if (cVar3 != '\0') {
        FUN_006bf04c(local_28,&DAT_006e4294);
        FUN_006bf0d8(local_8,local_28);
        FUN_006bf0b0(local_28,2);
        FUN_006bf04c(local_2c,&DAT_006e42c2);
        FUN_006bf0d8(local_c,local_2c);
        FUN_006bf0b0(local_2c,2);
      }
      FUN_006bf04c(local_30,&DAT_006e4302);
      cVar3 = FUN_006bf184(param_2 + 0x1f,local_30);
      FUN_006bf0b0(local_30,2);
      if (cVar3 != '\0') {
        FUN_006bf04c(local_34,&DAT_006e430a);
        FUN_006bf0d8(local_8,local_34);
        FUN_006bf0b0(local_34,2);
      }
    }
    bVar2 = false;
    local_b4 = 0;
    if (0 < local_ac) {
      do {
        uVar4 = FUN_0046fa54(local_54);
        (**(code **)(*param_1 + 0xc))(param_1,local_b4 + 1,uVar4);
        uVar4 = FUN_0046fa54(local_48);
        (**(code **)(*param_1 + 0xc))(param_1,local_b4,uVar4);
        uVar4 = FUN_0046fa54(local_50);
        FUN_006bf04c(local_4c,&DAT_006e4414);
        FUN_006bf100(local_48,local_4c,uVar4);
        uVar4 = FUN_0046fa54(local_58);
        FUN_006bf100(local_50,local_54,uVar4);
        cVar3 = FUN_00496754(local_58,local_8);
        if (cVar3 == '\0') {
          uVar4 = FUN_0046fa54(local_68);
          (**(code **)(*param_1 + 0xc))(param_1,local_b4 + 1,uVar4);
          uVar4 = FUN_0046fa54(local_5c);
          (**(code **)(*param_1 + 0xc))(param_1,local_b4,uVar4);
          uVar4 = FUN_0046fa54(local_64);
          FUN_006bf04c(local_60,&DAT_006e4418);
          FUN_006bf100(local_5c,local_60,uVar4);
          uVar4 = FUN_0046fa54(local_6c);
          FUN_006bf100(local_64,local_68,uVar4);
          cVar3 = FUN_00496754(local_6c,local_c);
          FUN_006bf0b0(local_6c,2);
          FUN_006bf0b0(local_68,2);
          FUN_006bf0b0(local_64,2);
          FUN_006bf0b0(local_60,2);
          FUN_006bf0b0(local_5c,2);
          if (cVar3 != '\0') goto LAB_0049757e;
          bVar1 = false;
        }
        else {
LAB_0049757e:
          bVar1 = true;
        }
        FUN_006bf0b0(local_58,2);
        FUN_006bf0b0(local_54,2);
        FUN_006bf0b0(local_50,2);
        FUN_006bf0b0(local_4c,2);
        FUN_006bf0b0(local_48,2);
        if (bVar1) {
          bVar2 = true;
          break;
        }
        local_b4 = local_b4 + 1;
      } while (local_b4 < local_ac);
    }
    if (!bVar2) {
      FUN_006bf04c(local_70,&DAT_006e441c);
      cVar3 = FUN_006bf190(param_2 + 0x1d,local_70);
      FUN_006bf0b0(local_70,2);
      if (cVar3 == '\0') {
        *(int *)(*param_2 + 0x16c) = *(int *)(*param_2 + 0x16c) + 1;
        puVar5 = (undefined4 *)FUN_006bf04c(local_78,&DAT_006e44b2);
        (**(code **)(*param_3 + 0x38))(param_3,*puVar5);
        FUN_006bf0b0(local_78,2);
      }
      else {
        puVar5 = (undefined4 *)FUN_006bf04c(local_74,&DAT_006e441e);
        (**(code **)(*param_3 + 0x38))(param_3,*puVar5);
        FUN_006bf0b0(local_74,2);
      }
    }
    FUN_006bf0b0(local_c,2);
    uVar4 = FUN_006bf0b0(local_8,2);
    *in_FS_OFFSET = local_9c;
  }
  return uVar4;
}


