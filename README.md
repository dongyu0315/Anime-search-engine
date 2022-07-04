# Anime search engine

本機器人使用 [Trace.moe](https://trace.moe) 與 [SauceNAO](https://saucenao.com) 提供的 API 作程式的編寫，並在 HeorKu 上運行。

GitHub 上已經有其他關於[如何搭建 LINE Bot 機器人](https://github.com/yaoandy107/line-bot-tutorial)的詳細中文教學，

本文就不再對其多做說明。

LINE Bot 帳號連結：[Source](https://page.line.me/475fahrf)

<img src="https://i.imgur.com/GGpmKI9.jpg" width="240" height="443"/><br/>

## 目錄

[如果你也想要搭建一個與本文相同的 LINE Bot](#如果你也想要搭建一個與本文相同的-line-bot你需要)

[這是什麼？ 它可以幹嘛？](#這是什麼它可以幹嘛)

[參考資料](#參考資料)


## 如果你也想要搭建一個與本文相同的 LINE Bot，你需要:

- 用你 LINE 的帳號註冊 [LINE Developers](https://developers.line.biz/console)

- 註冊 [Heroku](https://id.heroku.com/login) 帳號  

- 註冊 [SauceNAO](https://saucenao.com/user.php) 並取得 API Key

- 註冊 [imgur](https://imgur.com) 的帳號以存放要顯示在按鈕上面的縮圖  

**小技巧**

　　Heroku 免費方案每 30 分鐘沒有活動就會進入休眠，
  
　　而在休眠狀態傳送訊息會有大概 20 秒的延遲，
 
　　且免費方案一個月只有 550 小時的活動時間，
  
　　可以在驗證信用卡使每月可活動時間增加到 1000 小時過後，
  
　　再透過`threading` 建立子執行緒並每 25 分鐘使用 `requests.get()` 連線到在 Heroku 上的域名避免進入休眠。
  
　　詳細請見 [main.py](https://github.com/dongyu0315/Trace.moe_and_SauceNAO_for_LINE/blob/main/main.py#L25)
    
## 這是什麼？它可以幹嘛？

### [Source](https://page.line.me/475fahrf) 提供了以下幾種方法為你的圖片搜尋來源：

- **透過圖片搜尋動畫 （支援 GIF 檔）**

<img src="https://i.imgur.com/hcE3MCU.gif" width="240" height="269"/><br/><br/> 


- **透過圖片搜尋漫畫名稱與集數** 

<img src="https://i.imgur.com/ajmnCf0.png" width="240" height="302"/><br/><br/> 

- **透過圖片搜尋畫師名稱、PIXIV ID 與連結** 

<img src="https://i.imgur.com/w2WwgZy.png" width="240" height="444"/><br/><br/> 

- **全域搜尋**

  不去對要搜尋的類別多作限制，從各大網站的資料中取得搜尋結果
  

## 參考資料

- [Trace.moe API](https://soruly.github.io/trace.moe-api/#/docs)

- [SauceNAO API](https://saucenao.com/user.php?page=search-api)

- [LINE Bot Heroku Wakeup](https://github.com/maso0310/linebot_heroku_wakeup)
 
