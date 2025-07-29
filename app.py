import feedparser
from flask import Flask, jsonify
from flask_cors import CORS

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
# Kích hoạt CORS cho tất cả các domain trên tất cả các route
CORS(app)

# Danh sách các nguồn RSS
RSS_FEEDS = [
    'https://cafef.vn/thi-truong-chung-khoan.rss',
    'https://vneconomy.vn/chung-khoan.rss',
    'https://vneconomy.vn/tai-chinh.rss',
    'https://vneconomy.vn/thi-truong.rss',
    'https://vneconomy.vn/nhip-cau-doanh-nghiep.rss',
    'https://vneconomy.vn/tin-moi.rss',
    'https://vietstock.vn/830/chung-khoan/co-phieu.rss',
    'https://vietstock.vn/145/chung-khoan/y-kien-chuyen-gia.rss',
    'https://cafebiz.vn/rss/cau-chuyen-kinh-doanh.rss'
]

@app.route('/news', methods=['GET'])
def get_news():
    """
    API endpoint để lấy tin tức từ tất cả các nguồn RSS.
    """
    all_news = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                news_item = {
                    'title': entry.get('title', 'N/A'),
                    'link': entry.get('link', 'N/A'),
                    'published': entry.get('published', 'N/A'),
                    'summary': entry.get('summary', 'N/A'),
                    'source': feed.feed.get('title', 'N/A')
                }
                all_news.append(news_item)
        except Exception as e:
            # Ghi lại lỗi nếu có vấn đề với một nguồn RSS cụ thể
            print(f"Error fetching feed from {feed_url}: {e}")

    # Sắp xếp tất cả các tin tức theo thời gian công bố giảm dần (nếu có)
    # Lưu ý: Định dạng ngày tháng có thể khác nhau giữa các nguồn RSS
    try:
        all_news.sort(key=lambda x: x['published'], reverse=True)
    except Exception:
        # Bỏ qua lỗi sắp xếp nếu định dạng ngày tháng không đồng nhất
        pass

    return jsonify(all_news)

@app.route('/')
def home():
    """
    Trang chủ đơn giản để kiểm tra API có hoạt động không.
    """
    return "News API is running! Use the /news endpoint to fetch articles."

if __name__ == '__main__':
    # Chạy ứng dụng ở chế độ debug (chỉ dành cho phát triển cục bộ)
    app.run(debug=True)
