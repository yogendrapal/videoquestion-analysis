package com.testvideoanalysis.repository;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import com.testvideoanalysis.video.Video;

@Repository
public interface VideoRepository extends MongoRepository <Video, String> {

}
