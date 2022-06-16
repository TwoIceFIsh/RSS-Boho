import datetime
import time
from mail_func import *

while True:
    print('Scanning : ' + str(datetime.datetime.now()))

    # 신규 게시물 확인
    article_list = get_text_list(file_name='./article_lists.txt')
    new_article_list = get_data(url='https://www.boho.or.kr/data/secNoticeList.do')
    newest_article = what_is_new_article(article_list=article_list, new_article_list=new_article_list)

    # 신규 게시글 파일 작성성
    file_set_article(file_name='./article_lists.txt', articles=new_article_list)

    # 이메일 보내기
    mail_list = get_text_list(file_name='./mail_list.txt')

    if len(newest_article) > 0:

        article_text = article_to_html(newest_article=newest_article)

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
