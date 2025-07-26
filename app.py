from flask import Flask, jsonify, render_template_string
import feedparser
import requests
from datetime import datetime
import pytz
import re
from urllib.parse import urljoin
import os

app = Flask(**name**)

# RSS feeds

RSS_FEEDS = {
‘vietstock_stocks’: ‘https://vietstock.vn/830/chung-khoan/co-phieu.rss’,
‘cafef_market’: ‘https://cafef.vn/thi-truong-chung-khoan.rss’,
‘vietstock_expert’: ‘https://vietstock.vn/145/chung-khoan/y-kien-chuyen-gia.rss’,
‘vietstock_business’: ‘https://vietstock.vn/737/doanh-nghiep/hoat-dong-kinh-doanh.rss’,
‘vietstock_eastasian’: ‘https://vietstock.vn/1328/dong-duong/thi-truong-chung-khoan.rss’
}

def clean_html(text):
“”“Remove HTML tags and clean text”””
if not text:
return “”
# Remove HTML tags
clean = re.compile(’<.*?>’)
text = re.sub(clean, ‘’, text)
# Remove extra whitespace
text = ’ ’.join(text.split())
return text

def format_date(date_string):
“”“Format date for Vietnamese timezone”””
try:
if hasattr(date_string, ‘tm_year’):
dt = datetime(*date_string[:6])
else:
dt = datetime.strptime(date_string, ‘%a, %d %b %Y %H:%M:%S %z’)

```
    # Convert to Vietnam timezone
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    dt = dt.astimezone(vn_tz)
    
    return dt.strftime('%d/%m/%Y %H:%M')
except:
    return datetime.now().strftime('%d/%m/%Y %H:%M')
```

def fetch_rss_feed(url, source_name):
“”“Fetch and parse RSS feed”””
try:
headers = {
‘User-Agent’: ‘Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36’
}
response = requests.get(url, headers=headers, timeout=10)
feed = feedparser.parse(response.content)

```
    articles = []
    for entry in feed.entries[:10]:  # Limit to 10 articles per feed
        article = {
            'title': clean_html(entry.get('title', '')),
            'description': clean_html(entry.get('description', ''))[:200] + '...',
            'link': entry.get('link', ''),
            'published': format_date(entry.get('published_parsed', entry.get('published', ''))),
            'source': source_name
        }
        articles.append(article)
    
    return articles
except Exception as e:
    print(f"Error fetching {url}: {str(e)}")
    return []
```

@app.route(’/’)
def home():
“”“Mobile-friendly homepage”””
html_template = “””
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tin Tức Chứng Khoán Việt Nam</title>
<style>
* {
margin: 0;
padding: 0;
box-sizing: border-box;
}

```
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 16px;
        }
        
        .api-section {
            padding: 30px 20px;
        }
        
        .api-item {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #4ECDC4;
        }
        
        .api-item h3 {
            color: #333;
            margin-bottom: 10px;
            font-size: 18px;
        }
        
        .api-item p {
            color: #666;
            margin-bottom: 15px;
            line-height: 1.6;
        }
        
        .api-link {
            display: inline-block;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 500;
            transition: transform 0.3s ease;
        }
        
        .api-link:hover {
            transform: translateY(-2px);
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #eee;
        }
        
        @media (max-width: 600px) {
            .container {
                margin: 10px;
                border-radius: 10px;
            }
            
            .header {
                padding: 20px 15px;
            }
            
            .header h1 {
                font-size: 20px;
            }
            
            .api-section {
                padding: 20px 15px;
            }
            
            .api-item {
                padding: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 API Tin Tức Chứng Khoán</h1>
            <p>Cập nhật tin tức từ các nguồn uy tín</p>
        </div>
        
        <div class="api-section">
            <div class="api-item">
                <h3>🔥 Tất Cả Tin Tức</h3>
                <p>Lấy tất cả tin tức mới nhất từ tất cả các nguồn</p>
                <a href="/api/news" class="api-link">Xem JSON</a>
                <a href="/news" class="api-link">Xem Web</a>
            </div>
            
            <div class="api-item">
                <h3>📊 Tin Cổ Phiếu - VietStock</h3>
                <p>Tin tức về cổ phiếu từ VietStock</p>
                <a href="/api/news/vietstock_stocks" class="api-link">Xem JSON</a>
            </div>
            
            <div class="api-item">
                <h3>💼 Thị Trường - CafeF</h3>
                <p>Tin tức thị trường chứng khoán từ CafeF</p>
                <a href="/api/news/cafef_market" class="api-link">Xem JSON</a>
            </div>
            
            <div class="api-item">
                <h3>🎯 Ý Kiến Chuyên Gia</h3>
                <p>Phân tích và dự báo từ các chuyên gia</p>
                <a href="/api/news/vietstock_expert" class="api-link">Xem JSON</a>
            </div>
            
            <div class="api-item">
                <h3>🏢 Hoạt Động Doanh Nghiệp</h3>
                <p>Tin tức về hoạt động kinh doanh các công ty</p>
                <a href="/api/news/vietstock_business" class="api-link">Xem JSON</a>
            </div>
            
            <div class="api-item">
                <h3>🌏 Thị Trường Đông Dương</h3>
                <p>Tin tức thị trường chứng khoán khu vực</p>
                <a href="/api/news/vietstock_eastasian" class="api-link">Xem JSON</a>
            </div>
        </div>
        
        <div class="footer">
            <p>📱 Tối ưu cho mobile • 🚀 Deploy trên Render</p>
        </div>
    </div>
</body>
</html>
"""
return html_template
```

@app.route(’/api/news’)
def get_all_news():
“”“Get all news from all RSS feeds”””
all_news = []

```
for feed_key, feed_url in RSS_FEEDS.items():
    source_name = {
        'vietstock_stocks': 'VietStock - Cổ Phiếu',
        'cafef_market': 'CafeF - Thị Trường',
        'vietstock_expert': 'VietStock - Chuyên Gia',
        'vietstock_business': 'VietStock - Doanh Nghiệp',
        'vietstock_eastasian': 'VietStock - Đông Dương'
    }.get(feed_key, feed_key)
    
    articles = fetch_rss_feed(feed_url, source_name)
    all_news.extend(articles)

# Sort by published date (newest first)
all_news.sort(key=lambda x: x['published'], reverse=True)

return jsonify({
    'status': 'success',
    'total_articles': len(all_news),
    'last_updated': datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%d/%m/%Y %H:%M'),
    'data': all_news[:50]  # Return top 50 articles
})
```

@app.route(’/api/news/<feed_name>’)
def get_specific_news(feed_name):
“”“Get news from specific RSS feed”””
if feed_name not in RSS_FEEDS:
return jsonify({‘error’: ‘Feed not found’}), 404

```
source_name = {
    'vietstock_stocks': 'VietStock - Cổ Phiếu',
    'cafef_market': 'CafeF - Thị Trường',
    'vietstock_expert': 'VietStock - Chuyên Gia',
    'vietstock_business': 'VietStock - Doanh Nghiệp',
    'vietstock_eastasian': 'VietStock - Đông Dương'
}.get(feed_name, feed_name)

articles = fetch_rss_feed(RSS_FEEDS[feed_name], source_name)

return jsonify({
    'status': 'success',
    'source': source_name,
    'total_articles': len(articles),
    'last_updated': datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%d/%m/%Y %H:%M'),
    'data': articles
})
```

@app.route(’/news’)
def news_web_view():
“”“Mobile-friendly news web view”””
all_news = []

```
for feed_key, feed_url in RSS_FEEDS.items():
    source_name = {
        'vietstock_stocks': 'VietStock - Cổ Phiếu',
        'cafef_market': 'CafeF - Thị Trường',
        'vietstock_expert': 'VietStock - Chuyên Gia',
        'vietstock_business': 'VietStock - Doanh Nghiệp',
        'vietstock_eastasian': 'VietStock - Đông Dương'
    }.get(feed_key, feed_key)
    
    articles = fetch_rss_feed(feed_url, source_name)
    all_news.extend(articles)

# Sort by published date (newest first)
all_news.sort(key=lambda x: x['published'], reverse=True)

html_template = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tin Tức Chứng Khoán</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            line-height: 1.6;
        }
        
        .header {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .news-item {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .news-item:hover {
            transform: translateY(-2px);
        }
        
        .news-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
            text-decoration: none;
        }
        
        .news-title:hover {
            color: #667eea;
        }
        
        .news-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-size: 12px;
            color: #666;
        }
        
        .news-source {
            background: #4ECDC4;
            color: white;
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 11px;
        }
        
        .news-description {
            color: #555;
            font-size: 14px;
            line-height: 1.6;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 10px;
            }
            
            .news-item {
                padding: 15px;
                margin-bottom: 15px;
            }
            
            .news-meta {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .news-source {
                margin-top: 5px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📈 Tin Tức Chứng Khoán</h1>
        <p>Cập nhật: {{ last_updated }}</p>
    </div>
    
    <div class="container">
        {% for article in articles %}
        <div class="news-item">
            <div class="news-meta">
                <span class="news-source">{{ article.source }}</span>
                <span>{{ article.published }}</span>
            </div>
            <a href="{{ article.link }}" target="_blank" class="news-title">
                {{ article.title }}
            </a>
            <div class="news-description">
                {{ article.description }}
            </div>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

from jinja2 import Template
template = Template(html_template)
return template.render(
    articles=all_news[:30],
    last_updated=datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%d/%m/%Y %H:%M')
)
```

@app.route(’/health’)
def health_check():
“”“Health check endpoint for monitoring”””
return jsonify({
‘status’: ‘healthy’,
‘timestamp’: datetime.now(pytz.timezone(‘Asia/Ho_Chi_Minh’)).isoformat(),
‘feeds_count’: len(RSS_FEEDS)
})

if **name** == ‘**main**’:
port = int(os.environ.get(‘PORT’, 5000))
app.run(host=‘0.0.0.0’, port=port, debug=False)
