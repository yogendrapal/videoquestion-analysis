package com.testvideoanalysis.video;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Paths;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.testvideoanalysis.path.PathManager;

@Service
public class Analyser {
	
	@Autowired
	PathManager pathManager;
	String tags = "";
	String s;
	
	public String getTags(Video video) {
		
		String downloadPath = pathManager.getDownloadedVideos() + video.getVideoNameWithExtension();
		String jsonFilePath = pathManager.getJsonFiles() + video.getVideoName() + ".json";
        String tags = "";
        
		try {
            
			// Command in string to be run to create a new python process.
        	String command = "python3 " + pathManager.getPythonSrc() + "integrate.py " + downloadPath;
        	
        	//Run the command and wait for process to end.
        	Process pythonProcessInstance = Runtime.getRuntime().exec(command);
            pythonProcessInstance.waitFor();
            
            BufferedReader stdInput = new BufferedReader(new InputStreamReader(pythonProcessInstance.getInputStream()));
            BufferedReader stdError = new BufferedReader(new InputStreamReader(pythonProcessInstance.getErrorStream()));

 	   // read the output from the command
            /*System.out.println("Standard output from Python:\n");
            while ((s = stdInput.readLine()) != null) {
                System.out.println(s);
            }*/
               
            // read any errors from the attempted command
            /*System.out.println("Standard erro from Python:\n");
            while ((s = stdError.readLine()) != null) {
                   System.out.println(s);
            }*/

	   String command1 = "python3 " + pathManager.getPythonSrc() + "key.py " + downloadPath+" "+video.getVideoName();
           System.out.println(command1);
           Process p1 = Runtime.getRuntime().exec(command1);
           p1.waitFor();

           BufferedReader StdInput = new BufferedReader(new InputStreamReader(p1.getInputStream()));
           BufferedReader StdError = new BufferedReader(new InputStreamReader(p1.getErrorStream()));

 	   // read the output from the command
            /*System.out.println("Standard output from Python:\n");
            while ((s = StdInput.readLine()) != null) {
                System.out.println(s);
            }*/
               
            // read any errors from the attempted command
            /*System.out.println("Standard erro from Python:\n");
            while ((s = StdError.readLine()) != null) {
                   System.out.println(s);
            }*/

            //read the JSON file which contains tags created by python3 process. 
            tags += new String(Files.readAllBytes(Paths.get(jsonFilePath)));
        }
        
        
        catch (Exception e) {
            System.out.println("Exception occurred: ");
            e.printStackTrace();
            System.exit(-1);
        }
        
        return tags;
    }
	
}
