from flask import Blueprint, request, render_template, flash, redirect, url_for

# 추가할 모듈이 있다면 추가

test2 = Blueprint('app', __name__, url_prefix='/')


@test2.route('/fucking_test', methods=['GET'])
def index():
    # /main/index.html은 사실 /project_name/app/templates/main/index.html을 가리킵니다.
    return render_template('test.html')