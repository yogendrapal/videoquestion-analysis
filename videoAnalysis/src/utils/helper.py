import json


def get_video_path(video_path_in_json_file):

    with open(video_path_in_json_file, 'r') as infile:
        video_path = json.loads(infile.read())
        return video_path

def get_json_tag_write_file (video_path, json_directory_path):

    video_name = video_path["path"].split('/')[-1].split('.')[0]
    json_tag_write_path = json_directory_path + video_name + ".json"

    return json_tag_write_path

def get_predicted_gender (gender_count):

    man_count        = gender_count["man"]
    woman_count      = gender_count["woman"]
    predicted_gender = max(gender_count, key=gender_count.get)
    
    return predicted_gender

def store_in_json_file(predicted_gender, json_tag_write_path):

    tags = {"Gender": predicted_gender}

    with open(json_tag_write_path, 'w') as outfile:
        json.dump(tags, outfile)
