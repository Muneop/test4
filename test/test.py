# -*- coding: utf-8 -*-
import ssl
import random

from flask import Blueprint, request, render_template, flash, redirect, url_for, g
from math import sqrt
from operator import itemgetter
from datetime import datetime


####뇬뇬뇬의 코드
from urllib.request import urlopen, Request
import urllib
import bs4
from bs4 import BeautifulSoup
####뇬뇬의 코드

from module import dbModule

test1 = Blueprint('test', __name__, url_prefix='/recommendation')

local_food_evaluation_list = []
guser = {'id':'', 'emotion':0, 'location':'' ,'temperature': None , 'weather':None,'RorS':None ,'count' : 1,'list':[],'eval_history':None,'time':None,'foodname':None}


#g.user = {'user_name':'','cur_time':None,'cur_cloud':None,'cur_RorS':None,'cur_temp':None,'cur_emotion':None}

def sim_pearson(data, name1, name2):  # 사용자의 음식평가리스트를 통해 유사도 분석할때
    # X : name1의 음식평점
    # Y : name2의 음식평점
    sumX = 0  # X의 합
    sumY = 0  # Y의 합
    sumPowX = 0  # X 제곱의 합
    sumPowY = 0  # Y 제곱의 합
    sumXY = 0  # X*Y의 합
    count = 0  # 같은 음식의 갯수

    for i in data[name1]:  # i = key, name1의 음식평가리스트를 쭈욱 비교한다.
        if i in data[name2]:  # name2에서 name1과 똑같은 음식의 평가가 있을떄
            # print(data[name1][i]['name'])
            #print(data[name1][i]['esti'])
            sumX += data[name1][i]['esti']
            sumY += data[name2][i]['esti']
            sumPowX += pow(data[name1][i]['esti'], 2)
            sumPowY += pow(data[name2][i]['esti'], 2)
            sumXY += data[name1][i]['esti'] * data[name2][i]['esti']
            count += 1
    # print(name1,name2,sumX,sumY,sumPowX,sumPowY,sum)
    # 같은 음식에 대해서 한영화에 대한 두명의 평점의 합을 count로 나누고
    # 두명의 영화의 평점의 곲들의 합에 위의 값을 뺴준다.
    # 그리고 이 값들을 X의 제곱을 카운트로 나눠서 이값을 X의 값들의 합에서 빼주고 제곱한것과
    # 밑에도 y동일하게 진행해서 두개의 값을 곱해 위의 값을 나눠줌
    # print(name2,count)
    # print(" ")
    if count == 0:
        return -404
    else:
        if sqrt((sumPowX - (pow(sumX, 2) / count)) * (sumPowY - (pow(sumY, 2) / count)))==0:
            return -404
    return (sumXY - ((sumX * sumY) / count)) / sqrt((sumPowX - (pow(sumX, 2) / count)) * (sumPowY - (pow(sumY, 2) / count)))


def top_match(data, name, index, sim_function=sim_pearson):  # 여러 사용자와의 유사도 구하기
    # data = critics_test
    # name = 'A' #임의로 지정한 사용자 A
    # data는 dictionary
    # name은 기준 사람
    # index는 몇위까지 출력할 것인지
    # sim_function은 위에서 구해놓은 sim_distance함수
    li = []
    for i in data:
        if name != i:
            if sim_function(data, name, i)==-404:
                pass
            else:
                li.append((sim_function(data, name, i), i))  # 유사도, 이름을 튜플에 묶어 리스트에 추가한다.
    li.sort()  # 오름차순 정렬
    li.reverse()  # 내림차순정렬
    return li[:index]


def getRecommendation(data, person, sim_function=sim_pearson):#사용자 평가 기반 유사도 측
    result = top_match(data, person, len(data))
    simSum = 0  # 유사도 합을 위한 변수
    score = 0  # 평점 합을 위한 변수
    li = []  # 리턴을 위한 리스트
    score_dic = {}  # 유사도 총합을 위한 dic
    sim_dic = {}  # 평점 총합을 위한 dic

    for sim, name in result:  # 튜플이므로 한번에
        if sim < 0: continue  # 유사도가 양수인 사람만
        for food in data[name]:
            if food not in data[person]:  # name이 평가를 내리지 않은 음식
                score += sim * data[name][food]['esti']  # 타 사용자의 음식평점 * 유사도
                score_dic.setdefault(food, 0)  # 기본값 설정
                score_dic[food] += score  # 합계 구함
                # print(score_dic)
                # 조건에 맞는 사람의 유사도의 누적합을 구한다
                sim_dic.setdefault(food, 0)
                sim_dic[food] += sim
            score = 0  # 음식이 바뀌었으니 초기화
    # print(score_dic,sim_dic,'\n')
    for key in score_dic:
        score_dic[key] = score_dic[key] / sim_dic[key]  # 평점 총합/ 유사도 총합
        li.append((score_dic[key], key))  # list((tuple))의 리턴을 위해서.
    li.sort()  # 오름차순
    li.reverse()  # 내림차순

    for i in range(len(li)):
        li[i]=li[i][1]

    print('li',li)
    return li


def getRecommendation_status(data,customer):#사용자 상태와 매칭한 추천
    result = []
    for user in data:
        sum = 0
        for food in data[user]:
            time = data[user][food]['esti_time']
            time_text = ''
            if(time>4 and time<10):
                time_text = 'morning'
            elif(time<15):
                time_text = 'lunch'
            elif(time<20):
                time_text = 'dinner'
            else:
                time_text = 'deepnight'
            if(time_text==customer['esti_time']):
                print('time_text',time_text)
                print('esti_time',customer['esti_time'])
                sum+=1
            if(data[user][food]['RorS']==customer['cur_RorS']):
                sum+=1

            sum+=pow(data[user][food]['cloud'] - customer['cur_cloud'],2) + pow(data[user][food]['temp'] - customer['cur_temp'],2) + pow(data[user][food]['emotion'] - customer['cur_emotion'],2)
            sum = 1/(1+sqrt(sum))
            #print(data[user][food])
            result.append((data[user][food]['esti'], data[user][food]['food_name'],sum))
    result.sort(key=itemgetter(2))
    result.reverse()
    result = result[:30]
    result.sort(key=itemgetter(0))
    result.reverse()
    count = 0
    temp = []
    while(count<20):
        for i in result:
            if i not in temp:
                temp.append((i[1]))
                count +=1
    result = temp
    print(result)
    return result


def getFoodEvaluationlist():#to make dictionary
    db_class = dbModule.Database()
    sql = "SELECT * FROM testDB.food_evaluation"
    row = db_class.executeAll(sql)
    local_food_evaluation_list = row
    # print(local_food_evaluation_list)

    sql = "SELECT distinct user_name FROM testDB.food_evaluation"
    row = db_class.executeAll(sql)
    user_list = row
    # print(user_list)
    temp = {}
    #print(temp)

    # 함수화 시켜서 따로 빼도록 하자
    # 사용자별로 구분하여 딕셔너리로 만들기
    for each_user in user_list:
        temp[each_user['user_name']] = {}
    keys_of_list = ['food_name', 'esti_time', 'cloud', 'RorS', 'temp', 'emotion', 'esti']
    for each_esti in local_food_evaluation_list:
        temp[each_esti['user_name']][each_esti['food_name']] = {}
        for i in keys_of_list:
            temp[each_esti['user_name']][each_esti['food_name']][i] = each_esti[i]
    return temp

def getRandomFoodList():
    db_class = dbModule.Database()
    sql = "SELECT * FROM testDB.food_list"
    row = db_class.executeAll(sql)
    random_var = random.randrange(1,len(row))
    #print(random_var)
    result = []
    count = 0
    while(count<20):
        random_var = random.randrange(1, len(row))
        if row[random_var] not in result:
            result.append(row[random_var])
            count = count+1
    for i in range(len(result)):
        result[i] = result[i]['name']
    return result



def getStatus():
    ####뇬뇬뇬의 코드
    enc_location = urllib.parse.quote('모현읍날씨')
    url = "https://search.naver.com/search.naver?ie=utf8&query=" + enc_location
    req = Request(url)
    page = urlopen(req)
    html = page.read()
    # html = requests.get(url)
    soup = bs4.BeautifulSoup(html, 'html5lib')
    st_weat = str(soup.find("p", class_="cast_txt").text)  # 구름파트
    today_weat = st_weat.split(',')  # 구름파트
    weather = today_weat[0]

    temp = soup.find("p", class_="info_temperature").find('span', class_='todaytemp').text
    # temp = soup.find("p",class_="cast_txt")
    temperature = 15

    real_location = str(soup.find("span", {"class": "btn_select"}).text)

    if weather == '비' or weather == '눈':
        guser['weather'] = 5
        word = ''
        if weather == '비':
            word = 'R'
        elif weather == '눈':
            word = 'S'
        guser['RorS'] = word
    else:
        # 맑음, 구름많음, 구름조금, 흐림, 비, 눈
        guser['RorS'] = 'N'
        if weather == '맑음':
            guser['weather'] = 1
        elif weather == '구름조금':
            guser['weather'] = 2
        elif weather == '구름많음':
            guser['weather'] = 3
        elif weather == '흐림':
            guser['weather'] = 4

    guser['location'] = real_location
    guser['temperature'] = temperature
    guser['time'] = datetime.now().hour
    return guser


#초기화면
@test1.route('/', methods=['POST'])
def index():
    print("index(), /")
    guser['location']=None
    guser['count']=1
    guser['eval_history']=None
    guser['id']=(request.form['id'])
    db_class = dbModule.Database()
    sql = "SELECT * FROM testDB.user WHERE user_name = '" + guser['id'] + "'"
    user_list = db_class.executeAll(sql)

    if len(user_list)==0:
        sql = "INSERT INTO testDB.user(user_name) VALUES('" +guser['id']+ "')"
        db_class.executeAll(sql)
        db_class.commit()

    sql = "SELECT * FROM testDB.food_evaluation WHERE user_name = '" + guser['id'] + "'"
    eval_user = db_class.executeAll(sql)
    guser['eval_history']=eval_user
    getStatus()
    esti_time = datetime.now().hour#현재시간 html로 전달
    real_location = guser['location']
    temperature = guser['temperature']
    weather = guser['weather']
    return render_template('foodforme.html', id=guser['id'],user_location = real_location,temperature=temperature,weather=weather,count=guser['count'],cur_time = esti_time)

#프론트와 통신해야될 목록들
# 1. 사용자의 현재상태 입력
# 2. 현재의 날씨, 기타 등등
# 3. 추천을 누르는 순간
# 평가 목록
    # 여러 사용자의 음식 평가를 기반으로 평점 예상 후 추천
    # 현재의 사용자와의 상태가 가장 유사한 음식평가 목록중에서 높은 평점의 음식을 추천

# 추천함수
@test1.route('/execute', methods=['POST'])
def recommendation():
    A = guser['count']
    A = A+1
    guser['count']=A
    guser['emotion'] = int(request.form['emotion'])
    print("여기를 지납니다만!/execute")
    temperature = guser['temperature']
    real_location = guser['location']

    esti_time = datetime.now().hour

    temp_user = {'user_name': guser['id'], 'esti_time': esti_time, 'cur_cloud': 10, 'cur_RorS': 'N', 'cur_temp': temperature, 'cur_emotion': guser['emotion']}
    temp = getFoodEvaluationlist()#DB의 음식평가목록을 딕셔너리로 바꿔서 저장

    C = getRandomFoodList()#랜덤으로 음식을 추천
    if len(guser['eval_history'])<3:
        print('사용자가 한 평가가 없을 경우 일단 사용')
        guser['list'] = C #사용자가 한 평가가 없을 경우 랜덤으로 추천
    else:
        A = getRecommendation_status(temp, temp_user)  # 사용자의 현재상태와 유사한 평가를 가져옴
        B = getRecommendation(temp, guser['id'])  # 사용자의 평가를 기반으로 유사도를 측정
        print('사용자 평가가 3개 이상인 경우 사용하기')
        temp_temp = B+A+C #중복제거하는 부분
        count = 0
        for i in range(len(temp_temp)):
            temp_temp[i]=(temp_temp[i])
        templist = []
        for i in temp_temp:
            if i not in templist:
                templist.append(i)
                print(i)
        guser['list']= templist#사용자 평가가 3개 이상인 경우 사용하기 -> 사용자의 추천 유사도와 매칭한다.
    result = guser['list']
    print(C)
    print(result)
    output = result[0]
    guser['foodname'] = output
    del result[0]
    guser['list'] = result

    real_location = guser['location']
    temperature = guser['temperature']
    weather = guser['weather']
    #return render_template('foodforme.html', recommendation_result=result,id=guser['id'])
    return render_template('foodforme.html', recommendation_result=output, id=guser['id'],user_location = real_location,temperature=temperature,weather=weather,count = guser['count'],cur_time = esti_time)


@test1.route('/execute/onemore', methods=['POST'])
def recommendation_onemore():
    #print(guser['list'])
    guser['count'] = guser['count'] + 1
    guser['emotion'] = int(request.form['emotion'])
    print("여기를 지납니다만/execute/onemore")
    temperature = guser['temperature']

    esti_time = datetime.now().hour

    result = guser['list']
    output = result[0]
    rec_result_temp = output
    guser['foodname'] = output
    del result[0]
    guser['list'] = result

    real_location = guser['location']
    temperature = guser['temperature']
    weather = guser['weather']
    # return render_template('foodforme.html', recommendation_result=result,id=guser['id'])
    return render_template('foodforme.html', recommendation_result=output, id=guser['id'], user_location=real_location, temperature=temperature, weather=weather,count = guser['count'],cur_time = esti_time)


@test1.route('/evaluation', methods=['POST'])
def foodEvaluation():
    # print(guser['list'])
    esti = request.form['score']
    print("여기를 지납니다만/evaluation")
    temp_user = {'user_name': guser['id'],'food_name':guser['foodname'],'esti_time': guser['time'], 'cloud':guser['weather'], 'RorS': guser['RorS'],
                 'temp': guser['temperature'], 'emotion': guser['emotion'],'esti':esti}

    db_class = dbModule.Database()
    sql = "INSERT INTO testDB.food_evaluation(user_name, food_name, esti_time, cloud, RorS, temp, emotion, esti) " \
          "VALUES('" + guser['id'] + "','" +guser['foodname']+ "','"+ repr(guser['time'])+ "','"+repr(guser['weather'])+ \
          "','"+guser['RorS']+ "','"+repr(guser['temperature'])+ "','"+repr(guser['emotion'])+ "','"+esti+ "')"
    print(sql)
    db_class.executeAll(sql)
    db_class.commit()
    esti_time = datetime.now().hour
    real_location = guser['location']
    temperature = guser['temperature']
    weather = guser['weather']
    # return render_template('foodforme.html', recommendation_result=result,id=guser['id'])
    #return redirect(url_for('recommendation_onemore', recommendation_result=rec_result_temp, id=guser['id'], user_location=real_location,temperature=temperature, weather=weather, count=guser['count'], cur_time=esti_time))
    return render_template('foodforme.html', recommendation_result='', id=guser['id'], user_location=real_location, temperature=temperature, weather=weather,count = guser['count'],cur_time = esti_time)


'''
@test1.route('/execute', methods=['POST'])
def recommendation():
    '''

#INSERT 함수 예제
@test1.route('/insert', methods=['GET'])
def insert():
    db_class = dbModule.Database()
    sql = "INSERT INTO testDB.testTable(test) VALUES('%s')" % ('testData')
    db_class.execute(sql)
    db_class.commit()

    return render_template('test.html',
                           result='insert is done!',
                           resultData=None,
                           resultUPDATE=None)



# UPDATE 함수 예제
@test1.route('/update', methods=['GET'])
def update():
    db_class = dbModule.Database()

    sql = "UPDATE testDB.testTable \
                SET test='%s' \
                WHERE test='testData'" % ('update_Data')
    db_class.execute(sql)
    db_class.commit()

    sql = "SELECT idx, test \
                FROM testDB.testTable"
    row = db_class.executeAll(sql)

    return render_template('test.html',
                           result=None,
                           resultData=None,
                           resultUPDATE=row[0])
