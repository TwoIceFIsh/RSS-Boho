import os
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from datetime import datetime
from threading import Thread
import configparser
from bs4 import BeautifulSoup

import requests as requests

class Log:

    # 오늘 일자로 파일 이름을 생성 한다.
    def __init__(self):
        self.file_name = f'.\\log{datetime.today().strftime("%Y-%m-%d")}.txt'

    # 현재시간을 기준으로 로그를 파일에 작성 및 
    def add_log(self, comment: str):
        if os.path.isfile(self.file_name) is True:
            with open(self.file_name, 'a', encoding='utf-8') as f:
                log_str = f'{datetime.today().strftime("%Y/%m/%d %H:%M:%S : ")}{comment}'
                f.write(log_str+'\n')
                print(log_str)
            return True
        return False

    # 새로운 파일 생성
    def new_log_file(self):
        if os.path.isfile(self.file_name) is False:
            with open(self.file_name, 'w', encoding='utf-8') as f:
                pass
            return True
        return False


class Properties:

    def __init__(self):
        self.file_name = f'.\\config.ini'

    def new_config_file(self):
        if os.path.isfile(self.file_name) is False:
            with open(self.file_name,'w', encoding='utf-8') as f:
                f.write(self.file_name)

            return True
        return False

    def set(self):
        properties = configparser.ConfigParser()  ## 클래스 객체 생성

        properties.set("DEFAULT", "google_gmail_id", "myid@gmail.com")
        properties.set("DEFAULT", "google_app_pw", "xxxxyyyyzzzzqqqq")

        with open(self.file_name, "w") as f:
            properties.write(f)



def send_mail(id:str,pw:str,article: str, new_num: int, to_ad: str):
    from_addr = formataddr(('RSS-Boho', id))

    # 받는사람
    to_addr = formataddr(('담당자', to_ad))

    session = None
    try:
        # SMTP 세션 생성
        session = smtplib.SMTP('smtp.gmail.com', 587)
        # session.set_debuglevel(True)

        # SMTP 계정 인증 설정
        session.ehlo()
        session.starttls()
        session.login(id, pw)

        # 메일 콘텐츠 설정
        message = MIMEMultipart("mixed")

        # 메일 송/수신 옵션 설정
        message.set_charset('utf-8')
        message['From'] = from_addr
        message['To'] = to_addr
        message['Subject'] = "[보안관제] KISA 보호나라 보안공지 신규 게시물 알림 (" + str(new_num) + "건)"
        # 메일 콘텐츠 - 내용
        body = "보안공지 새로운 게시물을 알려드립니다.(❁´◡`❁)<br><br><br>" + article + ""
        bodyPart = MIMEText(body, 'html', 'utf-8')
        message.attach(bodyPart)

        # 메일 발송
        session.sendmail(from_addr, to_addr, message.as_string())

    except Exception as e:
        return 9

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
        return list(set(new_article_list))
    return sorted(list(set(new_article_list) - set(article_list)))


def article_to_html(newest_article: list):
    text = ''
    for i in newest_article:
        text += i + '<br>'
    return text


log = Log()
properties = Properties()

print('''
.______          _______.     _______.       .______     ______    __    __    ______   
|   _  \        /       |    /       |       |   _  \   /  __  \  |  |  |  |  /  __  \  
|  |_)  |      |   (----`   |   (----` ______|  |_)  | |  |  |  | |  |__|  | |  |  |  | 
|      /        \   \        \   \    |______|   _  <  |  |  |  | |   __   | |  |  |  | 
|  |\  \----.----)   |   .----)   |          |  |_)  | |  `--'  | |  |  |  | |  `--'  | 
| _| `._____|_______/    |_______/           |______/   \______/  |__|  |__|  \______/   v1.0

''')

flag = 0
while flag == 0:
    flag_num = input('시작하시겠습니까? [y/n] : ')

    if flag_num.lower() =='y' :
        flag = 1
    if flag_num.lower() =='n':
        quit()


if log.new_log_file():
    pass

mail_list = get_text_list(file_name='./mail_list.txt')
get_text_list(file_name='./article_lists.txt')

log.add_log(comment='소스코드 https://github.com/TwoIceFIsh/RSS-Boho')
log.add_log(comment='설명 https://twoicefish-secu.tistory.com/428')

if properties.new_config_file() is True:
    log.add_log(comment='[-] 새로운 설정 파일이 생성 되었습니다.')
    log.add_log(comment='[-] 설정 후 실행해 주세요.')
    log.add_log(comment=f'[-] =======================================')
    log.add_log(comment=f'[-] {os.path.dirname(__file__)}\\config.ini')
    log.add_log(comment=f'[-] {os.path.dirname(__file__)}\\mail_list.txt')
    log.add_log(comment=f'[-] =======================================')
    properties.set()
    os.system('pause')
    sys.exit()

propertiesq = configparser.ConfigParser()  ## 클래스 객체 생성
propertiesq.read('.\\config.ini')  ## 파일 읽기
default = propertiesq['DEFAULT']

if 'myid@gmail.com' == default['google_gmail_id'] or 'xxxxyyyyzzzzqqqq' == default['google_app_pw']:
    log.add_log(comment=f'[!] 자신만의 설정값으로 변경해 주세요')
    log.add_log(comment=f'[-] {os.path.dirname(__file__)}\\config.ini')
    os.system('pause')
    sys.exit()


if mail_list is None:
    log.add_log(comment=f'[!] 이메일 리스트가 비어 있습니다. 추가해주세요')
    log.add_log(comment=f'[-] {os.path.dirname(__file__)}\\mail_list.txt')
    print(f'''
            작성예시({os.path.dirname(__file__)}\\mail_list.txt)
            
            asdfadsf@gmail.com
            sdijovjid@test.com
            sdjico@sdco.net
            
            ...
            
            ''')
    os.system('pause')
    sys.exit()
else:
    for i in mail_list:
        if '@' not in i or '.' not in i:
            log.add_log(comment=f'[!] {i} 올바른 이메일 형식이 아닙니다. 확인해 주세요')
            print(f'''
            작성예시({os.path.dirname(__file__)}\\mail_list.txt)
            
            asdfadsf@gmail.com
            sdijovjid@test.com
            sdjico@sdco.net
            
            ...
            
            ''')
            os.system('pause')
            sys.exit()

while True:
    log.add_log(comment=f'[-] ======RSS-BOHO Start======')

    # 신규 게시물 확인
    article_list = get_text_list(file_name='./article_lists.txt')
    new_article_list = get_data(url='https://www.boho.or.kr/data/secNoticeList.do')
    newest_article = what_is_new_article(article_list=article_list, new_article_list=new_article_list)

    # 이메일 목록을 획득 및 메일 발송
    if len(newest_article) > 0:
        log.add_log(comment=f'=====================================')
        log.add_log(comment=f'[-] {len(newest_article)}건의 신규 게시물이 발견 되었습니다 ')
        article_text = article_to_html(newest_article=newest_article)
        for i in enumerate(newest_article, start=1):
            log.add_log(comment=f'[{i[0]}] {i[1].split(":")[0].replace(" URL ","")}(New)')
        log.add_log(comment=f'=====================================')

        # 메일리스트 확인
        mail_list = get_text_list(file_name='./mail_list.txt')
        if mail_list is None:
            log.add_log(comment=f'[!] 이메일 리스트가 비어 있습니다. 추가해주세요')
            log.add_log(comment=f'[!] 15분후에 메일 발송을 시도 합니다.')
            log.add_log(comment=f'[!] (신규 게시글 정보 업데이트 스킵)')
        else:

            pid = default['google_gmail_id']
            ppw = default['google_app_pw']

            for to in mail_list:
                message = send_mail(id=pid,pw=ppw,article=article_text, new_num=len(newest_article), to_ad=to)
                if message ==9:
                    log.add_log(comment=f'[!] Google ID 및 Google API PW를 일치하지 않거나 존재하지 않습니다 확인해 주세요')
                    log.add_log(comment=f'[-] {os.path.dirname(__file__)}\\config.ini')
                    os.system('pause')
                    sys.exit()

                else:
                    log.add_log(comment=f'[-] {mail_list}에게 메일을 발송했습니다.')
                    file_set_article(file_name='./article_lists.txt', articles=new_article_list)
                    log.add_log(comment=f'[-] 신규 게시글 정보 업데이트를 완료했습니다.')
                    log.add_log(comment=f'{os.path.dirname(__file__)}\\article_lists.txt')
                    log.add_log(comment=f'[-] 루틴 종료 15분후에 재탐색을 실시 합니다.')
    else:
        log.add_log(comment=f'[-] 새롭게 발견된 기사가 없습니다.')
        log.add_log(comment=f'[-] 루틴 종료 15분후에 재탐색을 실시 합니다.')

    time.sleep(900)
