// Controlled CLI-only message sender for a newly owned, hash-verified target.
using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
class SendOwnedDrop {
  delegate bool EnumProc(IntPtr hwnd,IntPtr data);
  [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc callback,IntPtr data);
  [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr parent,EnumProc callback,IntPtr data);
  [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr hwnd,out uint pid);
  [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int GetClassName(IntPtr hwnd,StringBuilder text,int max);
  [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int GetWindowText(IntPtr hwnd,StringBuilder text,int max);
  [DllImport("user32.dll")] static extern bool PostMessage(IntPtr hwnd,uint msg,IntPtr w,IntPtr l);
  [DllImport("user32.dll")] static extern bool ShowWindow(IntPtr hwnd,int command);
  [DllImport("user32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr SendMessageTimeout(IntPtr hwnd,uint msg,IntPtr w,IntPtr l,uint flags,uint timeout,out IntPtr result);
  [DllImport("user32.dll",EntryPoint="SendMessageTimeoutW",CharSet=CharSet.Unicode,SetLastError=true)] static extern IntPtr ReadText(IntPtr hwnd,uint msg,IntPtr w,StringBuilder l,uint flags,uint timeout,out IntPtr result);
  [DllImport("kernel32.dll")] static extern IntPtr GlobalAlloc(uint flags,UIntPtr bytes);
  [DllImport("kernel32.dll")] static extern IntPtr GlobalLock(IntPtr handle);
  [DllImport("kernel32.dll")] static extern bool GlobalUnlock(IntPtr handle);
  [DllImport("kernel32.dll")] static extern IntPtr GlobalFree(IntPtr handle);
  static string ClassName(IntPtr hwnd){var s=new StringBuilder(256);GetClassName(hwnd,s,s.Capacity);return s.ToString();}
  static int Main(string[] args){
    if(args.Length!=6 || args[4]!="instrumented-entry-v2" || (args[5]!="master" && args[5]!="phd"))return 2;
    string outDir=args[3];
    try {
      uint pid=uint.Parse(args[0]);var process=Process.GetProcessById((int)pid);
      if(!String.Equals(Path.GetFullPath(process.MainModule.FileName),Path.GetFullPath(args[1]),StringComparison.OrdinalIgnoreCase))throw new Exception("Target path mismatch");
      using(var sha=SHA256.Create())using(var file=File.OpenRead(args[1])){
        string hash=BitConverter.ToString(sha.ComputeHash(file)).Replace("-","").ToLowerInvariant();
        if(hash!="5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0")throw new Exception("Target hash mismatch");
      }
      IntPtr main=IntPtr.Zero,master=IntPtr.Zero,memo=IntPtr.Zero;
      string wanted=args[5]=="master" ? "ВКР магистра" : "НКР аспиранта";
      int modeMatches=0;
      EnumWindows((h,d)=>{uint found;GetWindowThreadProcessId(h,out found);if(found==pid && ClassName(h)=="TTstWndMain")main=h;return true;},IntPtr.Zero);
      if(main==IntPtr.Zero)throw new Exception("Owned main window missing");
      ShowWindow(main,0);
      EnumChildWindows(main,(h,d)=>{uint found;GetWindowThreadProcessId(h,out found);if(found!=pid)return true;string c=ClassName(h);var text=new StringBuilder(512);GetWindowText(h,text,text.Capacity);if(c=="TRadioButton" && text.ToString()==wanted){master=h;modeMatches++;}if(c=="TMemo")memo=h;return true;},IntPtr.Zero);
      if(modeMatches!=1 || memo==IntPtr.Zero)throw new Exception("Expected unique mode radio / memo missing");
      IntPtr modeResult;
      if(SendMessageTimeout(master,0x00f5,IntPtr.Zero,IntPtr.Zero,2,3000,out modeResult)==IntPtr.Zero)throw new Exception("Mode selection message failed");
      if(SendMessageTimeout(master,0x00f0,IntPtr.Zero,IntPtr.Zero,2,3000,out modeResult)==IntPtr.Zero || modeResult.ToInt32()!=1)throw new Exception("Requested mode was not checked");
      File.WriteAllText(Path.Combine(outDir,"selected-mode.txt"),args[5]+"\n"+wanted+"\n",new UTF8Encoding(false));
      // Signal only. The attached owned-process debugger redirects this handler
      // before it consumes HDROP, passing the native UTF-16 path object instead.
      // No cross-process global-memory ownership or DragFinish contract is used.
      if(!File.Exists(args[2]))throw new Exception("Controlled input missing");
      IntPtr result;IntPtr sent=SendMessageTimeout(main,0x0233,IntPtr.Zero,IntPtr.Zero,2,15000,out result);
      File.WriteAllText(Path.Combine(outDir,"drop-send-status.txt"),"pid="+pid+"\nmain="+main+"\nmaster="+master+"\nmemo="+memo+"\nsend_success="+(sent!=IntPtr.Zero)+"\nwin32_error="+Marshal.GetLastWin32Error()+"\n");
      if(sent==IntPtr.Zero)return 4;
      // VCL may recreate the memo HWND while changing its presentation.
      memo=IntPtr.Zero;
      EnumChildWindows(main,(h,d)=>{uint found;GetWindowThreadProcessId(h,out found);if(found==pid && ClassName(h)=="TMemo")memo=h;return true;},IntPtr.Zero);
      if(memo==IntPtr.Zero)throw new Exception("Result memo missing after check");
      if(SendMessageTimeout(memo,0x000e,IntPtr.Zero,IntPtr.Zero,2,2000,out result)==IntPtr.Zero)throw new Exception("Memo length read failed; HWND="+memo+" error="+Marshal.GetLastWin32Error());
      int length=result.ToInt32();if(length<0 || length>4000000)throw new Exception("Memo text budget exceeded");
      var content=new StringBuilder(length+1);
      if(ReadText(memo,0x000d,(IntPtr)content.Capacity,content,2,2000,out result)==IntPtr.Zero)throw new Exception("Memo text read failed");
      int copied=result.ToInt32();
      if(copied!=length || content.Length!=length)throw new Exception("Native report truncated or changed during read");
      if(SendMessageTimeout(memo,0x000e,IntPtr.Zero,IntPtr.Zero,2,2000,out result)==IntPtr.Zero || result.ToInt32()!=length)throw new Exception("Native report changed after read");
      File.WriteAllText(Path.Combine(outDir,"collection-length.txt"),length+"\n"+copied+"\n");
      File.WriteAllText(Path.Combine(outDir,"native-result.txt"),content.ToString(),new UTF8Encoding(false));return 0;
    } catch(Exception error){File.WriteAllText(Path.Combine(outDir,"drop-sender-error.txt"),error.ToString());return 5;}
  }
}
