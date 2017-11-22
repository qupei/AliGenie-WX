import itchat
from http.server import BaseHTTPRequestHandler, HTTPServer
from cgi import parse_header, parse_multipart
from threading import Thread
from urllib.parse import parse_qs
import json

class WXRequestHandler(BaseHTTPRequestHandler):

    wechatNickNames = {
        "爸爸" : "胖梁",
        "妈妈": "YOYO"
    }

    def parse_JSON(self):
        ctype, pdict = parse_header(self.headers['content-type'])
        if ctype == 'application/json':
            length = int(self.headers['content-length'])
            data = self.rfile.read(length)
            print(data)
            return json.loads(data)
        else:
            length = int(self.headers['content-length'])
            data = self.rfile.read(length)
            print(data)
            return json.loads(data)

    def do_POST(self):
        print(self.path)
        
        resp = {}
        if self.path == "/send" :
            jsonData = self.parse_JSON()
            print(jsonData)
            resp = self.do_SEND(jsonData)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(json.dumps(resp, ensure_ascii=False),"utf8"))
        return

    def do_GET(self):
        print("do_GET:%s", self.path)
        resp = {
            "returnCode":"0",
            "returnValue":{
                "reply": "不支持浏览器请求",
                "resultType": "RESULT"
            }
        }
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(json.dumps(resp, ensure_ascii=False),"utf8"))
        return

    def parse_SLOT(self, jsonData):
        slots = {}
        for slot in jsonData['slotEntities']:
            slots[slot['intentParameterName']] = slot

        return slots

    def do_SEND(self, jsonData):
        slots = self.parse_SLOT(jsonData)
        if 'target' in slots :
            target = slots['target']['standardValue']
        else:
            target = "爸爸"

        nickName = self.wechatNickNames[target]

        msg = jsonData['utterance'] + " [天猫精灵]"
        
        users = itchat.search_friends(nickName=nickName)
        if len(users) == 0 :
            reply = "没有找到接收者"
        else:
            user = users[0]
            print(user)
            itchat.send(msg, toUserName=user.userName)
            reply = "发送成功"

        resp = {
            "returnCode":"0",
            "returnValue":{
                "reply": reply,
                "resultType": "RESULT"
            }
        }
        return resp

def runHttp(port):
    print('starting server...')

    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, WXRequestHandler)
    print('running http server...')
    httpd.serve_forever()


@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    print(msg.user['NickName'], msg.text)
    return "收到 [天猫精灵]"

def loginCallback():
    server = Thread(target=runHttp, args=[8081])
    server.start()

itchat.auto_login(loginCallback=loginCallback, hotReload=True, enableCmdQR=False)
itchat.run()