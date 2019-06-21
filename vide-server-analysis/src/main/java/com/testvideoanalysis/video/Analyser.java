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
	
	public String getTags(Video video) {
		
		String downloadPath = pathManager.getDownloadedVideos() + video.getVideoNameWithExtension();
		String jsonFilePath = pathManager.getJsonFiles() + video.getVideoName() + ".json";
        String tags = "";
		try {
            
        String command = "python3 " + pathManager.getPythonSrc() + "integrate.py " + downloadPath;
        Process p = Runtime.getRuntime().exec(command);
           p.waitFor();
         String command1 = "python3 " + pathManager.getPythonSrc() + "key.py " + downloadPath+" "+video.getVideoName();
            System.out.println(command1);
          Process p1 = Runtime.getRuntime().exec(command1);
            p1.waitFor();
            BufferedReader in = new BufferedReader(new InputStreamReader(p1.getInputStream()));
            BufferedReader out = new BufferedReader(new InputStreamReader(p1.getErrorStream()));
            String line ;
            while((line=in.readLine()) != null){
            	System.out.println(line);
            }
            while((line=out.readLine()) != null){
            	System.out.println(line);
            }

           
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
