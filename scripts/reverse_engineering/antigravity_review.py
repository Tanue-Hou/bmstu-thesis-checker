"""Ask the user-authorized external reviewer about public static evidence only."""
import argparse,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser();p.add_argument('--model',default='gemini-3.8-flash-low');p.add_argument('--prompt-file',type=Path);p.add_argument('--out',type=Path,default=ROOT/'evidence/business-map-232/antigravity-review');a=p.parse_args()
    out=a.out.resolve()
    if not out.is_relative_to(ROOT/'evidence'):raise ValueError('Output must stay inside evidence')
    out.mkdir(exist_ok=False)
    prompt='''Read-only independent review. Do not execute commands, inspect private files, change configuration, or run the target. Use ONLY these public observations and return concise Chinese conclusions with limitations.
Target TestVkr build232, Windows x86 native PE. Export table has69 names:67 Initialize/Finalize or runtime entries, and _TstWndMain at VA0x738e1c (.data), ___CPPdebugHook at VA0x6c10ac (.data). _TstWndMain is a data export, not an executable function.
Ghidra exported10191 of10192 discovered functions. Four functions reference GetCommandLineW: runtime initialization00401c14, parameter reader00572a38, runtime init00578a50, C++ runtime init006bb0f8.
00572a38(int n,int*out): if n==0, returns GetModuleFileNameW; else GetCommandLineW and repeatedly invokes tokenizer0057297c. calls.tsv finds only one direct caller005be2c4, whose body calls00572a38(0,out). No claim that indirect callers are complete.
Native bytes contain UTF16 SkipTest strings, but not literal --help/--input or /help. This alone cannot prove switches are handled or absent.
Known work-name function0044a748 references oblique and nominative VKR token lists and diagnostic strings. It receives object-like pointers and calls virtual methods, so cannot safely be called as a plain C function without reconstructing ABI/object state.
Questions: (1) What can and cannot be concluded about an existing headless CLI? (2) Which three next static/dynamic checks offer most value? (3) Point out overclaims in treating _TstWndMain as a callable API or10191 functions as complete recovery. Return evidence vs inference vs unknown separately. No additional research or tool calls needed.'''
    if a.prompt_file:prompt=a.prompt_file.read_text(encoding='utf-8')
    (out/'prompt.txt').write_text(prompt,encoding='utf-8')
    cli=Path('C:/Users/Tanue Hou/AppData/Local/agy/bin/agy.exe')
    args=[str(cli),'--model',a.model,'--mode','plan','--sandbox','--disable-slash-commands','--print-timeout','90s','--output-format','json','--log-file',str(out/'cli.log'),'--print',prompt]
    try:
        result=subprocess.run(args,cwd=out,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
        (out/'response.json').write_text(result.stdout,encoding='utf-8')
        (out/'stderr.log').write_text(result.stderr,encoding='utf-8')
        status={'model_requested':a.model,'exit_code':result.returncode,'scope':'Public deidentified static facts only; independent model opinion is not execution evidence'}
    except subprocess.TimeoutExpired:
        status={'model_requested':a.model,'status':'timeout','scope':'No review result established'}
    (out/'receipt.json').write_text(json.dumps(status,indent=2),encoding='utf-8');print(json.dumps(status))
if __name__=='__main__':main()
