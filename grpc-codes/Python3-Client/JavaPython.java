
import java.io.*; 
import java.io.BufferedReader; 
import java.io.FileReader; 
import java.io.IOException;





public class JavaPython
 {

    public static void main(String[] args) throws IOException{
        // Prints "Hello, World" to the terminal window.
	System.out.println("GGG");
try{	
	String pythonScriptPath = "pre1.py";
	String[] cmd = new String[2 + args.length];
	cmd[0] = "python";
	cmd[1] = pythonScriptPath;
	 
	for(int i = 0; i < args.length; i++) {
	cmd[i+2] = args[i];
}

 
// create runtime to execute external command
Runtime rt = Runtime.getRuntime();
Process pr = rt.exec(cmd);
        
	BufferedReader reader = new BufferedReader(new InputStreamReader(pr.getInputStream()));
String line = "";
while ((line = reader.readLine()) != null) {
    System.out.println(line + "\n"+"kkk");
}
System.out.println("hello");
}
catch(Exception e)
{System.err.println(e.getMessage());
}

}
}

    


