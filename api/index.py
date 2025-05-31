from flask import Flask, render_template, jsonify, send_from_directory
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import time
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
import os

# 現在のファイルのディレクトリから一つ上のディレクトリ（プロジェクトルート）を取得
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
           template_folder=os.path.join(BASE_DIR, 'templates'),
           static_folder=os.path.join(BASE_DIR, 'static'))

class NewsAggregator:
    def __init__(self):
        self.news_sources = {
            'GIGAZINE': {
                'url': 'https://gigazine.net',
                'rss': 'https://gigazine.net/news/rss_2.0/',
                'selector': '.post-title a'
            },
            'ITmedia NEWS': {
                'url': 'https://www.itmedia.co.jp/news/',
                'rss': 'https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml',
                'selector': '.headline a'
            },
            'Gizmodo Japan': {
                'url': 'https://www.gizmodo.jp',
                'rss': 'https://www.gizmodo.jp/index.xml',
                'selector': '.p-post-title a'
            },
            'MIT Technology Review Japan': {
                'url': 'https://www.technologyreview.jp',
                'rss': 'https://www.technologyreview.jp/rss/',
                'selector': '.entry-title a'
            }
        }
    
    def parse_rss_date(self, date_string):
        """RSS日付文字列を解析"""
        try:
            # 一般的なRSS日付形式を試行
            formats = [
                '%a, %d %b %Y %H:%M:%S %z',
                '%a, %d %b %Y %H:%M:%S %Z',
                '%Y-%m-%dT%H:%M:%S%z',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_string.strip(), fmt).date()
                except ValueError:
                    continue
            
            # 日付解析に失敗した場合は今日の日付を返す
            return datetime.now().date()
        except:
            return datetime.now().date()
    
    def get_news_from_rss(self, source_name, rss_url):
        """RSSフィードからニュースを取得"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(rss_url, headers=headers, timeout=5)
            response.raise_for_status()
            
            # XMLを解析
            root = ET.fromstring(response.content)
            news_items = []
            today = datetime.now().date()
            
            # RSS 2.0形式の場合
            items = root.findall('.//item')
            if not items:
                # Atom形式の場合
                items = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            for item in items[:10]:  # 最新10件を取得
                try:
                    # タイトルを取得
                    title_elem = item.find('title')
                    if title_elem is None:
                        title_elem = item.find('.//{http://www.w3.org/2005/Atom}title')
                    title = title_elem.text if title_elem is not None else 'タイトルなし'
                    
                    # リンクを取得
                    link_elem = item.find('link')
                    if link_elem is None:
                        link_elem = item.find('.//{http://www.w3.org/2005/Atom}link')
                        link = link_elem.get('href') if link_elem is not None else ''
                    else:
                        link = link_elem.text if link_elem.text else ''
                    
                    # 説明を取得
                    desc_elem = item.find('description')
                    if desc_elem is None:
                        desc_elem = item.find('.//{http://www.w3.org/2005/Atom}summary')
                    description = desc_elem.text if desc_elem is not None else ''
                    
                    # HTMLタグを除去
                    if description:
                        description = BeautifulSoup(description, 'html.parser').get_text()
                        description = description[:200] + '...' if len(description) > 200 else description
                    
                    # 日付を取得
                    date_elem = item.find('pubDate')
                    if date_elem is None:
                        date_elem = item.find('.//{http://www.w3.org/2005/Atom}published')
                    if date_elem is None:
                        date_elem = item.find('.//{http://www.w3.org/2005/Atom}updated')
                    
                    if date_elem is not None:
                        pub_date = self.parse_rss_date(date_elem.text)
                    else:
                        pub_date = today
                    
                    # 今日の記事のみを取得
                    if pub_date == today:
                        news_items.append({
                            'title': title.strip(),
                            'link': link.strip(),
                            'summary': description.strip(),
                            'published': pub_date.strftime('%Y-%m-%d'),
                            'source': source_name
                        })
                except Exception as e:
                    print(f"Error processing RSS item from {source_name}: {e}")
                    continue
            
            return news_items
        except Exception as e:
            print(f"Error fetching RSS from {source_name}: {e}")
            return []
    
    def get_news_from_web(self, source_name, url, selector):
        """Webスクレイピングでニュースを取得（フォールバック）"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            news_items = []
            
            # セレクターでニュースリンクを取得
            links = soup.select(selector)[:10]
            
            for link in links:
                try:
                    title = link.get_text(strip=True)
                    href = link.get('href')
                    
                    if href and title:
                        # 相対URLを絶対URLに変換
                        full_url = urljoin(url, href)
                        
                        news_items.append({
                            'title': title,
                            'link': full_url,
                            'summary': '',
                            'published': datetime.now().strftime('%Y-%m-%d'),
                            'source': source_name
                        })
                except Exception as e:
                    print(f"Error processing link from {source_name}: {e}")
                    continue
            
            return news_items
        except Exception as e:
            print(f"Error scraping {source_name}: {e}")
            return []
    
    def get_all_news(self):
        """全てのニュースソースから今日のニュースを取得"""
        all_news = []
        
        for source_name, source_info in self.news_sources.items():
            try:
                print(f"Fetching news from {source_name}...")
                
                # まずRSSから取得を試行（タイムアウトを短縮）
                rss_news = self.get_news_from_rss(source_name, source_info['rss'])
                
                if rss_news:
                    all_news.extend(rss_news)
                    print(f"Found {len(rss_news)} articles from {source_name} RSS")
                else:
                    # RSSが失敗した場合はWebスクレイピングを試行
                    print(f"RSS failed for {source_name}, trying web scraping...")
                    web_news = self.get_news_from_web(source_name, source_info['url'], source_info['selector'])
                    all_news.extend(web_news)
                    print(f"Found {len(web_news)} articles from {source_name} web scraping")
                
                # Vercelのタイムアウト対策: 待機時間を短縮
                time.sleep(0.5)
                
                # 7秒経過したら残りのソースをスキップ（Vercelの10秒制限対策）
                import time as time_module
                if hasattr(self, 'start_time'):
                    elapsed = time_module.time() - self.start_time
                    if elapsed > 7:
                        print(f"Timeout approaching, stopping at {source_name}")
                        break
                else:
                    self.start_time = time_module.time()
                    
            except Exception as e:
                print(f"Error processing {source_name}: {e}")
                continue
        
        print(f"Total articles found: {len(all_news)}")
        return all_news

# グローバルインスタンス
news_aggregator = NewsAggregator()

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """静的ファイルの配信"""
    static_dir = os.path.join(BASE_DIR, 'static')
    return send_from_directory(static_dir, filename)

@app.route('/api/test')
def test():
    """テスト用APIエンドポイント"""
    return jsonify({
        'success': True,
        'message': 'API is working!',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/news')
def get_news():
    """ニュースAPIエンドポイント"""
    try:
        news = news_aggregator.get_all_news()
        return jsonify({
            'success': True,
            'news': news,
            'count': len(news),
            'updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Vercel用のエクスポート - 最新の仕様に合わせて修正
app.wsgi_app = app.wsgi_app

# 通常の実行用
if __name__ == '__main__':
    app.run(debug=False) 