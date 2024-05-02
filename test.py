from flask import Flask, request
 
from io import BytesIO
 
import requests
from bs4 import BeautifulSoup
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (ApiClient, Configuration, MessagingApi, MessagingApiBlob, ReplyMessageRequest, TextMessage)
from linebot.v3.webhooks import (ImageMessageContent, MessageEvent, TextMessageContent)
from PIL import Image
from pyzbar import pyzbar

from fake_useragent import UserAgent



# 建立 Flask Instance
app = Flask("LineBot")
configuration = Configuration(access_token="F+QrKu+UOekxQLVJvIW3u9z2sV6eNretnxwjVXK+5L5NJuMTlexz7/uS5ZLijHYtp5DoEKlD7pM+bBQwWvPiKn1diRAG3i36Dd8BgoDl5fmcUSqvEqFJHSbyhMaM3IEpsla/NzZjLnQvLVF2tkaUBgdB04t89/1O/w1cDnyilFU=") #CHANNEL_ACCESS_TOKEN
handler = WebhookHandler("d7ab3c2d8dd4b55fe99ed0f8736796bf") #CHANNEL_SECRET


# 定義路由
@app.get("/")
def index():
    return "Hello World"


@app.post("/callback")
def callback():
    # 獲取簽章
    signature: str = request.headers["X-Line-Signature"]
 
    # 獲取請求內容
    body: str = request.get_data(as_text=True)
    print(body)
 
    # 處理事件
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        # 若請求內的簽章與計算結果不符則報錯
        return "Invalid signature.", 400
 
    return "OK"


# 處理文字訊息
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    # 建立 ApiClient 實例
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
 
        # 獲取使用者發送的訊息
        msg: str = event.message.text

        if (msg[0] == "！" or msg[0] == "!"):
            #回覆原訊息
            line_bot_api.reply_message_with_http_info(
               ReplyMessageRequest(
                   reply_token=event.reply_token,
                   messages=[
                       TextMessage(text=msg),
                   ],
               )
            )
 
        return "OK"
    

# 接收圖片訊息
@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image(event: MessageEvent):
    # 建立 ApiClient 實例
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        api_blob = MessagingApiBlob(api_client)
 
        # 獲取圖片內容
        image_content = api_blob.get_message_content(event.message.id)
        image = Image.open(BytesIO(image_content))
 
        # 解碼圖片中的 QR Code
        barcodes = pyzbar.decode(image)
 
        if len(barcodes) > 0:
            code = barcodes[0].data.decode("utf-8")
 
            print("QR Code:", code)


#
def get_viewstate(soup: BeautifulSoup):#不存在就return 空字串
    event_target = soup.select_one("#__EVENTTARGET")["value"] if soup.select_one("#__EVENTTARGET") else ""
    event_argument = soup.select_one("#__EVENTARGUMENT")["value"] if soup.select_one("#__EVENTARGUMENT") else ""
    viewstate = soup.select_one("#__VIEWSTATE")["value"]
    viewstate_generator = soup.select_one("#__VIEWSTATEGENERATOR")["value"]
    event_validation = soup.select_one("#__EVENTVALIDATION")["value"]
 
    return {
        "__EVENTTARGET": event_target,
        "__EVENTARGUMENT": event_argument,
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstate_generator,
        "__EVENTVALIDATION": event_validation,
    }


#
def signin(username: str, password: str, code: str):
    # ASP.NET 會驗證 session cookie, Session() 可以於多請求中共享 cookie
    session = requests.Session()
    
    # 先獲取 /login.aspx 頁面的 view state
    headersg = {'User-Agent': UserAgent().random}
    res = session.get("https://signin.fcu.edu.tw/clockin/login.aspx", headers=headersg) #https://ccu.0xian.dev/clockin/login.aspx
    soup = BeautifulSoup(res.text, "html.parser")
    data = get_viewstate(soup)
    
    # 加上登入用到的資料
    data["LoginLdap$UserName"] = username
    data["LoginLdap$Password"] = password
    data["LoginLdap$LoginButton"] = "登入"
 
    # 連同 view state 一起發送回去
    headersh = {'User-Agent': UserAgent().random}
    res = session.post("https://signin.fcu.edu.tw/clockin/login.aspx", data=data, headers=headersh) #https://ccu.0xian.dev/clockin/login.aspx
    
    # 登入成功會被導到 /Student.aspx
    if not res.url.endswith("/Student.aspx"):
        return "登入失敗"
 
    # 打卡
    res = session.get(f"https://signin.fcu.edu.tw/clockin/ClassClockin.aspx?param={code}") #https://ccu.0xian.dev/clockin/ClassClockin.aspx?param={code}
    soup = BeautifulSoup(res.text, "html.parser")
    
    # 若 LabelNote 是空的則代表成功
    return soup.select_one("#LabelNote").text or "打卡成功"


# 接收圖片訊息
@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image(event: MessageEvent):
    # 建立 ApiClient 實例
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        api_blob = MessagingApiBlob(api_client)
 
        # 獲取圖片內容
        image_content = api_blob.get_message_content(event.message.id)
        image = Image.open(BytesIO(image_content))
 
        # 解碼圖片中的 QR Code
        barcodes = pyzbar.decode(image)
 
        if len(barcodes) > 0:
            code = barcodes[0].data.decode("utf-8")
 
            #print("QR Code:", code)
            #status = signin("D1248916", "william93kao0207w", code) ##改 "id", "password"
            #print("Signin:", status)

            s = ""
            name = ["高慶霖", "曾偉倫", "陳宥甫", "周竑宇", "王兆偉", "鄭佑誠", "江浩瑜"]
            id = ["D1248916", "D1210267", "D1249313", "D1209305", "D1285001", "D1285165", "D1268264"]
            passwd = ["william93kao0207w", "e30330e30330", "Ff47921352fF", "943526yhnkjh943526", "Brant1234567890", "aashow610331",  "Ayamedochi1213"]
            for i in range(len(id)):
                status = signin(id[i], passwd[i], code) ##改 "id", "password"
                if(i==len(id)-1):
                    s = s + name[i] + " "  + str(id[i]) + " >> " + status
                else:
                    s = s + name[i] + " " + str(id[i]) + " >> " + status + "\n"
                #s.append(status)
                #print("Signin:", status)
                print(f"Signin: {id[i]} >> {status}")

            status = str(id[-1]) + " >> " + status
            line_bot_api.reply_message(ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=s),],))

            # id = ["D1248916", "D1210267"]
            # passwd = ["william93kao0207w", "e30330e30330"]
            # for i in range(len(id)):
            #     status = signin(id[i], passwd[i], code) ##改 "id", "password"
            #     print("Signin:", status)

# 程式執行時啟動伺服器
    if __name__ == "__main__":
        app.run("0.0.0.0", port=8080)