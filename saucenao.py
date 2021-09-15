import requests
from config import api_secret

saucenao_url = 'https://saucenao.com/search.php'


# 使用圖片搜尋
def img_search(img, index):
    params = {
        'db': index,                                            # 想要查詢的圖片類型
        'numres': '1',                                          # 想取得的搜尋結果數
        'testmode': '1',                                        # 使每個匹配的索引最多輸出 1 進行測試
        'output_type': '2',                                     # 網站回傳的資料格式，2 為 json 格式
        'api_key': api_secret                                   # 註冊網站帳號後取得的 API 密鑰
    }
    # 開始搜尋並取得網站回傳結果
    response = requests.post(saucenao_url, params=params, files={'file': img}).json()
    remaining_quota = response['header']['long_remaining']      # 當日剩餘的搜尋次數
    if response['header']['status']:                            # 如果 status 值不為 0 則代表發生錯誤
        return '讀取失敗，請稍後再傳送一次！', remaining_quota, True

    similarity = str(round(float(response['results'][0]['header']['similarity']))) + ' %'
    data = response['results'][0]['data']
    res_index = response['header']['index']
    # 如果不是使用全域搜尋
    if index != '999':
        # 插畫搜尋
        if '5' in res_index:
            title = data['title']
            pixiv_id = data['pixiv_id']
            artist = data['member_name']
            url = data['ext_urls'][0]
            message = ('插畫標題：' + title + '\n\n' +
                       '作者：' + artist + '\n\n' +
                       'PIXIV ID：' + str(pixiv_id) + '\n\n' +
                       '相似度：' + similarity + '\n\n' +
                       '網址：' + url)
            return message, remaining_quota, False

        # 漫畫搜尋
        elif '37' in res_index:
            title = data['source']
            part = data['part'].split('Chapter')[1]
            artist = data['artist']
            message = ('漫畫名稱：' + title + '\n\n' +
                       '集數：第' + part + ' 集\n\n' +
                       '作者：' + artist + '\n\n' +
                       '相似度：' + similarity)
            return message, remaining_quota, False

    # 使用全域搜尋
    else:
        # 查詢各大相關網頁的資料，每個網頁回傳的格式都略有不同，故需整合內容
        title, artist, url, message = '', '', '', ''
        if 'jp_name' in data and data['jp_name'] != '':
            title = data['jp_name']
        elif 'source' in data and data['source'] != '':
            title = data['source']
        elif 'title' in data and data['title'] != '':
            title = data['title']

        if 'creator' in data and data['creator'] != '':
            if isinstance(data['creator'], str):
                artist = data['creator']
            else:
                artist = ' , '.join(data['creator'])

        if 'ext_urls' in data and data['ext_urls'][0] != '':
            url = data['ext_urls'][0]

        if title:
            message += '標題：' + title + '\n\n'
        if artist:
            message += '作者：' + artist + '\n\n'
        if url:
            message += '網址：' + url + '\n\n'

        return (message + '相似度：' + similarity), remaining_quota, False
