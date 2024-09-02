import requests
from bs4 import BeautifulSoup
import pandas as pd


# 페이지 내부 타이틀, 닉네임, 날짜, 콘텐츠, 주소 정보 스크롤
def get_blog_item(url) :
    tmp = url.split("/")
    url = f'https://blog.naver.com/PostView.naver?blogId={tmp[-2]}&logNo={tmp[-1]}'
    res = requests.get(url)
    nick = tmp[-2]
    soup = BeautifulSoup(res.text, "html.parser")
    
    if soup.select_one(".se-title-text") :
        title = soup.select_one(".se-title-text").text
        date = soup.select_one(".se_publishDate").text
        content = soup.select_one(".se-main-container").text
    else : # 테마가 다른 블로그
        title = soup.select_one(".se_title h3").text
        date = soup.select_one(".se_publishDate").text
        content = soup.select(".se_component_wrap")[1].text
        
    # if랑 else에 있는 tavle, content 공통된 replace를 묶어서 처리
    title = title.replace("\n", "").replace("\u200b", "").replace("\xa0", "").replace("\t", "").replace("\r","")
    content = content.replace("\n", "").replace("\u200b", "").replace("\xa0", "").replace("\t", "").replace("\r","")
        
    return (title, nick, date, content, url)


# 네이버 페이지에서 블로그 옵션에 접근 
def get_naver_blog(keyword, startdate, enddate) :
    url = f'https://s.search.naver.com/p/review/48/search.naver?ssc=tab.blog.all&api_type=8&query={keyword}&start=1&nx_search_query=&nx_and_query=&nx_sub_query=&ac=1&aq=0&spq=0&sm=tab_opt&nso=so%3Add%2Cp%3Afrom{startdate}to{enddate}&prank=30&ngn_country=KR&lgl_rcode=09170128&fgn_region=&fgn_city=&lgl_lat=37.5278&lgl_long=126.9602&enlu_query=IggCADqCULhpAAAAj0RP67RmqTWRq3DkdYxhcV7F5RKpJAPG1d9ZSyMVgoc%3D&abt=&retry_count=0'

    ret = []

    range = pd.date_range(startdate, enddate, freq='D')
    step = 100 / len(range) 
    percent_complete = 0
    my_bar = st.progress(0, '블로그 수집 시작')

    for d in range :
        # page = 1
        print(d)

        while True :
            res = requests.get(url)
            res_dic = eval(res.text)
            soup = BeautifulSoup(res_dic['contents'], 'html.parser')
            if res_dic['nextUrl'] == "" :
                break
            url = res_dic['nextUrl']

            for item in soup.select('.title_area > a') :
                try :
                    ret.append(get_blog_item(item['href']))
                except : # 테마가 다른 블로그
                    print(item['href'])

            # page += 1

        percent_complete = percent_complete + step
        my_bar.progress(int(percent_complete), f'{d.strftime("%Y-%m-%d")} {int(percent_complete)} % : {len(ret)}건 수집됨')
        print(percent_complete)

    df = pd.DataFrame(ret, columns=['title', 'nick', 'date', 'content', 'url'])
    return df


import streamlit as st

st.title('블로그')

with st.sidebar:
    code = st.text_input('키워드를 입력해주세요')
    sd = st.date_input("조회 시작일을 선택해 주세요")
    ed = st.date_input("조회 종료일을 선택해 주세요")
    # cb_csv - st.checkbox('csv를 저장할까요?')
    btn = st.button('수집하기')

if sd and ed and code and btn :
    df = get_naver_blog(code, sd.strftime('%Y%m%d'), ed.strftime('%Y%m%d'))
    st.dataframe(df)




