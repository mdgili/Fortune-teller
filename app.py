
from flask import Flask, render_template, jsonify, request
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from pymongo import MongoClient

app = Flask(__name__)

# client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
client = MongoClient('mongodb://park:park@localhost',27017)
db = client.myproject

@app.route('/')
def home():
    return render_template('first.html')

@app.route('/1')
def home2():
    word_receive = request.args['q']
    return render_template('second-1.html',q=word_receive)

@app.route('/2')
def home3():
    return render_template('third.html')

@app.route('/dream', methods=['POST'])
def post_dream():
    word_receive = request.form['word_give']

    if len(list(db.myproject.find({'search_word': word_receive}))) > 0:
        return jsonify({'result': 'success', 'msg': '검색을 시작합니다!'})

    plusUrl = urllib.parse.quote_plus((word_receive) + '꿈해몽')

    pageNum = 1
    lastPage = 21

    while pageNum < lastPage + 1:
        url = f'https://search.naver.com/search.naver?date_from=&date_option=0&date_to=&dup_remove=1&nso=&post_blogurl=&post_blogurl_without=&query={plusUrl}&sm=tab_pge&srchby=all&st=sim&where=post&start={pageNum}'

        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html, 'html.parser')

        titles = soup.find_all(class_='sh_blog_title')
        comments = soup.find_all(class_='sh_blog_passage')
        days = soup.find_all(class_='txt_inline')

        if len(titles) == len(comments) and len(comments) == len(days):
            for i in range(len(titles)):
                title = titles[i]
                comment = comments[i]
                day = days[i]

                # print(title.attrs['title'])
                # print(title.attrs['href'])
                # print(comment.text)
                # print(day.text)

                my_title = title.attrs['title']
                my_url = title.attrs['href']
                my_comment = comment.text
                my_day = day.text

                if my_title is None or my_title == '':
                    continue

                doc = {
                    'title': my_title,
                    'url': my_url,
                    'comment': my_comment,
                    'day': my_day,
                    'search_word': word_receive
                }

                db.myproject.insert_one(doc)

        pageNum += 10

    return jsonify({'result': 'success', 'msg': '검색을 시작합니다!'})



@app.route('/dream', methods=['GET'])
def read_dream():
    word_receive = request.args['q']
    data = list(db.myproject.find({'search_word': word_receive}, {'_id': False}))
    return jsonify({'result': 'success', 'allData': data})

@app.route('/starluck', methods=['POST'])
def get_starluck():
    star = request.form['star']
    plusUrl = urllib.parse.quote_plus(star)
    url = 'https://search.naver.com/search.naver?sm=top_hty&fbm=1&ie=utf8&query=' + plusUrl
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    fortunes = soup.find_all(class_='text _cs_fortune_text')

    fortuneTexts = [t.text for t in fortunes]

    return jsonify({'result': 'success', 'fortunes': fortuneTexts})


@app.route('/animalluck', methods=['POST'])
def get_animalluck():
    animal = request.form['animal']
    plusUrl = urllib.parse.quote_plus(animal)
    url = 'https://search.naver.com/search.naver?sm=top_hty&fbm=1&ie=utf8&query=' + plusUrl
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    animalFortunes = soup.find_all(class_='text _cs_fortune_text')

    animalFortuneTexts = [t.text for t in animalFortunes]

    return jsonify({'result': 'success', 'animalFortunes': animalFortuneTexts})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
