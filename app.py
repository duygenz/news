# app.py
from flask import Flask, jsonify
import feedparser
from bs4 import BeautifulSoup
import re
from datetime import datetime

app = Flask(__name__)

# Danh sách các nguồn RSS
RSS_FEEDS = [
    "https://vietstock.vn/830/chung-khoan/co-phieu.rss",
    "https://cafef.vn/thi-truong-chung-khoan.rss",
    "https://vietstock.vn/145/chung-khoan/y-kien-chuyen-gia.rss",
    "https://vietstock.vn/737/doanh-nghiep/hoat-dong-kinh-doanh.rss",
    "https://vietstock.vn/1328/dong-duong/thi-truong-chung-khoan.rss"
]

def clean_html(raw_html):
    """Loại bỏ thẻ HTML và làm sạch nội dung"""
    if raw_html is None:
        return ""
    clean_text = re.sub('<.*?>', '', raw_html)
    return clean_text.strip()

def parse_feed(feed_url):
    """Phân tích RSS feed và trích xuất thông tin cần thiết"""
    parsed = feedparser.parse(feed_url)
    articles = []
    
    for entry in parsed.entries:
        # Xử lý ngày đăng bài
        published_time = entry.get('published', '')
        if published_time:
            try:
                published_dt = datetime.strptime(published_time, '%a, %d %b %Y %H:%M:%S %z')
                published_time = published_dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                published_time = ""
        
        # Xử lý nội dung
        description = clean_html(entry.get('description', ''))
        
        articles.append({
            'title': entry.get('title', ''),
            'link': entry.get('link', ''),
            'published': published_time,
            'source': feed_url,
            'description': description,
            'thumbnail': entry.get('media_thumbnail', [{}])[0].get('url', '') if 'media_thumbnail' in entry else ''
        })
    
    return articles

@app.route('/news', methods=['GET'])
def get_news():
    """Endpoint trả về tin tức tổng hợp"""
    all_articles = []
    
    for feed_url in RSS_FEEDS:
        try:
            articles = parse_feed(feed_url)
            all_articles.extend(articles)
        except Exception as e:
            print(f"Lỗi khi xử lý {feed_url}: {str(e)}")
    
    # Sắp xếp theo thời gian đăng bài (mới nhất đầu tiên)
    all_articles.sort(key=lambda x: x['published'], reverse=True)
    
    return jsonify({
        'status': 'success',
        'count': len(all_articles),
        'articles': all_articles
    })

if __name__ == '__main__':
    app.run(debug=True)