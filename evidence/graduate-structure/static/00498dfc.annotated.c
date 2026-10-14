/* ENTRY 00498dfc NAME FUN_00498dfc */

void FUN_00498dfc(undefined4 param_1,int *param_2)

{
  char cVar1;
  undefined4 uVar2;
  short *psVar3;
  undefined2 *puVar4;
  int iVar5;
  undefined4 *in_FS_OFFSET;
  int local_38;
  undefined4 local_2c;
  undefined1 local_8 [4];
  
  FUN_006ad628(&DAT_006e639c);
  uVar2 = FUN_0046fa54(local_8);
  FUN_006bf3cc(param_1,uVar2);
  FUN_006bf0d8(param_1,local_8);
  FUN_006bf0b0(local_8,2);
  *param_2 = 0;
  local_38 = 1;
  while( true ) {
    iVar5 = FUN_00476b14(param_1);
    if (iVar5 <= local_38) break;
    psVar3 = (short *)FUN_0047699c(param_1,local_38);
    if (*psVar3 == 0x20) {
      psVar3 = (short *)FUN_0047699c(param_1,local_38 + 1);
      if (*psVar3 == 0x20) {
        FUN_006bf280(param_1,local_38 + 1,1);
      }
    }
    puVar4 = (undefined2 *)FUN_0047699c(param_1,local_38);
    cVar1 = FUN_0049fa04(*puVar4);
    if (cVar1 != '\0') {
      *param_2 = *param_2 + 1;
    }
    local_38 = local_38 + 1;
  }
  *in_FS_OFFSET = local_2c;
  return;
}


