import json
import os
import sys

def get_nonzero_values_key(count):

    sum_of_nonzero_entries = sum(x > 0 for x in count.values())
    return sum_of_nonzero_entries


def get_video_path(video_path_in_json_file):

    with open(video_path_in_json_file, 'r') as infile:
        video_path = json.loads(infile.read())
        return video_path

def get_json_tag_write_file (video_path, json_directory_path):

    video_name = video_path.split('/')[-1].split('.')[0]
    json_tag_write_path = json_directory_path + video_name + ".json"

    return json_tag_write_path

def get_predictions (count, topn = 1):

    '''
    Input: A dictionary which contains labels as keys and count of labels as values.
           Top n predictions returned as a list. 

    Output: N labels with the max count.
    
    '''

    topn = min(topn, get_nonzero_values_key(count))
    predicted_labels_dict = dict(sorted(count.items(), key=lambda x: x[1], reverse = True)[:topn])
    predicted_labels_list = list(predicted_labels_dict.keys())
    return predicted_labels_list

def store_in_json_file(tags, json_tag_write_path):

    with open(json_tag_write_path, 'w') as outfile:
        json.dump(tags, outfile)
