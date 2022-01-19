import sqlite3
import time
from turtle import pos
from requests import post
import yaml
import json
import push_msg

def create_database():
    conn = sqlite3.connect('src.db')
    c = conn.cursor()
    try:
        c.execute("""
        CREATE TABLE src_project(
            platform        TEXT     NOT NULL,
            id              INT,
            company_name    TEXT     NOT NULL,
            begintime       TEXT,
            endtime         TEXT
        );
        """)
    except Exception as e:
        print(e)
    conn.commit()
    conn.close()

def load_config():
    with open('config.yaml', 'r') as f:
        config = yaml.load(f,Loader=yaml.FullLoader)
        if int(config['dingding'][0]['enable'])==1:
            dingding_webhook = config['dingding'][1]['webhook']
            dingding_secretKey = config['dingding'][2]['secretKey']
            app_name = config['dingding'][3]['app_name']
            return app_name,dingding_webhook,dingding_secretKey
        elif int(config['feishu'][0]['enable']) == 1:
            feishu_webhook = config['feishu'][1]['webhook']
            app_name = config['feishu'][2]['app_name']
            return app_name,feishu_webhook,feishu_webhook
        elif int(config['server'][0]['enable']) == 1:
            server_sckey = config['server'][1]['sckey']
            app_name = config['server'][2]['app_name']
            return app_name,server_sckey
        elif int(config['tgbot'][0]['enable']) ==1 :
            tgbot_token = config['tgbot'][1]['token']
            tgbot_group_id = config['tgbot'][2]['group_id']
            app_name = config['tgbot'][3]['app_name']
            return app_name,tgbot_token,tgbot_group_id
        elif int(config['tgbot'][0]['enable']) == 0 and int(config['feishu'][0]['enable']) == 0 and int(config['server'][0]['enable']) == 0 and int(config['dingding'][0]['enable']) == 0:
            print("[-] 配置文件有误，enable为1不存在")

# 获取补天src里的新项目
def get_butian_src():
    platform = "butian"
    post_data = post('https://www.butian.net/Reward/corps')
    data = json.loads(post_data.text)
    data = data['data']['list']
    new = []
    for x in data:
        if len(find_compand_by_id(x['company_id'],platform)) == 0:
            new.append([x['company_id'],x['company_name'],"1641041268","1641041268"])
            # print("补天 新增资产 {}".format(x['company_name']))
    if len(new) != 0:
        insert_new_compand(new,platform)
        title = "补天有 "+str(len(new))+"个新项目"
        msg = []
        for x in new:
            msg.append(x['company_name'])
        send_news(title,str(msg))

# 获取火线src里的新项目
def get_huoxian_src():
    platform= "huoxian"
    page = 1
    headers = {'Content-Type': 'application/json'}
    new = []
    while True:
        data={"page":page,"page_size":10}
        response_data =post('https://www.huoxian.cn/fireapi/fireapp/projectList/',headers=headers,data=json.dumps(data))
        if response_data.json()["data"] != []:
            results = response_data.json()["data"]['results']
            for x in results:
                if len(find_compand_by_id(x['id'],platform)) == 0:
                    new.append([x['id'],x['name'],x['begintime'],x['endtime']])
            page+=1
        else:
            break
    if len(new) != 0:
        insert_new_compand(new,platform)
        title = "火线 "+str(len(new))+"个新项目"
        msg = []
        for x in new:
            msg.append(x[1])
        send_news(title,str(msg))

def find_compand_by_id(id,platform):
    conn = sqlite3.connect('src.db')
    cur = conn.cursor()
    sql_grammar = "SELECT id FROM src_project WHERE id = '{}' and platform='{}';".format(id,platform)
    cursor = cur.execute(sql_grammar)
    return list(cursor)

# list [id,compand_name,time]
def insert_new_compand(list,platform):
    conn = sqlite3.connect('src.db')
    cur = conn.cursor()
    try:
        for x in list:
            sql_grammar="INSERT INTO src_project (platform,id,company_name,begintime,endtime) VALUES ('{}',{},'{}',date({},'unixepoch'),date({},'unixepoch'))".format(platform,x[0],x[1],x[2],x[3])
            # print(sql_grammar)
            cur.execute(sql_grammar)
    except Exception as e:
        print(e)
    conn.commit()
    conn.close()


def send_news(title,msg=""):
    if load_config()[0] == "dingding":
        push_msg.dingding(title, msg,load_config()[1],load_config()[2])
    elif load_config()[0] == "server":
        push_msg.server(title, msg,load_config()[1])
    elif load_config()[0] == "tgbot":
        push_msg.tgbot(title,msg,load_config()[1],load_config()[2])


if __name__ == "__main__":
    # print("init")
    create_database()
    # print("initial done")
    send_news("src_monitor","连接成功")
    try:
        while True:
            get_butian_src()
            get_huoxian_src()
            time.sleep(60*60)
    except KeyboardInterrupt:
        print("end")
    except Exception as e:
        print(e)
        send_news("[error] src_monitor",e)
