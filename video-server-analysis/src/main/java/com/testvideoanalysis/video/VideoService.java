package com.testvideoanalysis.video;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import com.testvideoanalysis.path.PathManager;
import com.testvideoanalysis.repository.VideoRepository;

@Service
public class VideoService {
	
	@Autowired
	Analyser analyser;
	
	@Autowired
	PathManager pathManager;
	
	@Autowired
	VideoRepository videoRepository;
	
	public String uploadVideo(Video video, MultipartFile file) {
		
		try {
			  
			  // save video object in database 
			  videoRepository.save(video);
		      InputStream is = file.getInputStream();
		      
		      // download the video and store in downloaded-videos
		      Files.copy(is, Paths.get(pathManager.getDownloadedVideos() + video.getVideoNameWithExtension()), StandardCopyOption.REPLACE_EXISTING);
		      
		      //update status of stored video object in database
		      updateStatus(video, "Processing");
		      
		      // start analyzing video
		      String tags = analyser.getTags(video);
		      
		      updateStatus(video, "Finished");
		      updateTags(video, tags);
		      
		      // delete stored video and JSON file to free memory
		      Files.deleteIfExists(Paths.get(pathManager.getDownloadedVideos() + video.getVideoNameWithExtension() ) ); 
		      Files.deleteIfExists(Paths.get(pathManager.getJsonFiles() + video.getVideoName() + ".json"));

		      // delete .mp3 and .wav files 
		      Files.deleteIfExists(Paths.get(pathManager.getDownloadedVideos() + video.getVideoName + ".mp3" ) ); 
		      Files.deleteIfExists(Paths.get(pathManager.getJsonFiles() + video.getVideoName() + ".wav"));

		      return tags;
		}
		
		catch (IOException ex) {
		      return "Error writing file to output stream.";
		}
	}
	
	
	public String getVideoStatus(String id) {
		Optional<Video> video = videoRepository.findById(id);
		
		if (video.isPresent())
			return video.get().getStatus();
		
		// throw error if queried video id is not stored in Database.
		return "Video ID is invalid and doesnt exist in the Database.";
	}
	
	
	public void updateStatus(Video video, String status) {
		
		// update status of stored video object in Database.
		video.setStatus(status);
		videoRepository.save(video);
		
	}
	
	
	public void updateTags(Video video, String tags) {
		
		// update tags of stored video object in Database.
		video.setTags(tags);
		videoRepository.save(video);
		
	}
	
	
	public Optional<Video> getVideo(String id) {
		
		//return video object from id.
		return videoRepository.findById(id);
	}
	
}
