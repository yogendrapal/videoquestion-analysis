# Name  
Video Analysis API.        

## Description
Video Analysis API is an API built using Springboot and Python. The springboot accepts a video of a person and returns with a JSON response of tags such as gender and emotions. The tags are the output of a python script which uses a Convolutional neural network.     
[**NOTE**: The project is still under development and further tags like age, etc need to be added.]

## Directory Structure
Test-Video-Analysis-API is the root of the project.  
- **src**: contains the springboot server.  
- **python-src** 
   - integrate.py is the main script that outputs the JSON tags using CNNs.

- **json-files**: contains .json files for each tag.  
- **downloaded-videos**: contains downloaded videos sent by client.  
- **pom.xml**: contains the Maven dependencies for springboot. Update this file to add Maven dependencies.

## Usage
Clone the repository using git clone.  
Open video-analysis-server/Test-Video-Analysis-API/ as an Eclipse/ STS project.    
Run the server. [The Server should be up and running!].  
Use Postman for sending HTTP POST request.  
Run MongoDB in the background.  

```   
sudo service mongod start  
mongo  
```  
   
Set the URI to:    
```    
http://localhost:4001/drupal/upload    
```  

[**NOTE**: The port no. can be changed in video-analysis-server/src/main/resources/application-properties.]  
  
Server consumes **form-data** in the body. 
The body should contain 2 fields:
- key: **video** ; value = **video to be uploaded**.
- key: **id** ; value = **any integer id**.
