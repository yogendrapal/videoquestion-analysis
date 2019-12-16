
import uuid
import moviepy.editor as mp
import pydub
import speech_recognition as sr
import re
import operator
import nltk
import sys
import os
from sklearn.externals import joblib
import json

VideoName=sys.argv[1]
video = sys.argv[2]

clip = mp.VideoFileClip(VideoName)
name=VideoName[0:len(VideoName)-4]
name=name+".mp3"
clip.audio.write_audiofile(name)


sound = pydub.AudioSegment.from_mp3(name)
sound = sound.set_channels(1)
sound = sound.set_sample_width(2)
sound = sound.set_frame_rate(16000)
name=name[0:len(name)-4]
sound.export(name, format="wav")
r = sr.Recognizer()
harvard = sr.AudioFile(name)
s=str()
with harvard as source:
	r.adjust_for_ambient_noise(source)
	audio = r.record(source)
#s=r.recognize_bing(audio,key=BING_KEY)
text=r.recognize_google(audio)
print(text)


debug = False
test = True


def is_number(s):
    try:
        float(s) if '.' in s else int(s)
        return True
    except ValueError:
        return False


def load_stop_words(stop_word_file):
    """
    Utility function to load stop words from a file and return as a list of words
    @param stop_word_file Path and file name of a file containing stop words.
    @return list A list of stop words.
    """
    stop_words = []
    for line in open(stop_word_file):
        if line.strip()[0:1] != "#":
            for word in line.split():  # in case more than one per line
                stop_words.append(word)
    return stop_words


def separate_words(text, min_word_return_size):
    """
    Utility function to return a list of all words that are have a length greater than a specified number of characters.
    @param text The text that must be split in to words.
    @param min_word_return_size The minimum no of characters a word must have to be included.
    """
    splitter = re.compile('[^a-zA-Z0-9_\\+\\-/]')
    words = []
    for single_word in splitter.split(text):
        current_word = single_word.strip().lower()
        #leave numbers in phrase, but don't count as words, since they tend to invalidate scores of their phrases
        if len(current_word) > min_word_return_size and current_word != '' and not is_number(current_word):
            words.append(current_word)
    return words


def split_sentences(text):
    """
    Utility function to return a list of sentences.
    @param text The text that must be split in to sentences.
    """
    sentence_delimiters = re.compile(u'[.!?,;:\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s')
    sentences = sentence_delimiters.split(text)
    return sentences


def build_stop_word_regex(stop_word_file_path):
    stop_word_list = load_stop_words(stop_word_file_path)
    stop_word_regex_list = []
    for word in stop_word_list:
        word_regex = r'\b' + word + r'(?![\w-])'  # added look ahead for hyphen
        stop_word_regex_list.append(word_regex)
    stop_word_pattern = re.compile('|'.join(stop_word_regex_list), re.IGNORECASE)
    return stop_word_pattern


def generate_candidate_keywords(sentence_list, stopword_pattern):
    phrase_list = []
    for s in sentence_list:
        tmp = re.sub(stopword_pattern, '|', s.strip())
        phrases = tmp.split("|")
        for phrase in phrases:
            phrase = phrase.strip().lower()
            if phrase != "":
                phrase_list.append(phrase)
    return phrase_list


def calculate_word_scores(phraseList):
    word_frequency = {}
    word_degree = {}
    for phrase in phraseList:
        word_list = separate_words(phrase, 0)
        word_list_length = len(word_list)
        word_list_degree = word_list_length - 1
        #if word_list_degree > 3: word_list_degree = 3 #exp.
        for word in word_list:
            word_frequency.setdefault(word, 0)
            word_frequency[word] += 1
            word_degree.setdefault(word, 0)
            word_degree[word] += word_list_degree  #orig.
            #word_degree[word] += 1/(word_list_length*1.0) #exp.
    for item in word_frequency:
        word_degree[item] = word_degree[item] + word_frequency[item]

    # Calculate Word scores = deg(w)/frew(w)
    word_score = {}
    for item in word_frequency:
        word_score.setdefault(item, 0)
        word_score[item] = word_degree[item] / (word_frequency[item] * 1.0)  #orig.
    #word_score[item] = word_frequency[item]/(word_degree[item] * 1.0) #exp.
    return word_score


def generate_candidate_keyword_scores(phrase_list, word_score):
    keyword_candidates = {}
    for phrase in phrase_list:
        keyword_candidates.setdefault(phrase, 0)
        word_list = separate_words(phrase, 0)
        candidate_score = 0
        for word in word_list:
            candidate_score += word_score[word]
        keyword_candidates[phrase] = candidate_score
    return keyword_candidates


class Rake(object):
    def __init__(self, stop_words_path):
        self.stop_words_path = stop_words_path
        self.__stop_words_pattern = build_stop_word_regex(stop_words_path)

    def run(self, text):
        sentence_list = split_sentences(text)

        phrase_list = generate_candidate_keywords(sentence_list, self.__stop_words_pattern)

        word_scores = calculate_word_scores(phrase_list)

        keyword_candidates = generate_candidate_keyword_scores(phrase_list, word_scores)

        sorted_keywords = sorted(keyword_candidates.items(), key=operator.itemgetter(1), reverse=True)
        return sorted_keywords


if test:
    #text = "i wanted to know about how stock market works like a very new to this topic so i would like to note in layman terms like how exactly things happened in the stock market     "

    # Split text into sentences
    sentenceList = split_sentences(text)
    #stoppath = "FoxStoplist.txt" #Fox stoplist contains "numbers", so it will not find "natural numbers" like in Table 1.1
    stoppath = "python-src/SmartStoplist.txt"  #SMART stoplist misses some of the lower-scoring keywords in Figure 1.5, which means that the top 1/3 cuts off one of the 4.0 score words in Table 1.1
    stopwordpattern = build_stop_word_regex(stoppath)

    # generate candidate keywords
    phraseList = generate_candidate_keywords(sentenceList, stopwordpattern)

    # calculate individual word scores
    wordscores = calculate_word_scores(phraseList)

    # generate candidate keyword scores
    keywordcandidates = generate_candidate_keyword_scores(phraseList, wordscores)
    if debug: print(keywordcandidates)

    sortedKeywords = sorted(keywordcandidates.items(), key=operator.itemgetter(1), reverse=True)
    if debug: print(sortedKeywords)
    
    totalKeywords = len(sortedKeywords)
    if debug: print(totalKeywords)
    print(sortedKeywords[0:int(totalKeywords / 3)])

    rake = Rake("python-src/" + "SmartStoplist.txt")
    keywords = rake.run(text)
    print("Keywords: ",keywords)
    #print(type(keywords[0]))
    l=[]

    if(keywords[0][1]):
        score=keywords[0][1]
    else:
        score=1
    for i in keywords:
        if(i[1]==score):
            l.append(i[0])
        else:
            break
    
    print("l: ", l)

    tagg = []
    kwds = []
    #for i in range(len(l)):
        #l[i] = l[i].split(" ")
        #tagg.append(nltk.pos_tag(l[i]))

    #fkeys = " "
    #for x in tagg: 
        #for z in x:
                #fkeys=fkeys+" "+z[0]
    #print("keys : ", fkeys)
	
 
    with open('../classification/classes.txt') as file:
    	lines=file.read()    
    #print(lines)
    lines=lines.split('\n')
    lines=lines[0:10]
    #print(lines)
    #print(text)
    
    from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
    
    

    from sklearn.externals import joblib
    pipe = joblib.load('../classification/newSavedModel.pkl')
    predictions=pipe.predict([l[0]])

    for i in predictions:
    	r=lines[i-1]
    	#print(clf)

   
    #tagged = nltk.pos_tag(l)
    #print(tagged)
    #name=name+".txt"
    #dir=os.path.normpath(os.getcwd()+os.sep+os.pardir)
    jsonPath="json-files/"+ video + ".json"
    #f=open (name,"w+")
    with open(jsonPath) as f:
        data=json.load(f)
    data['Topic']=[r]
    with open(jsonPath,'w') as json_files:
    	json.dump(data,json_files) 
    	