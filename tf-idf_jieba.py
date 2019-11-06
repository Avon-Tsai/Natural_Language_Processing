# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 10:35:39 2018

@author
"""

import matplotlib.pyplot as plt
import numpy as np
import jieba.analyse
import codecs
from wordcloud import WordCloud

import pymysql 
import pandas as pd 
from pandas.io import sql
from sqlalchemy import create_engine 

import re
from collections import Counter
from pprint import pprint

pymysql.install_as_MySQLdb()

conn = pymysql.connect(host, port, user, passwd, db, charset='utf8')  
sql = "SELECT * FROM gsearch.urcosme_reviews where prodid = 4821;"

df = pd.read_sql(sql, conn)

result_all = ''
for  i  in  range(len(df)):
    # 去除停用字
    stop = re.compile(r'http://[a-zA-Z0-9.?/&=:]*',re.S)
    content = stop.sub("", df['content'][i])
    stoplist = '[★XD。，：’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~0-9]+'
    content = re.sub(stoplist, '', content)
    jieba.analyse.set_stop_words("stopword.txt")
    jieba.suggest_freq('雅詩蘭黛', True)
   
    words = jieba.analyse.extract_tags(content,50,allowPOS=['n','ns','nr','nt','a'])
    result = ", ".join(words)
    result_all += result
    print("="*70)
    print(result+"\n")

count = Counter(result_all.split(", ")).most_common(200)
print("*"*70)
pprint(count)
        
'''
# 詞性標註
import jieba.posseg as pseg
words = pseg.cut("黏膩")
for w in words:
    print(w.word, w.flag )
'''

sql = "SELECT content FROM gsearch.urcosme_reviews r, gsearch.urcosme_prods_new p where p.category = '精華液' and (p.brandid = 38 or p.brandid = 65 or p.brandid = 14 or p.brandid = 24 or p.brandid = 30 or p.brandid = 55)  and p.prodid = r.prodid and p.prodid!=4821 ;"
df_other = pd.read_sql(sql, conn)

other_all = []
for  i  in  range(len(df_other)):
    # 去除停用字
    stop = re.compile(r'http://[a-zA-Z0-9.?/&=:]*',re.S)
    content = stop.sub("", df_other['content'][i])
    stoplist = '[★XD。，：’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~0-9]+'
    content = re.sub(stoplist, '', content)
    jieba.analyse.set_stop_words("C:\\Users\\A40455\\Downloads\\stopword.txt")
    jieba.suggest_freq('雅詩蘭黛', True)
  
    words = jieba.analyse.extract_tags(content,len(content),allowPOS=['n','ns','nr','nt','a'])
    other_all.extend(words)
    
'''
count target term 
'''
result_count = []
for  i  in  range(len(count)):
    word_count = Counter(other_all)[count[i][0]]
    data = (count[i][0], word_count)
    result_count.append(data)

result_sort = sorted(result_count,key=lambda x: x[1])
result_sort[:10]

lst = []
for i in range(len(result_sort)):
    term_data = 'SK-II+青春露+'+result_sort[i][0]
    lst.append(term_data)

