// Focused recovery of one previously timed-out function; read-only project use.
// @category TestVkr
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
public class DecompileFocused extends GhidraScript {
    public void run() throws Exception {
        String[] args=getScriptArgs();
        if(args.length!=2) throw new IllegalArgumentException("output-directory function-address");
        if(!currentProgram.getExecutableSHA256().equalsIgnoreCase("5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0")) throw new IllegalStateException("Target identity mismatch");
        Path out=Paths.get(args[0]);Files.createDirectory(out);
        Function f=currentProgram.getFunctionManager().getFunctionAt(toAddr(args[1]));
        if(f==null) throw new IllegalArgumentException("Exact function entry missing");
        DecompInterface d=new DecompInterface();d.openProgram(currentProgram);
        try {
            long start=System.currentTimeMillis();
            DecompileResults result=d.decompileFunction(f,120,monitor);
            boolean success=result.decompileCompleted() && result.getDecompiledFunction()!=null;
            String status="target_sha256="+currentProgram.getExecutableSHA256()+"\nentry="+f.getEntryPoint()+"\nbody_bytes="+f.getBody().getNumAddresses()+"\nsuccess="+success+"\nelapsed_ms="+(System.currentTimeMillis()-start)+"\nerror="+result.getErrorMessage()+"\nlimits=Recovered pseudocode, not original source; indirect calls and inferred types remain incomplete.\n";
            Files.writeString(out.resolve("status.txt"),status,StandardCharsets.UTF_8);
            if(success) Files.writeString(out.resolve("function.c"),"/* ENTRY "+f.getEntryPoint()+" NAME "+f.getName()+" */\n"+result.getDecompiledFunction().getC(),StandardCharsets.UTF_8);
            println(status);
        } finally {d.dispose();}
    }
}
