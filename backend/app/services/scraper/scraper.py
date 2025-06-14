#!/usr/bin/env python3
"""
G検定対策ツール - Webスクレイピング基盤
Playwright を用いて指定 URL の HTML を取得し、robots.txt を遵守する基盤
"""

import asyncio
import sys
import time
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from datetime import datetime
import requests
from playwright.async_api import async_playwright


class GExamScraper:
    """G検定対策用スクレイパー"""
    
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; GExamBot/1.0)"
        self.min_delay = 1.0  # 最小ウェイト時間（秒）
        self.output_dir = Path("./html")
        self.last_request_time = 0
    
    def check_robots_txt(self, url: str) -> bool:
        """
        robots.txt を確認してクロール可能かチェック
        
        Args:
            url: チェック対象のURL
            
        Returns:
            bool: クロール可能な場合 True
        """
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            robots_url = urljoin(base_url, "/robots.txt")
            
            print(f"📋 robots.txt をチェック中: {robots_url}")
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            can_fetch = rp.can_fetch(self.user_agent, url)
            
            if can_fetch:
                print(f"✅ robots.txt: クロール許可")
            else:
                print(f"❌ robots.txt: クロール禁止")
                
            return can_fetch
            
        except Exception as e:
            print(f"⚠️  robots.txt の確認でエラー: {e}")
            print("🤔 安全のため続行を中止します")
            return False
    
    def generate_filename(self, url: str) -> tuple[str, str]:
        """
        保存用のファイル名とディレクトリパスを生成
        
        Args:
            url: 対象URL
            
        Returns:
            tuple: (ディレクトリパス, ファイル名)
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # URLからスラグを生成（ファイル名に使用可能な文字のみ）
        path = parsed_url.path.strip("/")
        if path:
            slug = re.sub(r'[^\w\-_.]', '_', path)
            # 長すぎる場合は先頭50文字に制限
            slug = slug[:50] if len(slug) > 50 else slug
        else:
            slug = "index"
        
        # 日付を追加
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}_{slug}.html"
        
        directory = self.output_dir / domain
        
        return str(directory), filename
    
    def apply_rate_limit(self):
        """レート制限を適用（1秒以上のウェイト）"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.min_delay:
            wait_time = self.min_delay - elapsed
            print(f"⏱️  レート制限: {wait_time:.2f}秒待機中...")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    async def fetch_html(self, url: str) -> str:
        """
        Playwright を使用してHTMLを取得
        
        Args:
            url: 取得対象のURL
            
        Returns:
            str: 取得したHTML
        """
        print(f"🌐 HTMLを取得中: {url}")
        
        async with async_playwright() as p:
            # ヘッドレスChrome を起動
            browser = await p.chromium.launch(headless=True)
            
            # ユーザーエージェントを設定
            context = await browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            try:
                # ページを読み込み（SPA対応のため十分な待機時間）
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # 追加の待機時間（JavaScript実行完了を確保）
                await page.wait_for_timeout(2000)
                
                # HTML取得
                html_content = await page.content()
                
                print(f"✅ HTML取得完了 ({len(html_content):,} 文字)")
                return html_content
                
            except Exception as e:
                print(f"❌ HTML取得失敗: {e}")
                raise
            finally:
                await browser.close()
    
    def save_html(self, html_content: str, directory: str, filename: str) -> str:
        """
        HTMLをファイルに保存
        
        Args:
            html_content: 保存するHTML
            directory: 保存先ディレクトリ
            filename: ファイル名
            
        Returns:
            str: 保存されたファイルパス
        """
        # ディレクトリ作成
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # ファイル保存
        file_path = dir_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"💾 保存完了: {file_path}")
        return str(file_path)
    
    async def scrape(self, url: str) -> str:
        """
        メインのスクレイピング処理
        
        Args:
            url: スクレイピング対象のURL
            
        Returns:
            str: 保存されたファイルパス
        """
        print(f"🚀 スクレイピング開始: {url}")
        
        # 1. robots.txt チェック
        if not self.check_robots_txt(url):
            raise ValueError("robots.txt によりクロールが禁止されています")
        
        # 2. レート制限適用
        self.apply_rate_limit()
        
        # 3. HTML取得
        html_content = await self.fetch_html(url)
        
        # 4. ファイル保存
        directory, filename = self.generate_filename(url)
        file_path = self.save_html(html_content, directory, filename)
        
        print(f"🎉 スクレイピング完了!")
        return file_path


async def main():
    """メイン関数"""
    if len(sys.argv) != 2:
        print("使用方法: python scraper.py <target_url>")
        print("例: python scraper.py https://example.com/g-exam-article")
        sys.exit(1)
    
    target_url = sys.argv[1]
    
    # URL形式の簡単なバリデーション
    if not target_url.startswith(('http://', 'https://')):
        print("❌ エラー: URLは http:// または https:// で始まる必要があります")
        sys.exit(1)
    
    scraper = GExamScraper()
    
    try:
        file_path = await scraper.scrape(target_url)
        print(f"\n📁 保存先: {file_path}")
        
    except KeyboardInterrupt:
        print("\n⚠️  ユーザーによって中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())