class NewsAggregatorApp {
    constructor() {
        this.newsData = [];
        this.isLoading = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadNews();
    }

    bindEvents() {
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadNews());
        }

        // 自動更新（5分ごと）
        setInterval(() => {
            if (!this.isLoading) {
                this.loadNews();
            }
        }, 5 * 60 * 1000);
    }

    async loadNews() {
        if (this.isLoading) return;

        this.isLoading = true;
        this.showLoading();
        this.hideError();

        try {
            const response = await fetch('/api/news');
            const data = await response.json();

            if (data.success) {
                this.newsData = data.news;
                this.renderNews();
                this.updateStats(data.count, data.updated);
            } else {
                throw new Error(data.error || 'ニュースの取得に失敗しました');
            }
        } catch (error) {
            console.error('Error loading news:', error);
            this.showError(error.message);
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }

    showLoading() {
        const loading = document.getElementById('loading');
        const stats = document.getElementById('stats');
        const newsSources = document.getElementById('news-sources');
        
        if (loading) loading.style.display = 'block';
        if (stats) stats.style.display = 'none';
        if (newsSources) newsSources.innerHTML = '';
    }

    hideLoading() {
        const loading = document.getElementById('loading');
        if (loading) loading.style.display = 'none';
    }

    showError(message) {
        const errorElement = document.getElementById('error-message');
        const errorText = document.getElementById('error-text');
        
        if (errorElement && errorText) {
            errorText.textContent = message;
            errorElement.style.display = 'block';
        }
    }

    hideError() {
        const errorElement = document.getElementById('error-message');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }

    updateStats(count, updated) {
        const stats = document.getElementById('stats');
        const totalCount = document.getElementById('total-count');
        const lastUpdated = document.getElementById('last-updated');

        if (stats) stats.style.display = 'flex';
        if (totalCount) totalCount.textContent = count;
        if (lastUpdated) lastUpdated.textContent = `最終更新: ${updated}`;
    }

    renderNews() {
        const newsSourcesContainer = document.getElementById('news-sources');
        if (!newsSourcesContainer) return;

        // ニュースソースごとにグループ化
        const groupedNews = this.groupNewsBySource();
        
        newsSourcesContainer.innerHTML = '';

        Object.entries(groupedNews).forEach(([source, articles]) => {
            const sourceElement = this.createSourceElement(source, articles);
            newsSourcesContainer.appendChild(sourceElement);
        });

        // フェードインアニメーション
        newsSourcesContainer.classList.add('fade-in');
    }

    groupNewsBySource() {
        const grouped = {};
        
        this.newsData.forEach(article => {
            const source = article.source;
            if (!grouped[source]) {
                grouped[source] = [];
            }
            grouped[source].push(article);
        });

        return grouped;
    }

    createSourceElement(sourceName, articles) {
        const sourceDiv = document.createElement('div');
        sourceDiv.className = 'news-source fade-in';

        const sourceIcon = this.getSourceIcon(sourceName);
        
        sourceDiv.innerHTML = `
            <div class="source-header">
                <div class="source-icon">
                    <i class="${sourceIcon}"></i>
                </div>
                <h2 class="source-title">${sourceName}</h2>
                <span class="source-count">${articles.length}件</span>
            </div>
            <ul class="news-list">
                ${articles.map(article => this.createNewsItemHTML(article)).join('')}
            </ul>
        `;

        return sourceDiv;
    }

    createNewsItemHTML(article) {
        const summary = article.summary ? 
            `<p class="news-summary">${this.escapeHtml(article.summary)}</p>` : '';
        
        return `
            <li class="news-item">
                <h3 class="news-title">
                    <a href="${article.link}" target="_blank" rel="noopener noreferrer">
                        ${this.escapeHtml(article.title)}
                    </a>
                </h3>
                ${summary}
                <div class="news-meta">
                    <span class="news-date">
                        <i class="fas fa-calendar-alt"></i>
                        ${article.published}
                    </span>
                    <a href="${article.link}" target="_blank" rel="noopener noreferrer" class="external-link">
                        <i class="fas fa-external-link-alt"></i>
                        記事を読む
                    </a>
                </div>
            </li>
        `;
    }

    getSourceIcon(sourceName) {
        const icons = {
            'GIGAZINE': 'fas fa-rocket',
            'ITmedia NEWS': 'fas fa-microchip',
            'Gizmodo Japan': 'fas fa-cog',
            'MIT Technology Review Japan': 'fas fa-flask'
        };
        
        return icons[sourceName] || 'fas fa-newspaper';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// アプリケーション初期化
document.addEventListener('DOMContentLoaded', () => {
    new NewsAggregatorApp();
});

// サービスワーカー登録（オフライン対応）
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
} 