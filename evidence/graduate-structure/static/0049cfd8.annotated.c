/* ENTRY 0049cfd8 NAME FUN_0049cfd8 */

void FUN_0049cfd8(int *param_1,int param_2,undefined4 param_3)

{
  char cVar1;
  int *piVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 *in_FS_OFFSET;
  int local_58;
  undefined4 local_44;
  undefined1 local_18 [4];
  undefined1 local_14 [4];
  undefined1 local_10 [4];
  undefined1 local_c [4];
  undefined4 local_8;
  
  FUN_006ad628(&DAT_006e708c);
  FUN_006bf04c(local_c,&DAT_006e4a3a);
  cVar1 = FUN_006bf190(param_2 + 0x6c,local_c);
  FUN_006bf0b0(local_c,2);
  if (cVar1 != '\0') {
    cVar1 = FUN_00476b58(param_2 + 0x74);
    if (cVar1 == '\0') {
      FUN_00495584(param_2);
    }
    else {
      FUN_00494dd0(param_2);
    }
  }
  piVar2 = (int *)FUN_005405fc(PTR_PTR_00534324,1);
  FUN_0046fa54(&local_8);
  local_58 = 0;
  while( true ) {
    iVar4 = (**(code **)(*param_1 + 0x14))();
    if (iVar4 <= local_58) break;
    uVar3 = FUN_0046fa54(local_10);
    (**(code **)(*param_1 + 0xc))(param_1,local_58,uVar3);
    uVar3 = FUN_0046fa54(local_14);
    FUN_006bf2b4(local_10,uVar3);
    uVar3 = FUN_0046fa54(local_18);
    FUN_006bf3cc(local_14,uVar3);
    FUN_006bf0d8(&local_8,local_18);
    FUN_006bf0b0(local_18,2);
    FUN_006bf0b0(local_14,2);
    FUN_006bf0b0(local_10,2);
    (**(code **)(*piVar2 + 0x38))(piVar2,local_8);
    uVar3 = (**(code **)(*param_1 + 0x18))(param_1,local_58);
    iVar4 = (**(code **)(*piVar2 + 0x14))();
    (**(code **)(*piVar2 + 0x24))(piVar2,iVar4 + -1,uVar3);
    local_58 = local_58 + 1;
  }
  FUN_0049c3ec(piVar2,param_2,param_3);
  FUN_0049d1ec(piVar2,param_2,param_3);
  FUN_0049e2c4(param_1,param_2,param_3);
  FUN_006bf0b0(&local_8,2);
  if ((piVar2 != (int *)0x0) && (piVar2 != (int *)0x0)) {
    (**(code **)(*piVar2 + -4))(piVar2,3);
  }
  *in_FS_OFFSET = local_44;
  return;
}


