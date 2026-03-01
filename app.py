import streamlit as st
import feedparser
import requests
import datetime
import base64
from urllib.parse import quote

# ページ設定
st.set_page_config(page_title="News & Weather", page_icon="🌤️", layout="wide")

# カスタムCSSの適用（モダンでリッチなデザイン）
def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;700;800&display=swap');
    
    /* 全体の背景とポップなフォント設定 */
    .stApp {
        background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%);
        color: #333333;
        font-family: 'M PLUS Rounded 1c', 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
    }

    /* ヘッダーの非表示化 */
    header {visibility: hidden;}
    
    /* ガラスモーフィズム風カードのデザイン（シャドウを強調） */
    .glass-card {
        background: rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.7);
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        color: #333333;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5);
    }

    /* 各種テキストデザイン */
    .app-title {
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 30px;
        color: #ffffff;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
        padding: 50px 20px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .section-title {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 15px;
        border-bottom: 2px solid rgba(0,0,0,0.1);
        padding-bottom: 5px;
        display: inline-block;
        color: #444;
    }

    /* ニュースのタイトルとスニペット */
    .news-title {
        font-size: 1.25rem;
        font-weight: bold;
        color: #1976d2 !important;
        text-decoration: none;
    }
    .news-title:hover {
        color: #0d47a1 !important;
        text-decoration: underline;
    }
    .news-date {
        font-size: 0.85rem;
        color: #78909c;
        margin-bottom: 8px;
    }
    .news-summary {
        font-size: 0.95rem;
        line-height: 1.5;
        color: #455a64;
    }

    /* 天気情報のスタイル */
    .weather-temp {
        font-size: 3rem;
        font-weight: bold;
        color: #f57f17;
        line-height: 1;
    }
    .weather-desc {
        font-size: 1.5rem;
        margin-top: 10px;
        color: #555;
    }
    .weather-detail {
        font-size: 1rem;
        color: #607d8b;
        margin-top: 5px;
    }

    /* スクロールバーのカスタマイズ */

    </style>
    """, unsafe_allow_html=True)

# ニュースの取得関数
@st.cache_data(ttl=900)
def fetch_news(query=""):
    if query:
        encoded_query = quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
    else:
        rss_url = "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja"
        
    feed = feedparser.parse(rss_url)
    return feed.entries[:10]  # 最新10件を取得

# 天気の取得関数 (Open-Meteo API)
@st.cache_data(ttl=1800)
def fetch_weather_forecast(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=Asia%2FTokyo&forecast_days=2"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None

# 天気コード（WMO）を日本語とアイコンに変換
def get_weather_info(weathercode):
    weather_mapping = {
        0: ("快晴", "☀️"),
        1: ("晴れ", "🌤️"),
        2: ("一部曇り", "⛅"),
        3: ("曇り", "☁️"),
        45: ("霧", "🌫️"),
        48: ("霧氷", "🌫️"),
        51: ("弱い霧雨", "🌧️"),
        53: ("霧雨", "🌧️"),
        55: ("強い霧雨", "🌧️"),
        61: ("弱い雨", "☔"),
        63: ("雨", "☔"),
        65: ("強い雨", "☔"),
        71: ("弱い雪", "❄️"),
        73: ("雪", "❄️"),
        75: ("強い雪", "❄️"),
        95: ("雷雨", "⛈️"),
        99: ("激しい雷雨", "⛈️🌩️")
    }
    return weather_mapping.get(weathercode, ("不明", "❓"))

def main():
    local_css()
    
    # バナー画像をBase64形式で読み込み、タイトルの背景に設定する
    try:
        with open("banner.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            bg_css = f"""
            <style>
            .app-title {{
                background-image: url("data:image/png;base64,{encoded_string}");
                background-size: cover;
                background-position: center;
            }}
            </style>
            """
            st.markdown(bg_css, unsafe_allow_html=True)
    except FileNotFoundError:
        pass
    
    st.markdown('<div class="app-title">🌍 Daily Nexus : News & Weather</div>', unsafe_allow_html=True)

    # 常時表示される設定・検索エリア（メイン画面の上部）
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    setting_col1, setting_col2 = st.columns([1, 2])
    
    with setting_col1:
        st.subheader("📍 都市選択")
        location_options = {
            "東京": (35.6895, 139.6917),
            "大阪": (34.6937, 135.5023),
            "名古屋": (35.1815, 136.9066),
            "福岡": (33.5902, 130.4017),
            "札幌": (43.0618, 141.3545)
        }
        selected_loc = st.selectbox("都市を選択", list(location_options.keys()))
        lat, lon = location_options[selected_loc]
        
    with setting_col2:
        st.subheader("🔍 ニュース検索")
        search_query = st.text_input("検索キーワードを入力（例：AI, スポーツ など）", value="")
        
    st.markdown('</div>', unsafe_allow_html=True)

    # メインレイアウト（天気とニュースをカラム分け）
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="section-title">🌤️ 今日の天気</div>', unsafe_allow_html=True)
        weather_data = fetch_weather_forecast(lat, lon)
        
        if weather_data:
            current = weather_data.get('current_weather', {})
            temp = current.get('temperature')
            wind_speed = current.get('windspeed')
            code = current.get('weathercode')
            desc, icon = get_weather_info(code)
            
            st.markdown(f"""
            <div class="glass-card">
                <h3>{selected_loc}</h3>
                <div class="weather-temp">{temp} °C {icon}</div>
                <div class="weather-desc">{desc}</div>
                <div class="weather-detail">🍃 風速: {wind_speed} km/h</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 明日の天気の表示
            daily = weather_data.get('daily', {})
            if daily:
                t_code = daily.get('weathercode', [])[1]
                t_max = daily.get('temperature_2m_max', [])[1]
                t_min = daily.get('temperature_2m_min', [])[1]
                t_desc, t_icon = get_weather_info(t_code)
                
                st.markdown('<div class="section-title">📅 明日の天気</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="glass-card">
                    <div style="font-size: 1.4rem; margin-bottom: 5px;">明日は... {t_desc} {t_icon}</div>
                    <div style="color: #e53935; font-weight: bold; display: inline-block; font-size: 1.1rem; margin-right: 15px;">🔼 最高: {t_max}°C</div>
                    <div style="color: #1e88e5; font-weight: bold; display: inline-block; font-size: 1.1rem;">🔽 最低: {t_min}°C</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 花粉情報の表示（季節に応じてメッセージを変えるシミュレーション仕様）
                now = datetime.datetime.now()
                month = now.month
                if 2 <= month <= 4:
                    pollen_level = "🌲 スギ・ヒノキ: 非常に多い 😷"
                elif 5 <= month <= 6:
                    pollen_level = "🌱 イネ科花粉: やや多い 🤧"
                elif 8 <= month <= 10:
                    pollen_level = "🌿 ブタクサ花粉: 多い 🤧"
                else:
                    pollen_level = "✨ 花粉: 少ない 😊"
                    
                st.markdown('<div class="section-title">😷 花粉情報</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="glass-card" style="border: 2px dashed rgba(255,255,255,0.8); background: rgba(255, 255, 255, 0.6);">
                    <div style="font-size: 1.3rem; font-weight: bold; color: #ef6c00;">{pollen_level}</div>
                    <div style="font-size: 0.8rem; color: #78909c; margin-top: 5px;">※AIによる季節予測データです</div>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.error("天気データの取得に失敗しました。")

    with col2:
        st.markdown('<div class="section-title">📰 最新ニュース</div>', unsafe_allow_html=True)
        
        with st.spinner('ニュースを取得中...'):
            articles = fetch_news(search_query)
            
            if articles:
                for article in articles:
                    # 日付のフォーマット処理
                    published = getattr(article, 'published', '')
                    
                    st.markdown(f"""
                    <div class="glass-card">
                        <a href="{article.link}" target="_blank" class="news-title">{article.title}</a>
                        <div class="news-date">{published}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("ニュースが見つかりませんでした。")

if __name__ == "__main__":
    main()
