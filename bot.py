import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram import Bot

# بيانات حساب تويتر
TWITTER_USERNAME = "ضع_اسم_مستخدم_تويتر"
TWITTER_PASSWORD = "ضع_كلمة_المرور"
TARGET_ACCOUNT = "اسم_الحساب_الذي_تتابعه"

# بيانات التليجرام
TELEGRAM_BOT_TOKEN = "توكن_بوت_تليجرام"
TELEGRAM_USER_ID = 123456789  # رقم الآيدي الخاص بك

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def send_telegram_message(text):
    try:
        bot.send_message(chat_id=TELEGRAM_USER_ID, text=text)
    except Exception as e:
        print("❌ خطأ في إرسال رسالة تليجرام:", e)

def save_cookies(driver, path):
    with open(path, 'w') as file:
        json.dump(driver.get_cookies(), file)

def load_cookies(driver, path):
    with open(path, 'r') as file:
        cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)

def login_to_twitter(driver):
    driver.get("https://x.com/login")
    wait = WebDriverWait(driver, 20)

    try:
        username_input = wait.until(EC.presence_of_element_located((By.NAME, "text")))
        username_input.send_keys(TWITTER_USERNAME)
        username_input.send_keys(Keys.ENTER)
        time.sleep(3)

        password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_input.send_keys(TWITTER_PASSWORD)
        password_input.send_keys(Keys.ENTER)
        time.sleep(5)

        save_cookies(driver, "cookies.json")
        print("✅ تم تسجيل الدخول وحفظ الكوكيز")
    except Exception as e:
        print("❌ فشل تسجيل الدخول:", e)
        raise

def is_logged_in(driver):
    driver.get("https://x.com/home")
    time.sleep(5)
    return "login" not in driver.current_url.lower()

def get_latest_tweet_url(driver):
    driver.get(f"https://x.com/{TARGET_ACCOUNT}")
    time.sleep(5)
    tweet = driver.find_element(By.XPATH, '//article[@role="article"]')
    link = tweet.find_element(By.XPATH, ".//a[contains(@href, '/status/')]")
    return link.get_attribute("href")

def like_and_retweet(driver):
    try:
        like_button = driver.find_element(By.XPATH, '//div[@data-testid="like"]')
        like_button.click()
        time.sleep(1)
        print("❤️ تم لايك")
    except:
        print("❌ لا يمكن الضغط على لايك (ربما تم لايك سابقًا)")

    try:
        retweet_button = driver.find_element(By.XPATH, '//div[@data-testid="retweet"]')
        retweet_button.click()
        time.sleep(1)
        confirm = driver.find_element(By.XPATH, '//div[@data-testid="retweetConfirm"]')
        confirm.click()
        print("🔁 تم ريتويت")
    except:
        print("❌ لا يمكن الضغط على ريتويت (ربما تم ريتويت سابقًا)")

def save_last_tweet(url):
    with open("last_tweet.txt", "w") as f:
        f.write(url)

def load_last_tweet():
    if os.path.exists("last_tweet.txt"):
        with open("last_tweet.txt", "r") as f:
            return f.read().strip()
    return ""

def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # لو تبي تشوف المتصفح احذف هذا السطر
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        print("▶ البوت بدأ الآن ويعمل بشكل مستمر ...")

        if os.path.exists("cookies.json"):
            driver.get("https://x.com/")
            load_cookies(driver, "cookies.json")
            driver.refresh()
            time.sleep(3)
            if not is_logged_in(driver):
                print("⚠️ الكوكيز غير صالحة، تسجيل الدخول يدوي...")
                login_to_twitter(driver)
        else:
            login_to_twitter(driver)

        last_tweet = load_last_tweet()
        latest_tweet = get_latest_tweet_url(driver)

        if latest_tweet != last_tweet:
            print("🆕 تم العثور على تغريدة جديدة")
            like_and_retweet(driver)
            send_telegram_message(f"🆕 تغريدة جديدة من @{TARGET_ACCOUNT}:\n{latest_tweet}")
            send_telegram_message("✅ تم عمل لايك وريتويت")
            save_last_tweet(latest_tweet)
        else:
            print("⏳ لا توجد تغريدات جديدة")

    except Exception as e:
        print("❌ خطأ:", e)
        send_telegram_message(f"❌ حدث خطأ في البوت:\n{e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    while True:
        main()
        time.sleep(60)
