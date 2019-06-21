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
			
			  videoRepository.save(video);
		      InputStream is = file.getInputStream();
		      
		      Files.copy(is, Paths.get(pathManager.getDownloadedVideos() + video.getVideoNameWithExtension()), StandardCopyOption.REPLACE_EXISTING);
		      updateStatus(video, "Processing");
		      
		      String tags = analyser.getTags(video);
		      
		      updateStatus(video, "Finished");
		      updateTags(video, tags);
		      
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
		
		return "Video ID is Invalid.";
	}
	
	public void updateStatus(Video video, String status) {
		video.setStatus(status);
		videoRepository.save(video);
	}
	
	public void updateTags(Video video, String tags) {
		video.setTags(tags);
		videoRepository.save(video);
	}
	
	public Optional<Video> getVideo(String id) {
		return videoRepository.findById(id);
	}
}
