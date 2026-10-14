/* RECOVERED PSEUDOCODE, not original source; 004374e3 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

float10 __cdecl
FUN_004374e3(int nmsedec,int compno,int level,int orient,int bpno,int qmfbid,double stepsize,
            int numcomps,double *mct_norms,int mct_numcomps)

{
  double dVar1;
  longdouble lVar2;
  double local_14;
  undefined4 local_c;
  undefined4 uStack_8;
  
  local_c = 0;
  uStack_8 = 0x3ff00000;
  if ((mct_norms != (double *)0x0) && ((uint)compno < (uint)mct_numcomps)) {
    local_c = *(undefined4 *)(mct_norms + compno);
    uStack_8 = *(undefined4 *)((int)mct_norms + compno * 8 + 4);
  }
  if (qmfbid == 1) {
    lVar2 = (longdouble)FUN_0041ae88(level,orient);
  }
  else {
    lVar2 = (longdouble)FUN_0041aebe(level,orient);
  }
  local_14 = (double)lVar2;
  dVar1 = (double)(1 << ((byte)bpno & 0x1f)) *
          (double)CONCAT44(uStack_8,local_c) * local_14 * stepsize;
  return (float10)(longdouble)((double)nmsedec * dVar1 * (double)_DAT_0043757b * dVar1);
}

