import os
import time
import requests
import saucenao
import trace_moe
from config import *
from threading import Thread
from linebot.models import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from flask import Flask, request, abort

app = Flask(__name__)
line_bot_api = LineBotApi(channel_token)
handler = WebhookHandler(channel_serect)
saucenao_quota = ''                         # 新增空字串用於儲存 sausenao 網站回傳的剩餘搜尋次數
id_dict = {'url_search_id': [],
           'img_search_id': [],             # LINE Messaging API 並沒有提供連續對話功能，
           'img_cut_search_id': [],         # 新增空字典用於儲存選擇了搜尋類型的用戶 ID，
           'manga_search_id': [],           # 以便用戶傳送圖片後分別為各個用戶查詢各自的內容
           'illustration_search_id': [],
           'global_search_id': []}


# Heroku 免費方案每 30 分鐘沒有活動就會進入休眠，為避免重啟時傳送訊息的延遲，每 25 分鐘連線到 Heroku 避免進入休眠
def keep_working():
    while True:
        requests.get('https://YOUR_APP_NAME.herokuapp.com')
        time.sleep(25 * 60)


Thread(target=keep_working).start()         # 使用子執行緒同步執行時間計數避免影響主程式執行


# 新增一個 route 供 keep_working 函式可以正常訪問在 Heroku 上的域名
@app.route("/")
def dont_sleep():
    return 'OK'


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 當用戶新增 LINE BOT 為好友，傳送開始搜尋的介面至該用戶
@handler.add(FollowEvent)
def handle_follow(event):
    message = carousel_template_message()                   # 要傳送的訊息內容
    line_bot_api.reply_message(event.reply_token, message)  # 傳送訊息給用戶


# 當用戶傳送的是文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id                          # 去識別化的用戶ID
    text = event.message.text                               # 用戶傳的訊息內容
    emoji = [                                               # 用於回應 Q & A 的表情貼圖
        {
            "index": 0,                                     # 設定表情貼圖在字串的 index 位置
            "productId": "5ac21a13031a6752fb806d57",        # 表情貼圖的名稱編號
            "emojiId": "001"                                # 表情貼圖的編號
        },
        {
            "index": 1,
            "productId": "5ac21a13031a6752fb806d57",
            "emojiId": "092"
        }
    ]
    if text == '網址搜尋':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入圖片網址：'))
        # 如果搜尋前有要求過其他類型的搜尋，則覆蓋前面的要求
        for key, value in id_dict.items():
            if key == 'url_search_id' and user_id not in value:
                id_dict[key].append(user_id)
            if key != 'url_search_id' and user_id in value:
                id_dict[key].remove(user_id)

    elif text == '圖片搜尋' or text == '圖片搜尋(去黑邊)':
        message = TextSendMessage(
            text="請選擇圖片：",
            # 開啟相簿的小按鈕
            quick_reply=QuickReply(
                items=[QuickReplyButton(action=CameraRollAction(label="開啟相簿"))]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
        if text == '圖片搜尋':
            for key, value in id_dict.items():
                if key == 'img_search_id' and user_id not in value:
                    id_dict[key].append(user_id)
                if key != 'img_search_id' and user_id in value:
                    id_dict[key].remove(user_id)

        elif text == '圖片搜尋(去黑邊)':
            for key, value in id_dict.items():
                if key == 'img_cut_search_id' and user_id not in value:
                    id_dict[key].append(user_id)
                if key != 'img_cut_search_id' and user_id in value:
                    id_dict[key].remove(user_id)

    elif text == '漫畫圖源搜尋' or text == '插畫圖源搜尋' or text == '全域搜尋':
        message = TextSendMessage(
            text="請選擇圖片：",
            quick_reply=QuickReply(
                items=[QuickReplyButton(action=CameraRollAction(label="開啟相簿"))]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
        if text == '漫畫圖源搜尋':
            for key, value in id_dict.items():
                if key == 'manga_search_id' and user_id not in value:
                    id_dict[key].append(user_id)
                if key != 'manga_search_id' and user_id in value:
                    id_dict[key].remove(user_id)

        elif text == '插畫圖源搜尋':
            for key, value in id_dict.items():
                if key == 'illustration_search_id' and user_id not in value:
                    id_dict[key].append(user_id)
                if key != 'illustration_search_id' and user_id in value:
                    id_dict[key].remove(user_id)

        elif text == '全域搜尋':
            for key, value in id_dict.items():
                if key == 'global_search_id' and user_id not in value:
                    id_dict[key].append(user_id)
                if key != 'global_search_id' and user_id in value:
                    id_dict[key].remove(user_id)

    elif 'https' in text and user_id in id_dict['url_search_id']:
        # 對 trace.moe 發出網址搜尋要求並回傳搜尋結果與是否發生錯誤
        message, err = trace_moe.url_search(text)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
        id_dict['url_search_id'].remove(user_id) if not err else None

    elif text == 'Q & A':
        # 按鈕樣板訊息
        message = TemplateSendMessage(
            alt_text='Buttons template',
            template=ButtonsTemplate(
                title='Q & A',
                text='請選擇問題',
                actions=[
                    MessageTemplateAction(
                        label='程式如何運作？',
                        text='程式如何運作？'
                    ),
                    MessageTemplateAction(
                        label='為何會顯示讀取失敗？',
                        text='為何會顯示讀取失敗？'
                    ),
                    MessageTemplateAction(
                        label='為何有些標題顯示英文？',
                        text='為何有些標題顯示英文？',
                    ),
                    MessageTemplateAction(
                        label='為何會有搜尋次數上限？',
                        text='為何會有搜尋次數上限？',
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)

    elif text == '程式如何運作？':
        message = ('$$ 當發送搜尋請求時，' +
                   '程式會帶著圖片資料連接到他人運營的網站請求搜尋資料。\n' +
                   '網站會比對伺服器內相似度最高的圖片資料回傳給程式，' +
                   '若沒有得到理想的搜尋結果可能是伺服器內沒有該圖片的資料。')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message, emojis=emoji))

    elif text == '為何會顯示讀取失敗？':
        message = ('$$ 動畫搜尋網站的免費用戶並不支援並列搜尋，' +
                   '當使用動畫搜尋後收到讀取失敗通知有兩個可能：\n' +
                   '一是此時有人也使用本程式進行動畫搜尋。\n' +
                   '二是本月搜尋次數已達上限。\n' +
                   '若使用圖源搜尋也收到讀取失敗通知則是網站讀取失敗或是本日搜尋已達上限。\n' +
                   '有關剩餘搜尋次數可在關於頁面查詢。')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message, emojis=emoji))

    elif text == '為何有些標題顯示英文？':
        message = ('$$ 因為會從非中文網頁抓取資料，' +
                   '搜尋結果的語言依該網頁的回傳格式而定，' +
                   '已透過一些方法將搜尋動畫後取得的資料中文化。')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message, emojis=emoji))

    elif text == '為何會有搜尋次數上限？':
        message = ('$$ 網站運營者為避免過多或惡意的流量請求引發問題，' +
                   '一組 IP（也就是本程式）在固定的時間週期內會有搜尋上限，' +
                   '不同的網站對於搜尋的限制也各有不同，動畫搜尋每月上限為1000次，圖源搜尋每日上限為200次。\n' +
                   '當搜尋次數達到上限，須待下個週期才能繼續搜尋。')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message, emojis=emoji))

    elif text == '關於本程式':
        message = ('LINE BOT ID：@475fahrf\n' +
                   '本機器人不開放加入群組，僅供個人搜尋用。')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

    elif text == '剩餘搜尋次數查詢':
        message = trace_moe.remaining_quota()
        message += '圖源搜尋：\n本日剩餘 ' + str(saucenao_quota) + ' 次搜尋次數'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

    else:
        # 當用戶傳送任意字元即推播搜尋介面至該用戶
        message = carousel_template_message()
        line_bot_api.reply_message(event.reply_token, message)


# 當用戶傳送的是圖片訊息
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    global saucenao_quota
    user_id = event.source.user_id                                        # 去識別化的用戶ID
    message_id = event.message.id                                         # 用戶傳送的圖片訊息編號
    message_content = line_bot_api.get_message_content(message_id)
    with open(message_id + '.jpg', 'wb') as save_img:                     # 下載用戶傳送的圖片至本機
        for chunk in message_content.iter_content():
            save_img.write(chunk)

    if user_id in id_dict['img_search_id'] or user_id in id_dict['img_cut_search_id']:
        cut = True if user_id in id_dict['img_cut_search_id'] else False  # 是否要自動切除螢幕截圖黑邊
        with open(message_id + '.jpg', 'rb') as load_img:                 # 打開用戶傳送的圖片檔案
            # 對 trace.moe 發出圖片搜尋要求並回傳搜尋結果與是否發生錯誤
            message, err = trace_moe.img_search(load_img, cut)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
            if cut:
                id_dict['img_cut_search_id'].remove(user_id) if not err else None
            else:
                id_dict['img_search_id'].remove(user_id) if not err else None

    elif user_id in id_dict['manga_search_id']:
        with open(message_id + '.jpg', 'rb') as load_img:
            # 對 saucenao 發出圖片搜尋要求並回傳搜尋結果、剩餘搜尋次數與是否發生錯誤
            message, saucenao_quota, err = saucenao.img_search(load_img, '37')  # 37: 漫畫搜尋
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
            id_dict['manga_search_id'].remove(user_id) if not err else None

    elif user_id in id_dict['illustration_search_id']:
        with open(message_id + '.jpg', 'rb') as load_img:
            message, saucenao_quota, err = saucenao.img_search(load_img, '5')   # 5: PIXIV 插畫搜尋
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
            id_dict['illustration_search_id'].remove(user_id) if not err else None

    elif user_id in id_dict['global_search_id']:
        with open(message_id + '.jpg', 'rb') as load_img:
            message, saucenao_quota, err = saucenao.img_search(load_img, '999')  # 999: 全域搜尋
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
            id_dict['global_search_id'].remove(user_id) if not err else None

    os.remove(message_id + '.jpg')       # 最後刪除下載至本機的圖片


# 輪播按鈕樣板訊息
def carousel_template_message():
    message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='YOUR_THUMBNAIL_IMAGE_URL',
                    title='動畫搜尋',
                    text='請選擇搜尋方式',
                    actions=[
                        MessageTemplateAction(
                            label='傳送圖片網址',
                            text='網址搜尋'
                        ),
                        MessageTemplateAction(
                            label='傳送圖片檔案',
                            text='圖片搜尋'
                        ),
                        MessageTemplateAction(
                            label='傳送圖片(去除截圖黑邊)',
                            text='圖片搜尋(去黑邊)'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='YOUR_THUMBNAIL_IMAGE_URL',
                    title='圖源搜尋',
                    text='請選擇圖片類型',
                    actions=[
                        MessageTemplateAction(
                            label='漫畫',
                            text='漫畫圖源搜尋'
                        ),
                        MessageTemplateAction(
                            label='插畫',
                            text='插畫圖源搜尋'
                        ),
                        MessageTemplateAction(
                            label='其他',
                            text='全域搜尋'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='YOUR_THUMBNAIL_IMAGE_URL',
                    title='關於',
                    text='About',
                    actions=[
                        MessageTemplateAction(
                            label='Q & A',
                            text='Q & A'
                        ),
                        MessageTemplateAction(
                            label='關於本程式',
                            text='關於本程式'
                        ),
                        MessageTemplateAction(
                            label='剩餘搜尋次數查詢',
                            text='剩餘搜尋次數查詢'
                        )
                    ]
                )
            ]
        )
    )
    return message


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
