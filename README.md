# デイリーテックダイジェスト

指定されたテクノロジーニュースサイトから最新のニュースを自動収集し、見やすく表示するWebアプリケーションです。

## 対応ニュースサイト

- **GIGAZINE** - https://gigazine.net
- **ITmedia NEWS** - https://www.itmedia.co.jp/news/
- **Gizmodo Japan** - https://www.gizmodo.jp
- **MIT Technology Review Japan** - https://www.technologyreview.jp

## 機能

- 📰 複数のニュースサイトから今日のニュースを自動収集
- 🔄 リアルタイム更新（5分間隔）
- 📱 レスポンシブデザイン（モバイル対応）
- 🎨 モダンで美しいUI
- ⚡ 高速なニュース取得（RSS + Webスクレイピング）
- 📊 ニュース統計表示

## セットアップ手順

### 1. 依存関係のインストール

```bash
# Python仮想環境の作成（推奨）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows

# 必要なパッケージのインストール
pip install -r requirements.txt
```

### 2. アプリケーションの起動

```bash
python app.py
```

### 3. ブラウザでアクセス

アプリケーションが起動したら、ブラウザで以下のURLにアクセスしてください：

```
http://localhost:5000
```

## 使用方法

1. **自動更新**: ページを開くと自動的にニュースが読み込まれます
2. **手動更新**: 「更新」ボタンをクリックして最新ニュースを取得
3. **記事閲覧**: 記事タイトルまたは「記事を読む」リンクをクリックして元記事を表示

## 技術仕様

### バックエンド
- **Flask** - Webフレームワーク
- **BeautifulSoup4** - HTMLパーサー
- **Requests** - HTTP通信
- **Feedparser** - RSSフィード解析

### フロントエンド
- **HTML5/CSS3** - マークアップとスタイリング
- **JavaScript (ES6+)** - インタラクティブ機能
- **Font Awesome** - アイコン
- **Google Fonts** - 日本語フォント

### データ取得方式
1. **RSS優先**: まずRSSフィードから記事を取得
2. **Webスクレイピング**: RSSが利用できない場合のフォールバック
3. **日付フィルタリング**: 今日の記事のみを表示

## ファイル構成

```
news-aggregator/
├── app.py                 # メインアプリケーション
├── requirements.txt       # Python依存関係
├── README.md             # このファイル
├── templates/
│   └── index.html        # HTMLテンプレート
└── static/
    ├── css/
    │   └── style.css     # スタイルシート
    └── js/
        └── app.js        # JavaScript
```

## カスタマイズ

### ニュースソースの追加

`app.py`の`NewsAggregator`クラス内の`news_sources`辞書に新しいソースを追加できます：

```python
'新しいサイト名': {
    'url': 'https://example.com',
    'rss': 'https://example.com/rss',
    'selector': '.article-title a'  # CSSセレクター
}
```

### 更新間隔の変更

`static/js/app.js`の以下の行で更新間隔を変更できます：

```javascript
// 5分間隔 → 10分間隔に変更する場合
setInterval(() => {
    if (!this.isLoading) {
        this.loadNews();
    }
}, 10 * 60 * 1000);  // 5 → 10に変更
```

## トラブルシューティング

### ニュースが取得できない場合

1. **インターネット接続を確認**
2. **ニュースサイトがアクセス可能か確認**
3. **コンソールでエラーメッセージを確認**

### パフォーマンスの問題

- ニュースサイトの応答が遅い場合があります
- 複数サイトから同時取得するため、初回読み込みに時間がかかることがあります

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 注意事項

- このアプリケーションは教育・個人利用目的で作成されています
- 各ニュースサイトの利用規約を遵守してください
- 過度なアクセスを避けるため、適切な間隔でリクエストを送信しています 