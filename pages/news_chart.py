import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_news_item(url) :
  res = requests.get(url)

  soup = BeautifulSoup(res.text, "html.parser")
  title = soup.select_one("h2#title_area").text
  media = soup.select_one(".media_end_head_top_logo img")["title"]
  date = soup.select_one(".media_end_head_info_datestamp_time")["data-date-time"]
  content = soup.select_one("#newsct_article").text.replace("\n", "").replace("\t", "").replace("\r", "")
  return (title, media, date, content, url)


import requests
from bs4 import BeautifulSoup
import pandas as pd
# def get_news(keyword, startdate, enddate):
keyword = '티니핑'
startdate = '2024.08.20'
enddate = '2024.08.26'
#start = 1 # 1, 11, 21, 31, 41, 51, 61 ...
def get_naver_new(keyword, startdate, enddate, to_csv=False):
    ret = []
    for d in pd.date_range(startdate,enddate, freq='D'):
        page = 1
        print(d)
        while True:
            start = (page - 1) * 10 + 1
            url = f"https://s.search.naver.com/p/newssearch/search.naver?de={d.strftime('%Y.%m.%d')}&ds={d.strftime('%Y.%m.%d')}&eid=&field=0&force_original=&is_dts=0&is_sug_officeid=0&mynews=0&news_office_checked=&nlu_query=&nqx_theme=&nso=%26nso%3Dso%3Add%2Cp%3Afrom{d.strftime('%Y%m%d')}to{d.strftime('%Y%m%d')}%2Ca%3Aall&nx_and_query=&nx_search_hlquery=&nx_search_query=&nx_sub_query=&office_category=0&office_section_code=0&office_type=0&pd=3&photo=0&query={keyword}&query_original=&service_area=0&sort=1&spq=0&start={start}&where=news_tab_api&nso=so:dd,p:from{d.strftime('%Y%m%d')}to{d.strftime('%Y%m%d')},a:all"
            h = {'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'}
            res = requests.get(url, headers = h)
            li = eval(res.text)['contents']
            if len(li) == 0:
                break
            for item in li :
                soup = BeautifulSoup(item, 'html.parser')
                a_tags = soup.select("div.info_group a")
                if len(a_tags) == 2 :
                    try:
                        ret.append(get_news_item(a_tags[1]['href']))
                    except :
                        print(a_tags[1]['href'])
            page += 1
    df = pd.DataFrame(ret, columns=['title', 'media', 'data', 'content', 'url'])
    return df



import streamlit as st

st.title('뉴스')

with st.sidebar :

    code = st.text_input('키워드를 입력해주세요')
    sd = st.date_input("조회 시작일을 선택해 주세요")
    ed = st.date_input("조회 종료일을 선택해 주세요")
    btn = st.button('수집하기')

if sd and ed and code and btn :
    df = get_naver_new(code, sd.strftime('%Y%m%d'), ed.strftime('%Y%m%d'))
    st.dataframe(df)


