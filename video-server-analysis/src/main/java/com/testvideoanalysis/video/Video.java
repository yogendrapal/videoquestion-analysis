package com.testvideoanalysis.video;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.annotation.Id;

import com.testvideoanalysis.path.PathManager;

public class Video {
	
	@Id
	private String videoId;
	private String videoName;
	private String videoType;
	private String tags;
	private String status;

	@Autowired
	PathManager pathManager;
	
	public Video() {
	
	}
	
	public Video(String videoName, String videoId) {
		super();
		this.videoId				= videoId;
		String [] splitVideoName	= videoName.split("\\.");
		this.videoType 				= splitVideoName[splitVideoName.length-1];
		this.videoName	 			= splitVideoName[0];
		this.status 				= "Queued";
		this.tags					= "";
	}

	public String getVideoName() {
		return videoName;
	}
	
	public String getVideoNameWithExtension() {
		return videoName + "." + videoType;
	}
	
	public void setVideoName(String videoName) {
		this.videoName = videoName;
	}
	
	public String getVideoType() {
		return videoType;
	}
	
	public void setVideoType(String videoType) {
		this.videoType = videoType;
	}
	
	public String getVideoId() {
		return videoId;
	}
	
	public String getTags() {
		return tags;
	}

	public void setTags(String tags) {
		this.tags = tags;
	}

	public String getStatus() {
		return status;
	}

	public void setStatus(String status) {
		this.status = status;
	}
	
}
