import pandas as pd
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import os
import string
import csv
from nltk.corpus import stopwords # I am using this just because for variable 'word count' in Text Analysis it is given to use nltk tool.
stopwords = set(stopwords.words('english'))

# making directory for extraction
os.mkdir('extracted_data')

# function to obtain syllables from word
def syllable_count(word):
    word = word.lower()
    if word[-2:] in ["es","ed"]:
        if len(word) ==2:
            return 1
        word = word[:-2]
    count = 0
    for c in word:
        if c in "aiouey":
            count+= 1
    return count

# importing links form INPUT
links = pd.read_excel("Input.xlsx")

#Creating output file:
label = ["URL_ID","URL","POSITIVE SCORE","NEGATIVE SCORE","POLARITY SCORE","SUBJECTIVITY SCORE","AVG SENTENCE LENGTH","PERCENTAGE OF COMPLEX WORDS","FOG INDEX","AVG NUMBER OF WORDS PER SENTENCE","COMPLEX WORD COUNT","WORD COUNT","SYLLABLE PER WORD","PERSONAL PRONOUNS","AVG WORD LENGTH"]
with open("output.csv",'w') as output:
    writer = csv.writer(output)
    writer.writerow(label)

    # Iterating over every link
    for i, link in links.iterrows():
        url_id =link['URL_ID']
        url = link['URL']
        # obtaining page with request
        try:
            page = requests.get(url)
            page.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            continue

        soup = BeautifulSoup(page.text,'html.parser')
        
        # obtaining title
        title = soup.find('h1',class_='entry-title').text

        # obtaining main text
        main_content = soup.find('div', class_='td-post-content')
        text = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'li'])

        all_text = ""
        for p in text[5:]:
            all_text += p.get_text(strip=text) + " "
        
        # data extraction in indivisual file 
        with open(f"extracted_data/{url_id}.txt",'w') as file:
            file.write(f'Title:{title}\n')
            file.write(all_text)
        
        # tokenize the text
        sentences = sent_tokenize(all_text)
        words = word_tokenize(all_text)

        # obtaning your given stop words for sentiment analysis
        new_stopwords = set()
        for filename in os.listdir("StopWords"):
            with open(f"StopWords/{filename}",'r',encoding='latin-1') as file:
                for word in file.readlines():
                    new_stopwords.add(word.split('|')[0].strip())
        
        # obtaing positive and negative words given by you
        positive_words = set()
        negative_words = set()

        with open("MasterDictionary/positive-words.txt",'r') as pw:
            for word in pw.readlines():
                positive_words.add(word.strip())
        with open("MasterDictionary/negative-words.txt",'r',encoding='latin-1') as nw:
            for word in nw.readlines():
                negative_words.add(word.strip())
        
        # varialbe intialization area
        positive_score = 0
        negative_score = 0
        complex_words = 0
        total_syllable_count =0
        personal_pronouns = 0
        char_count = 0

        # cleaning words and making count of varialbes
        f_words = []
        for word in words:
            word_lower = word.lower()
            if word_lower not in new_stopwords and word not in string.punctuation:
                f_words.append(word)
                char_count += len(word)
                if word_lower in ["i","us","we","my","our"]:
                    personal_pronouns += 1
                v = syllable_count(word)
                total_syllable_count +=v
                if v >2:
                    complex_words += 1
                if word_lower in positive_words:
                    positive_score += 1
                elif word_lower in negative_words:
                    negative_score += 1

        # polarity Score
        polarity_score = (positive_score - negative_score)/ ((positive_score + negative_score) + 0.000001)

        # subjective Score
        subjective_score = (positive_score + negative_score)/ (len(f_words) + 0.000001)

        # average sentence length
        average_sentence_length = len(f_words)/len(sentences)

        # obtainig word_count as stated in Text analysis file otherwise we have all ready filtered the text by your given stopwords
        word_count =0
        for word in words:
            if word.lower() not in stopwords and word not in string.punctuation:
                word_count += 1
        
        # syllable per word 
        syllable_per_word = total_syllable_count/len(f_words)

        # average  word length
        average_word_length = char_count / len(f_words)

        # percentage of complex words
        percentage_of_complex_word = (complex_words/len(f_words))*100

        # fog index
        fog_index = 0.4*(average_sentence_length+percentage_of_complex_word)

        # output to file
        result = [url_id,url,positive_score,negative_score,polarity_score,subjective_score,average_sentence_length,percentage_of_complex_word,fog_index,average_sentence_length,complex_words,word_count,syllable_per_word,personal_pronouns,average_word_length]

        writer.writerow(result)
