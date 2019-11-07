"""
Created on Tue Jul 17 16:17:45 2018

@author: A40455
"""

# -*- coding: utf-8 -*-  
import pymysql 
import pandas as pd 
from pandas.io import sql
from sqlalchemy import create_engine 

from konlpy.tag import Twitter
twitter = Twitter()

from collections import Counter
import  os  
import  sys  
from  sklearn  import  feature_extraction  
from  sklearn.feature_extraction.text  import  TfidfTransformer  
from  sklearn.feature_extraction.text  import  CountVectorizer

import urllib.request, urllib.parse
import json
from googletrans import Translator

pymysql.install_as_MySQLdb()

conn = pymysql.connect(host, port, user, passwd, db, charset='utf8')  

''' all '''
#sql = "SELECT * FROM naver.blog where title like '%대만%' and pdate BETWEEN '2018-01-01' AND '2018-01-08' ;" #대만:台灣 / 여행:旅行

''' 餐館 '''
#sql = "SELECT * FROM naver.blog where title like '%대만%' and (content like '%레스토랑%' or content like '%맛집%' or content like '%먹거리%' or content like '%메뉴%') and pdate = '2018-01-05';"
#sql = "SELECT * FROM naver.blog where title like '%대만%' and (content like '%레스토랑%' or content like '%맛집%' or content like '%먹거리%' or content like '%메뉴%') and pdate BETWEEN '2018-01-01' AND '2018-01-08';"

''' 伴手禮 '''
#sql = "SELECT * FROM naver.blog where title  like '%대만%' and (content like '%기념품%' or content like '%쇼핑%' or content like '%선물%' ) and pdate = '2018-01-05';"
sql = "SELECT * FROM naver.blog where title  like '%대만%' and (content like '%기념품%' or content like '%쇼핑%' or content like '%선물%' ) and pdate BETWEEN '2018-01-01' AND '2018-01-31';"

df = pd.read_sql(sql, conn)
df['content'] = df['content'].str.replace('마지막|윤오엔나|이윽고|위안부|언젠간|드디어|그대만','')

move = dict.fromkeys((ord(c) for c in u"\\xa0\\n\t\n"))
df['content'] = df['content'].str.translate(move)

# twitter.pos(df['title'][1], norm=True, stem=True)
#Counter(twitter.nouns(df['content'][3])).most_common(10)
#sum(Counter(twitter.nouns(df['content'][3])).values())

corpus = []
for  i  in  range(len(df)):
    print(i)
    nouns = twitter.nouns(df['content'][i])
    nouns = [item for item in nouns if len(item) > 2]
    content = ' '.join(nouns)
    corpus.append(content)
    
vectorizer = CountVectorizer() #該類會將文本中的詞語轉換為詞頻矩陣，矩陣元素a[i][j]表示j詞在i類文本下的詞頻  
transformer = TfidfTransformer() #該類會統計每個詞語的tf-idf權值  
tfidf = transformer.fit_transform(vectorizer.fit_transform(corpus))

word = vectorizer.get_feature_names() #獲取詞袋模型中的所有詞語  
weight = tfidf.toarray() #將tf-idf矩陣抽取出來，元素a[i][j]表示j詞在i類文本中的tf-idf權重  

word_result = []
weight_result = []

for  i  in  range(len(weight)): #打印每類文本的tf-idf詞語權重，第一個for遍歷所有文本，第二個for便利某一類文本下的詞語權重  
    print("-------這裡輸出第" + str(i) +"類文本的詞語tf-idf權重------" ) 
    for  j  in  range(len(word)):  
        word_result.append(word[j])
        weight_result.append(weight[i][j])
        #print(word[j],weight[i][j] )

result_dict = {
    "word": word_result,
    "weight": weight_result
}

# 建立 data frame
result = pd.DataFrame(result_dict)
#result = result.loc[result['weight'] >= 0.7]

result_sort = result.sort_values(by=['word','weight'], ascending=False)
result_sort = result_sort.drop_duplicates(subset='word', keep="first")
result_sort = result_sort.loc[result['weight'] >= 0.7]
result_sort = result_sort.sort_values(by=['weight'], ascending=False)
result_list = result_sort['word'].values.tolist()

#############################################################
# 計算詞頻
print("--------------- 計算詞頻 ---------------")
word_frequence = twitter.nouns(df['content'][0])
for  i  in  range(1,len(df)): 
    word_frequence += twitter.nouns(df['content'][i])
    
word_frequence = [item for item in word_frequence if len(item) > 2]
word_frequence_max = Counter(word_frequence).most_common(50)
word_list = pd.DataFrame(word_frequence_max)[0].values.tolist()

#############################################################
# 翻譯
def translation(term_list) :
    translator = Translator(service_urls=[
      'translate.google.com',
      'translate.google.co.kr',
    ])
    translations = translator.translate(term_list, dest='zh-tw')
    for translation in translations:        
        word = str(translation.origin.encode('utf-8'))[1:].replace("'","").replace("\\x","%")
        base_url = "https://zh.dict.naver.com/cndictApi/search/word?sLn=ko&q="+word+"&mode=pc&pageNo=1&format=json"   
        webURL  = urllib.request.urlopen(base_url)
        data = json.loads(webURL.readall().decode('utf-8'))
        
        if len(data) > 2 :
            keyword = data['searchResults']['searchEntryList']['items'][0]['fantizi']
            if(len(keyword) == 0) :
                keyword = data['searchResults']['searchEntryList']['items'][0]['entryName'] #샤오롱바오 小笼包
                if(len(keyword) == 0 or keyword.find('<strong>') != -1) :
                    keyword = data['searchResults']['searchEntryList']['items'][0]['meanList'][0]['mean'] #지우펀 九份
                    if(keyword.find('autoLink') != -1 ) :
                        #keyword = keyword.split('>')[1].split('<')[0] # 타이난 台南
                        keyword_list = keyword.split('<autoLink search=')
                        keyword = ''
                        for j in keyword_list:
                            keyword += j.split('>')[0]
                        keyword = keyword.replace('"','')
        else :
            keyword = 'NULL' # 백화유 白花油
            
        keyword = keyword.replace('←','').replace('。','').replace('-','')
        print(translation.origin + ' Translation -> '+keyword + ' || ' + translation.text)

#############################################################
print("--------------- TF-IDF WEIGHT > 0.7 ---------------")    
translation(result_list)
print("--------------- TF TOP 50 ---------------")
translation(word_list)





