import requests
import time
import os
import webbrowser
from datetime import datetime
from bs4 import BeautifulSoup

from config import WEATHER_API_KEY, GNEWS_API_KEY


# ============================================
# CITIES TO TRACK
# ============================================
CITIES = ["Nairobi", "Mombasa"]

# ============================================
# FUNCTION: GET WEATHER FOR A CITY
# ============================================
def get_weather(city):
    """
    Fetch current weather for a specific city
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get("cod") == 200:
            return {
                "success": True,
                "city": city,
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"]
            }
        else:
            return {"success": False, "city": city, "error": data.get("message", "Unknown error")}
    except Exception as e:
        return {"success": False, "city": city, "error": str(e)}


# ============================================
# FUNCTION: GET WEATHER FOR ALL CITIES
# ============================================
def get_all_weather():
    """
    Fetch weather for all cities in CITIES list
    """
    results = []
    for city in CITIES:
        print(f"   Fetching weather for {city}...")
        weather = get_weather(city)
        results.append(weather)
        if weather["success"]:
            print(f"      ✅ {weather['temp']}°C, {weather['description']}")
        else:
            print(f"      ❌ Error: {weather.get('error')}")
        time.sleep(0.5)
    return results


# ============================================
# FUNCTION: GET ENGLISH NEWS (GNews API)
# ============================================
def get_english_news():
    """
    Fetch top headlines from Kenya using GNews API
    """
    url = f"https://gnews.io/api/v4/top-headlines?country=ke&apikey={GNEWS_API_KEY}&lang=en&max=10"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "articles" in data:
            articles = []
            for article in data["articles"]:
                articles.append({
                    "title": article.get("title", "No title"),
                    "description": article.get("description", "No description available"),
                    "url": article.get("url", "#"),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "publishedAt": article.get("publishedAt", "")
                })
            print(f"   ✅ Found {len(articles)} English articles")
            return {"success": True, "articles": articles}
        else:
            error_msg = data.get("errors", ["Unknown error"])[0]
            print(f"   ❌ API Error: {error_msg}")
            return {"success": False, "error": error_msg}
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return {"success": False, "error": str(e)}


# ============================================
# FUNCTION: GET TAIFA LEO NEWS (Kiswahili)
# ============================================
def get_taifa_leo_news():
    """
    Scrape latest news from Taifa Leo (Kiswahili)
    """
    url = "https://taifaleo.nation.co.ke"
    
    try:
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        # Find all links that look like news articles
        for link in soup.find_all('a', href=True):
            title = link.get_text(strip=True)
            href = link['href']
            
            # Filter for likely article links
            if title and len(title) > 20 and href and not href.startswith('#'):
                full_url = url + href if href.startswith('/') else href
                articles.append({
                    "title": title,
                    "url": full_url,
                    "source": "Taifa Leo"
                })
        
        # Remove duplicates by title
        seen = set()
        unique_articles = []
        for article in articles:
            if article["title"] not in seen:
                seen.add(article["title"])
                unique_articles.append(article)
        
        print(f"   ✅ Found {len(unique_articles[:8])} Taifa Leo articles")
        return {"success": True, "articles": unique_articles[:8]}
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"success": False, "error": str(e)}


# ============================================
# FUNCTION: CREATE HTML CONTENT
# ============================================
def create_html(weather_results, english_result, taifa_result):
    """
    Create HTML page with all weather and news data
    """
    
    # Weather HTML for all cities
    weather_html = '<div class="weather-grid">'
    for weather in weather_results:
        if weather["success"]:
            weather_html += f"""
            <div class="weather-card">
                <h2>☁️ {weather['city']}</h2>
                <div class="weather-info">
                    <div class="temp">{weather['temp']}°C</div>
                    <div class="feels-like">Feels like: {weather['feels_like']}°C</div>
                    <div class="description">{weather['description'].capitalize()}</div>
                    <div class="details">💧 Humidity: {weather['humidity']}% | 💨 Wind: {weather['wind_speed']} m/s</div>
                </div>
            </div>
            """
        else:
            weather_html += f"""
            <div class="weather-card error">
                <h2>☁️ {weather['city']}</h2>
                <p>❌ Weather unavailable</p>
                <p class="error-msg">{weather.get('error', 'Unknown error')}</p>
            </div>
            """
    weather_html += '</div>'
    
    # English News HTML (GNews API)
    if english_result["success"] and english_result["articles"]:
        english_items = ""
        for i, article in enumerate(english_result["articles"], 1):
            title = article.get("title", "No title")
            source = article.get("source", "Unknown")
            description = article.get("description", "No description available")
            url = article.get("url", "#")
            
            english_items += f"""
            <div class="news-item">
                <div class="news-number">{i}</div>
                <div class="news-content">
                    <h3>{title}</h3>
                    <div class="news-meta">📍 Source: {source}</div>
                    <p>{description[:200]}{'...' if len(description) > 200 else ''}</p>
                    <a href="{url}" target="_blank">Read full story →</a>
                </div>
            </div>
            """
        
        english_news_html = f"""
        <div class="news-section">
            <h2>📰 Top News in Kenya (English)</h2>
            {english_items}
        </div>
        """
    else:
        english_news_html = f"""
        <div class="news-section error">
            <h2>📰 English News Unavailable</h2>
            <p>Error: {english_result.get('error', 'Unable to fetch news')}</p>
            <p>💡 Tip: Check your GNews API key or try again later.</p>
        </div>
        """
    
    # Taifa Leo News HTML (Kiswahili)
    if taifa_result["success"] and taifa_result["articles"]:
        taifa_items = ""
        for i, article in enumerate(taifa_result["articles"], 1):
            title = article.get("title", "Hakuna kichwa")
            url = article.get("url", "#")
            source = article.get("source", "Taifa Leo")
            
            taifa_items += f"""
            <div class="news-item">
                <div class="news-number">{i}</div>
                <div class="news-content">
                    <h3>{title}</h3>
                    <div class="news-meta">📍 Source: {source}</div>
                    <a href="{url}" target="_blank">Soma habari →</a>
                </div>
            </div>
            """
        
        taifa_news_html = f"""
        <div class="news-section taifa-section">
            <h2>📰 Taifa Leo - Habari za Kiswahili</h2>
            {taifa_items}
        </div>
        """
    else:
        taifa_news_html = f"""
        <div class="news-section error">
            <h2>📰 Taifa Leo - Habari za Kiswahili</h2>
            <p>Error: {taifa_result.get('error', 'Haiwezi kupata habari')}</p>
        </div>
        """
    
    # Full HTML page
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kenya Daily Update - {datetime.now().strftime('%B %d, %Y')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #e94560 0%, #ff6b6b 100%);
            border-radius: 20px;
            margin-bottom: 30px;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .date {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .weather-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .weather-card {{
            background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%);
            border-radius: 20px;
            padding: 25px;
            color: white;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            border: 1px solid rgba(255,255,255,0.1);
            text-align: center;
        }}
        
        .weather-card h2 {{
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        .weather-info {{
            text-align: center;
        }}
        
        .temp {{
            font-size: 4em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .feels-like {{
            font-size: 1.2em;
            opacity: 0.8;
        }}
        
        .description {{
            font-size: 1.5em;
            margin: 10px 0;
            text-transform: capitalize;
        }}
        
        .details {{
            margin-top: 15px;
            font-size: 1em;
            opacity: 0.9;
        }}
        
        .news-section {{
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 25px;
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }}
        
        .taifa-section {{
            background: rgba(46, 125, 50, 0.15);
            border: 1px solid rgba(76, 175, 80, 0.3);
        }}
        
        .news-section h2 {{
            color: #e94560;
            margin-bottom: 25px;
            font-size: 1.8em;
            border-left: 4px solid #e94560;
            padding-left: 15px;
        }}
        
        .taifa-section h2 {{
            color: #4caf50;
            border-left-color: #4caf50;
        }}
        
        .news-item {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            display: flex;
            gap: 15px;
            transition: transform 0.3s ease;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .news-item:hover {{
            transform: translateX(5px);
            background: rgba(255,255,255,0.1);
        }}
        
        .news-number {{
            background: #e94560;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2em;
            flex-shrink: 0;
        }}
        
        .taifa-section .news-number {{
            background: #4caf50;
        }}
        
        .news-content {{
            flex: 1;
        }}
        
        .news-content h3 {{
            color: white;
            margin-bottom: 8px;
            font-size: 1.2em;
        }}
        
        .news-meta {{
            color: #e94560;
            font-size: 0.85em;
            margin-bottom: 10px;
        }}
        
        .news-content p {{
            color: #ccc;
            margin-bottom: 12px;
            line-height: 1.5;
        }}
        
        .news-content a {{
            color: #ff6b6b;
            text-decoration: none;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .news-content a:hover {{
            text-decoration: underline;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #888;
            font-size: 0.85em;
        }}
        
        .error {{
            border: 1px solid #e94560;
        }}
        
        .error-msg {{
            color: #ff6b6b;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        
        @media (max-width: 768px) {{
            .news-item {{
                flex-direction: column;
            }}
            
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .temp {{
                font-size: 2.5em;
            }}
            
            .weather-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌍 Kenya Daily Update</h1>
            <div class="date">{datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}</div>
        </div>
        
        <h2 style="color: white; margin-bottom: 15px;">🌡️ Weather Updates</h2>
        {weather_html}
        
        {english_news_html}
        
        {taifa_news_html}
        
        <div class="footer">
            <p>🤖 Powered by OpenWeatherMap API, GNews API, & Taifa Leo | Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html_content


# ============================================
# FUNCTION: SAVE HTML TO FILE
# ============================================
def save_html_to_file(html_content):
    filename = f"kenya_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content)
    return filename


# ============================================
# FUNCTION: DISPLAY IN BROWSER
# ============================================
def display_in_browser(html_file_path):
    """
    Opens the HTML file in your default browser
    """
    print("\n🌐 Opening in default browser...")
    
    abs_path = os.path.abspath(html_file_path)
    file_url = f"file:///{abs_path.replace(os.sep, '/')}"
    webbrowser.open(file_url)
    
    print(f"✅ Daily update displayed in your browser!")
    print(f"📁 HTML file saved at: {abs_path}")


# ============================================
# MAIN FUNCTION
# ============================================
def main():
    print("\n" + "="*60)
    print("🌍 KENYA DAILY UPDATE BOT")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p')}\n")
    
    # 1. Get weather for all cities
    print("☁️  Fetching weather data...")
    weather_results = get_all_weather()
    
    # 2. Get English news (GNews API)
    print("\n📰 Fetching English news from Kenya...")
    english_result = get_english_news()
    
    # 3. Get Taifa Leo news (Kiswahili)
    print("\n📰 Fetching Taifa Leo news...")
    taifa_result = get_taifa_leo_news()
    
    # 4. Create HTML (now with 3 arguments)
    print("\n🎨 Generating HTML page...")
    html_content = create_html(weather_results, english_result, taifa_result)
    
    # 5. Save HTML to file
    html_file = save_html_to_file(html_content)
    print(f"   ✅ HTML saved to: {html_file}")
    
    # 6. Display in browser
    display_in_browser(html_file)
    
    print("\n" + "="*60)
    print("✅ Bot completed successfully!")
    print("="*60)


# ============================================
# RUN THE BOT
# ============================================
if __name__ == "__main__":
    main()
