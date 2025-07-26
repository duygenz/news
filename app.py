import feedparser
from flask import Flask, jsonify, request
import datetime

app = Flask(__name__)

# Danh sách các RSS feeds bạn muốn lấy tin tức
RSS_FEEDS = {
    "vietstock_chung_khoan_co_phieu": "https://vietstock.vn/830/chung-khoan/co-phieu.rss",
    "cafef_thi_truong_chung_khoan": "https://cafef.vn/thi-truong-chung-khoan.rss",
    "vietstock_y_kien_chuyen_gia": "https://vietstock.vn/145/chung-khoan/y-kien-chuyen-gia.rss",
    "vietstock_hoat_dong_kinh_doanh": "https://vietstock.vn/737/doanh-nghiep/hoat-dong-kinh_doanh.rss",
    "vietstock_dong_duong_thi_truong_chung_khoan": "https://vietstock.vn/1328/dong-duong/thi_truong_chung_khoan.rss",
}

def parse_feed(feed_url):
    """Phân tích cú pháp một RSS feed và trả về danh sách các bài viết."""
    try:
        feed = feedparser.parse(feed_url)
        articles = []
        for entry in feed.entries:
            # Lấy thông tin cơ bản từ mỗi bài viết
            title = getattr(entry, 'title', 'No title')
            link = getattr(entry, 'link', 'No link')
            summary = getattr(entry, 'summary', getattr(entry, 'description', 'No summary'))

            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    # Chuyển đổi thời gian từ cấu trúc thời gian được phân tích cú pháp
                    # sang định dạng ISO 8601 để dễ đọc và xử lý
                    published_date = datetime.datetime(*entry.published_parsed[:6]).isoformat()
                except TypeError:
                    pass # Bỏ qua nếu có lỗi chuyển đổi ngày tháng

            articles.append({
                "title": title,
                "link": link,
                "summary": summary,
                "published_date": published_date,
                "source": feed.feed.title if hasattr(feed.feed, 'title') else 'Unknown Source'
            })
        return articles
    except Exception as e:
        print(f"Error parsing feed {feed_url}: {e}")
        return []

@app.route('/news', methods=['GET'])
def get_news():
    """
    Endpoint API để lấy tin tức từ các RSS feeds.
    
    Có thể lọc theo nguồn bằng cách thêm tham số 'source' vào URL:
    ví dụ: /news?source=cafef_thi_truong_chung_khoan
    """
    source_param = request.args.get('source')
    all_articles = []

    if source_param and source_param in RSS_FEEDS:
        # Nếu có tham số 'source' và nó hợp lệ, chỉ lấy tin từ nguồn đó
        feed_url = RSS_FEEDS[source_param]
        articles = parse_feed(feed_url)
        all_articles.extend(articles)
    elif source_param and source_param not in RSS_FEEDS:
        # Nếu tham số 'source' không hợp lệ
        return jsonify({"error": f"Source '{source_param}' not found. Available sources: {', '.join(RSS_FEEDS.keys())}"}), 400
    else:
        # Nếu không có tham số 'source', lấy tin từ tất cả các feeds
        for source_name, feed_url in RSS_FEEDS.items():
            articles = parse_feed(feed_url)
            all_articles.extend(articles)
    
    # Sắp xếp các bài viết theo ngày xuất bản (mới nhất trước)
    all_articles.sort(key=lambda x: x['published_date'] if x['published_date'] else '', reverse=True)

    return jsonify(all_articles)

@app.route('/')
def home():
    """Trang chủ hiển thị các nguồn RSS có sẵn."""
    return f"""
    <h1>API Tin Tức RSS</h1>
    <p>Sử dụng endpoint <code>/news</code> để lấy tin tức.</p>
    <p>Các nguồn RSS có sẵn:</p>
    <ul>
        {''.join([f'<li>{name}: {url}</li>' for name, url in RSS_FEEDS.items()])}
    </ul>
    <p>Để lọc theo nguồn, thêm tham số <code>?source=tên_nguồn</code> vào URL (ví dụ: <code>/news?source=cafef_thi_truong_chung_khoan</code>).</p>
    """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
