import datetime
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from bs4 import BeautifulSoup
import requests as requests


def sendMail(article: str,new_num: int , to_ad: str):
    from_addr = formataddr(('SOCH', 'bh.lee@email.com'))

    # 받는사람
    to_addr = formataddr(('보안담당자', to_ad))

    session = None
    try:
        # SMTP 세션 생성
        session = smtplib.SMTP('smtp.gmail.com', 587)
        #session.set_debuglevel(True)

        # SMTP 계정 인증 설정
        session.ehlo()
        session.starttls()
        session.login('GOOGLE_ID', 'APP_PW')

        # 메일 콘텐츠 설정
        message = MIMEMultipart("mixed")

        # 메일 송/수신 옵션 설정
        message.set_charset('utf-8')
        message['From'] = from_addr
        message['To'] = to_addr
        message['Subject'] = "[보안관제] KISA 보호나라 보안공지 신규 게시물 알림 ("+str(new_num)+"건)"
        # 메일 콘텐츠 - 내용
        body = "보안공지 새로운 게시물을 알려드립니다.(❁´◡`❁)<br><br><br>" + article + "<br><br><br>문의 : Aiden Lee(이병호)<br>메일링 등록/해제 : https://www.kokonut.today/mail "
        bodyPart = MIMEText(body, 'html', 'utf-8')
        message.attach(bodyPart)

        # 메일 발송
        session.sendmail(from_addr, to_addr, message.as_string())

    except Exception as e:
        print(e)
    finally:
        if session is not None:
            session.quit()


def get_text_list(file_name: str):
    if os.path.isfile(file_name) is False:
        nf = open(file_name, 'w', encoding='utf-8')
        nf.close()

    f = open(file_name, 'r', encoding='utf-8')
    search = '\n'
    return_list = [word.strip(search) for word in f.readlines()]
    return return_list if len(return_list) > 0 else None


def file_set_article(file_name: str, articles: list):
    f = open(file_name, 'w', encoding='utf-8')
    for i in articles:
        f.writelines(i + '\n')
    f.close()


def get_data(url: str):
    response = requests.get(url)
    articles_list = []
    line = ''
    if response.status_code == 200:
        html = response.text.strip()
        soup = BeautifulSoup(html, 'html.parser')

        articles = soup.select('table > tbody > tr > td')
        for article in enumerate(articles, start=1):

            if int(article[0]) % 5 != 3:
                line += article[1].text.strip() + ' '

            if int(article[0]) % 5 == 2:
                line += 'URL : https://www.boho.or.kr' + article[1].find("a")["href"] + ' '

            if int(article[0]) % 5 == 0:
                articles_list.append(line)
                line = ''
                continue

        return articles_list


def what_is_new_article(article_list: list, new_article_list: list):
    if article_list is None:
        return []
    return sorted(list(set(new_article_list) - set(article_list)))


def article_to_html(newest_article: list):
    text = ''
    for i in newest_article:
        text += i + '<br>'
    return text

while True:
    print('Scanning : ' + str(datetime.datetime.now()))

    # 신규 게시물 확인
    article_list = get_text_list(file_name='./article_lists.txt')
    new_article_list = get_data(url='https://www.boho.or.kr/data/secNoticeList.do')
    newest_article = what_is_new_article(article_list=article_list, new_article_list=new_article_list)

    # 신규 게시글 파일 작성
    file_set_article(file_name='./article_lists.txt', articles=new_article_list)

    # 이메일 목록을 획득 및 메일 발송
    if len(newest_article) > 0:
        article_text = article_to_html(newest_article=newest_article)
        mail_list = get_text_list(file_name='./mail_list.txt')

        if mail_list is None:
            print('please insert email list')
        else:
            for to in mail_list:
                sendMail(article=article_text, new_num=len(newest_article), to_ad=to)

            now = datetime.datetime.now()
            print('발송 : '+ str(now) + ' : ' + ','.join(mail_list))
            for i in enumerate(newest_article, start=1):
                print(i)
        print('------------ Sleep 15 min -----------')
        time.sleep(900)
