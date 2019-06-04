from flask import Flask, render_template, url_for, jsonify, redirect, request, session
from test import test
app = Flask(__name__)


@app.route('/')
def mmg_recommendation():
    return render_template('MMG.html',id=None)

message_id = 10
@app.route("/message/<int:message_id>")
def get_message(message_id):
    return "message id: %d" % message_id

@app.route('/json_test')
def hello_json():
    data = {'name' : 'Aaron', 'family' : 'Byun'}
    return jsonify(data)

@app.route('/success/<name>')
def success(name):
   return 'welcome %s' % name



#####test
#구구단초기 화면을 보여주는모습임.
@app.route('/googooclass')
@app.route('/googooclass/<int:num>')
def inputTest(num=None):
    return render_template('test.html', num=num)


@app.route('/calculate', methods=['POST'])
def calculate(num=None):
    if request.method == 'POST':
        temp = request.form['num']
    else:
        temp = None
    return redirect(url_for('inputTest', num=temp))

####test끝



@app.route('/html_test')
def hello_html():
   return render_template('login_test.html')


@app.route('/hello/&lt;user&gt;')
def hello_name(user):
   return render_template('hello.html', name = user)




#모듈화 시킨 이 후 간단하게 실행시키는 법
#테스트하고자 하는 모듈을 from~import한다. from에는 해당 모듈의 파일 명까지 import에는 blueprint가 할당된 변수 이름을
from test_blueprint.test_blue import test2
#app이 주 서버 실행파일이므로 app에 test모듈을 등록한다(register_blueprint)
app.register_blueprint(test2)


from test.test import test1
app.register_blueprint(test1)

from login.login import login_function
app.register_blueprint(login_function)


if __name__ == '__main__':
    #with app.test_request_context():
    #    print(url_for('hello'))
    #    print(url_for('get_profile', username='flash'))

    app.run(host='0.0.0.0',debug=True,port=8080)
