import json
import requests
import urllib.parse

error_message = '讀取失敗，請稍後再傳送一次！'
trace_moe_url = 'https://api.trace.moe/search?anilistInfo'


# 查詢剩餘搜尋次數
def remaining_quota():
    response = requests.get('https://api.trace.moe/me').json()
    quota = '動畫搜尋：\n本月剩餘 ' + str(response['quota'] - response['quotaUsed']) + ' 次搜尋次數\n\n'
    return quota


# 使用圖片網址搜尋
def url_search(img_url):
    response = requests.get(trace_moe_url + '&url={}'.format(urllib.parse.quote_plus(img_url))).json()
    return (anime_data(response), False) if not response['error'] else (error_message, True)


# 使用圖片搜尋
def img_search(img, cut):
    if cut:
        response = requests.post(trace_moe_url + '&cutBorders', files={'image': img}).json()

    else:
        response = requests.post(trace_moe_url, files={'image': img}).json()

    return (anime_data(response), False) if not response['error'] else (error_message, True)


# 將網站回傳的資料整理並組成文字訊息
def anime_data(data):
    chinese_title = None
    japanese_title = data['result'][0]['anilist']['title']['native']
    anilist_id = int(data['result'][0]['anilist']['id'])
    # 透過網站回傳的 Anilist ID 查詢檔案中是否有相應的中文標題
    with open('anilist_chinese.json', encoding='utf-8') as file:
        file = json.load(file)
        if chinese_title is None:
            for number in range(len(file)):
                for value in file[number].values():
                    if value == anilist_id:
                        chinese_title = file[number]['title']

    anime_name = chinese_title if chinese_title is not None else japanese_title
    episode = '第 ' + str(data['result'][0]['episode']) + ' 集'
    minute = str(round(data['result'][0]['from'] / 60))
    second = str(round(data['result'][0]['from'] % 60))
    time = minute + ' 分 ' + second + ' 秒'
    similarity = str(round(data['result'][0]['similarity'] * 100)) + ' %'
    message = ('動畫名稱：' + anime_name + '\n\n' +
               '集數：' + episode + '\n\n' +
               '時間：' + time + '\n\n' +
               '相似度：' + similarity)
    return message
