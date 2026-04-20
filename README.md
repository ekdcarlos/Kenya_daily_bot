# Kenya Daily Update Bot 🇰🇪

A Python bot that fetches live weather data and news headlines for Nairobi and Mombasa, then generates a beautiful HTML dashboard.

## Features

- ☁️ **Weather** - Current temperature, conditions, humidity, and wind speed for Nairobi and Mombasa (OpenWeatherMap API)
- 📰 **English News** - Top headlines from Kenya (GNews API)
- 📰 **Kiswahili News** - Latest news from Taifa Leo (web scraping with BeautifulSoup)
- 🎨 **HTML Dashboard** - Automatically generates a professional, dark-themed webpage
- 🌐 **Auto-open** - Opens the dashboard in your default browser

## Technologies Used

- Python 3
- Requests library (API calls)
- BeautifulSoup (web scraping)
- HTML/CSS (dashboard design)

## Setup Instructions

1. Clone this repository
2. Install dependencies: `pip install requests beautifulsoup4`
3. Get API keys:
   - [OpenWeatherMap](https://openweathermap.org/api) (free)
   - [GNews API](https://gnews.io/) (free)
4. Add your API keys to the script
5. Run: `python kenya_daily_bot.py`

## Sample Output

![Kenya Daily Update Bot Screenshot](Screenshot 2026-04-20 102539.png)

## Author

[Emmanuel Kalongo Dena] - IT Student, COSEKE Attachment

## License

MIT
