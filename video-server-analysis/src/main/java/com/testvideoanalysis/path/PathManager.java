package com.testvideoanalysis.path;
import org.springframework.stereotype.Service;

@Service
public class PathManager {

	private String root 			= "";
	private String src 				= "";
	private String jsonFiles 		= "";
	private String pythonSrc 		= "";
	private String downloadedVideos = "";
	private String keyword 			= "";
	
	PathManager(){
		root 				+= System.getProperty("user.dir") + "/";
		src 				+= "src/";
		jsonFiles 			+= "json-files/";
		pythonSrc			+= "python-src/";
		downloadedVideos 	+= "downloaded-videos/";
		
	}
	
	public String getRoot() {
		return root;
	}
	
	public String getSrc() {
		return root + src;
	}
	
	public String getJsonFiles () {
		return root + jsonFiles;
	}
	
	public String getPythonSrc() {
		return root + pythonSrc;
	}
	
	public String getDownloadedVideos() {
		return root + downloadedVideos;
	}

	public String getKeyword() {
		return root+keyword;
	}
}
