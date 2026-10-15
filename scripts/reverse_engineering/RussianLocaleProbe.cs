// Dedicated child launcher for the CLI debugger. Never changes system locale.
using System;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
class RussianLocaleProbe {
  [DllImport("kernel32.dll",CharSet=CharSet.Unicode,SetLastError=true)] static extern bool SetDllDirectory(string path);
  static int Main(string[] args) {
    if(args.Length!=3 && args.Length!=4) return 2;
    try { return Run(args); }
    catch(Exception error) { File.WriteAllText(Path.Combine(args[2],"loader-error.txt"),error.ToString());return 5; }
  }
  static int Run(string[] args) {
    string folder=Path.GetFullPath(args[0]);
    if(!SetDllDirectory(folder)) return 3;
    var assembly=Assembly.LoadFrom(Path.Combine(folder,"LEProc.exe"));
    var type=assembly.GetType("LEProc.LoaderWrapper",true);
    var instance=Activator.CreateInstance(type,true);
    Action<string,object> set=(name,value)=>type.GetProperty(name,BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance).SetValue(instance,value,null);
    set("ApplicationName",Path.GetFullPath(args[1]));
    set("CommandLine","\""+Path.GetFullPath(args[1])+"\" --help");
    set("CurrentDirectory",Path.GetFullPath(args[2]));
    set("AnsiCodePage",(uint)1251);set("OemCodePage",(uint)866);
    set("LocaleID",(uint)1049);set("DefaultCharset",(uint)204);
    set("HookUILanguageAPI",(uint)0);set("Timezone","Russian Standard Time");
    set("NumberOfRegistryRedirectionEntries",0);set("DebugMode",args.Length==4 && args[3]=="suspended");
    uint result=(uint)type.GetMethod("Start",BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance).Invoke(instance,null);
    File.WriteAllText(Path.Combine(args[2],"loader-result.txt"),result.ToString());
    Console.WriteLine("Loader result: "+result);
    return result==0?0:4;
  }
}
