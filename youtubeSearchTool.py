import speech_recognition as sr
import webbrowser
from urllib.parse import quote
import vosk
import queue
import sounddevice as sd
import sys
import json

# 載入 Vosk 語音模型
model = vosk.Model("vosk-model-small-cn-0.22")

# 創建一個隊列對象
audio_queue = queue.Queue()

# 音频流的回调函数
def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(bytes(indata))

# 函数：语音识别并返回文本
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("请说话...")
        try:
            # 录音并进行语音识别
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio, language="zh-TW")  # zh-TW 是繁体中文，en-US 是美式英文
            print(f"识别到的文本：{text}")
            return text
        except sr.UnknownValueError:
            print("抱歉，无法识别您的语音。")
        except sr.RequestError:
            print("无法连接到语音识别服务。")
    return None

# 函数：根据搜索关键字在 YouTube 上搜索
def search_youtube(query):
    if query:
        encoded_query = quote(query)
        youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        webbrowser.open(youtube_url)
        print(f"正在 YouTube 上搜索：{query}")

# 主程序
if __name__ == "__main__":
    # 开始录音
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):
        print("正在监听... 说 '關鍵字' 以启动搜索")
        rec = vosk.KaldiRecognizer(model, 16000)

        while True:
            data = audio_queue.get()  # 使用 audio_queue 代替 q
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())  # 解析 JSON 結果
                if "text" in result and "开始 搜索" in result["text"]:
                    print("检测到热词！开始录音和搜索...")
                    # 在这里调用你的语音识别和 YouTube 搜索函数
                    query = recognize_speech()
                    search_youtube(query)
