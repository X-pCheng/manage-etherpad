import functools
import time
from flask import Flask, render_template, redirect, request, session, url_for
from etherpad_lite import EtherpadLiteClient
from conf.my_config import Config


def etherpad_client(my_config: dict = Config, param={}):
    base_params = {'apikey': my_config['apikey']}
    base_url = my_config['web_url'] + '/api'
    api_version = my_config['api_version']
    c = EtherpadLiteClient(
        base_params=base_params, base_url=base_url, api_version=api_version)
    if isinstance(param, dict) and param != {}:
        (c.base_params).update(param)
    return c


def list_pad_id(c: EtherpadLiteClient, searchText=''):
    # https://etherpad.org/doc/v1.9.4/index.html
    # 全部笔记查询
    pad_id_list = []
    try:
        pad_id_list = (c.listAllPads())['padIDs']
        if searchText and searchText != '':
            pad_id_list = list(
                filter(lambda item: item.find(searchText.strip()) >= 0, pad_id_list))
        return {'status': 0, 'msg': '搜索完成', 'data': pad_id_list}
    except Exception as e:
        print(e)
        return {'status': 1, 'msg': e, 'data': None}


def get_pads_info_by_id(c, pad_id_list):
    pad_header = ['pad_id', 'coor_link', 'read_only_link',
                  'last_edited', 'coor_count', 'editing_count']
    pad_list = []
    for i in range(len(pad_id_list)):
        pad_row = []

        pad_id = pad_id_list[i]
        pad_row.append(pad_id)

        web_url = Config['web_url']
        coor_link = web_url + '/p/'+pad_id
        pad_row.append(coor_link)

        param = {'padID': pad_id_list[i]}
        c = etherpad_client(param=param)

        read_only_link = (c.getReadOnlyID())['readOnlyID']
        pad_row.append(web_url+'/p/'+read_only_link)

        timestamp = ((c.getLastEdited())['lastEdited'])/1000
        last_edited = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        pad_row.append(last_edited)

        coor_count = len((c.listAuthorsOfPad())['authorIDs'])
        pad_row.append(coor_count)

        editing_count = (c.padUsersCount())['padUsersCount']
        pad_row.append(editing_count)

        pad_list.append(dict(zip(pad_header, pad_row)))
    return pad_list


def create_pad(c, pad_id):
    param = {'padID': pad_id}
    try:
        c = etherpad_client(param=param)
        c.createPad()
        return {'status': 0, 'msg': '['+pad_id+']创建成功', 'data': pad_id}
    except Exception as e:
        print(e)
        return {'status': 1, 'msg': e, 'data': None}


def delete_pad(c, pad_id):
    param = {'padID': pad_id}
    try:
        c = etherpad_client(param=param)
        c.deletePad()
        return {'status': 0, 'msg': '['+pad_id+']删除成功', 'data': pad_id}
    except Exception as e:
        print(e)
        return {'status': 1, 'msg': e, 'data': None}


def login_required(func):
    @functools.wraps(func)
    def inner(*args, **keyargs):
        username = session.get('username')
        # print('==========Session==========')
        # print(f'session username:{username}')
        if username:
            return func(*args, **keyargs)
        else:
            return redirect(url_for('signin'))
    return inner


app = Flask(__name__, static_folder='static', template_folder='templates')
# 密钥
app.config['SECRET_KEY'] = 'CSaSvOU6h1iMb15s+GsV5TuKYSbREcBZ/g1Gjh9nCec='
# 设置session的过期时间
app.config['PERMANENT_SESSION_LIFETIME'] = 7*24*60*60
# 指定端口


@app.route('/favicon.ico')
def favicon():
    # 静态路径访问的默认实现，send_static_file,
    # 把静态文件发给浏览器
    return app.send_static_file('favicon.ico')


@app.route('/', methods=['GET', 'POST'])
def index():
    print('==========/ Request==========')
    return redirect(url_for('signin'))


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    print('==========signin Request==========')
    msg = ''
    username = session.get('username')
    if username:
        return redirect(url_for('home'))
    elif request.method == 'POST':
        print(request.form)
        username = request.form.get('username')
        password = request.form.get('password')
        for user in Config['users']:
            if username == user["username"] and password == user["password"]:
                session['username'] = username
                session.permanent = True
                return redirect(url_for('home'))
        msg = '用户名或密码输入错误'
        print(msg)
        return render_template('signin.html', msg=msg)
    return render_template('signin.html')


@app.route('/signout', methods=['GET', 'POST'])
def signout():
    session.pop('username')
    res = {'staus': 0, 'msg': '注销成功'}
    print(res)
    return res


@app.route('/home', methods=['GET', 'POST'])
def home():
    print('==========home Request==========')
    username = session.get('username')
    if username:
        return render_template('home.html')
    else:
        return redirect(url_for('signin'))


@app.route('/listpad', methods=['POST'])
@login_required
def list_pad():
    print('==========listpad Request==========')
    searchText = request.get_json()['searchText']
    c = etherpad_client()
    res = list_pad_id(c, searchText)
    if res['status'] == 0:
        pad_list = get_pads_info_by_id(c, res['data'])
        res['data'] = pad_list
    print(res)
    return res


@app.route('/newpad', methods=['POST'])
@login_required
def new_pad():
    print('==========newpad Request==========')
    pad_id = request.get_json()['padID']
    c = etherpad_client()
    res = create_pad(c, pad_id)
    print(res)
    return res


@app.route('/delpad', methods=['POST'])
@login_required
def del_pad():
    print('==========delpad Request==========')
    pad_id = request.get_json()['padID']
    c = etherpad_client()
    res = delete_pad(c, pad_id)
    print(res)
    return res


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config['web_port'])
