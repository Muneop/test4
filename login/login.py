
'''
@app.route('/')
def login_form():
    return render_template('login.html',id=None)

@app.route('/input', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        if(request.form['id'] == 'admin' and request.form['pw'] == 'admin123'):
            session['logged'] = True
            session['user'] = request.form['id']
            return redirect(url_for('mmg_recommendation',id=request.form['id']))
        else:
            return """=<script>alert("wrong!");location.href='/';</script>"""
    else:
        return """<script>alert("not allowd!");location.href='/';</script>"""

app.secret_key = 'sample_secret'
'''

'''
HTML로 넘겨줘야 되는 값들
id 
pwd
-> 파이썬, html 변수명 동일하게 진행해 줘야 함.
'''






"""Flask Login Example and instagram fallowing find"""
from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from math import sqrt
from module import dbModule
from flask import Flask, url_for, render_template, request, redirect, session


login_function = Blueprint('login', __name__, url_prefix='/login')


@login_function.route('/', methods=['GET','POST'])
def home():
    '''sesssion control'''
    '''
    if not session.get('logged_in'):
        print(session.get('logged_in'))
        print("여기요1")
        return render_template('MMG.html')
    else:
        print("여기요2")
        if request.method=='POST':
            username=request.form['id']
            return render_template('MMG.html',id=username)
        return render_template('MMG.html')
        '''
    if request.method == 'GET':
        print("여기요3")
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['id']
        password = request.form['pwd']
        db_class = dbModule.Database()
        # SELECT * FROM user where password = 12345678
        sql = "SELECT * FROM testDB.user WHERE user_name = '" + username + "' AND password = " + password
        print(sql)
        user_list = db_class.executeAll(sql)
        print(user_list)
        try:
            if user_list is not None:
                return redirect(url_for('recommendation', id=username))
            else:
                return redirect(url_for('home'))
        except:
            return redirect(url_for('home'))


@login_function.route('/execute/', methods=['GET','POST'])
def login():
    '''Login Form'''
    if request.method == 'GET':
        print("여기요3")
        return render_template('login.html')
    elif request.method == 'POST':
        print("여기요4")
        username = request.form['id']
        password = request.form['pwd']
        db_class = dbModule.Database()
        #SELECT * FROM user where password = 12345678
        sql = "SELECT * FROM testDB.user WHERE user_name = '" + username + "' AND password = " + password
        print(sql)
        user_list = db_class.executeAll(sql)
        print(user_list)
        try:
            if user_list is not None:
                session['logged_in']=True
                return redirect(url_for('home',id=username))
            else:
                return redirect(url_for('home'))
        except:
            return redirect(url_for('home'))






@login_function.route('/register/', methods=['GET', 'POST'])
def register():
	"""Register Form"""
	if request.method == 'POST':
		new_user = User(username=request.form['username'], password=request.form['password'])
		db.session.add(new_user)
		db.session.commit()
		return render_template('login.html')
	return render_template('register.html')

@login_function.route("/logout")
def logout():
	"""Logout Form"""
	session['logged_in'] = False
	return redirect(url_for('home'))


if __name__ == '__main__':
	app.debug = True
	db.create_all()
	app.secret_key = "123"
	app.run(host='0.0.0.0')