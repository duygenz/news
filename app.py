import feedparser
from flask import Flask, jsonify
from flask_cors import CORS

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
# Kích hoạt CORS để cho phép truy cập từ các domain khác
CORS(app)

# Danh sách các nguồn cấp RSS
RSS_FEEDS = [
    'https://vietstock.vn/830/chung-khoan/co-phieu.rss',
    'https://cafef.vn/thi-truong-chung-khoan.rss',
    'https://vietstock.vn/145/chung-khoan/y-kien-chuyen-gia.rss',
    'https://vietstock.vn/737/doanh-nghiep/hoat-dong-kinh-doanh.rss',
    'https://vietstock.vn/1328/dong-duong/thi-truong-chung-khoan.rss'
]

@app.route('/news', methods=['GET'])
def get_news():
    """
    Endpoint lấy tin tức từ tất cả các nguồn RSS,
    sắp xếp theo ngày xuất bản và trả về dưới dạng JSON.
    """
    all_news = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            all_news.append({
                'title': entry.title,
                'link': entry.link,
                'published': entry.get('published', 'N/A'), # Lấy ngày xuất bản, nếu không có thì trả về N/A
                'summary': entry.get('summary', ''), # Lấy tóm tắt
                'source': feed.feed.title # Lấy tên của nguồn tin
            })

    # Sắp xếp tin tức theo ngày xuất bản (mới nhất trước)
    # Lưu ý: Điều này yêu cầu định dạng ngày tháng trong RSS phải nhất quán
    try:
        all_news.sort(key=lambda x: feedparser.parse(x['published']).tm_year, reverse=True)
    except:
        # Bỏ qua lỗi sắp xếp nếu định dạng ngày tháng không đồng nhất
        pass

    return jsonify(all_news)

@app.route('/')
def home():
    """Endpoint chính để kiểm tra API có hoạt động không."""
    return "API tin tức chứng khoán đang hoạt động! Sử dụng endpoint /news để lấy dữ liệu."

if __name__ == '__main__':
    # Chạy ứng dụng trên cổng 5000 khi chạy local
    app.run(host='0.0.0.0', port=5000)
