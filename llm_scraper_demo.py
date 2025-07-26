#!/usr/bin/env python3
"""
LLMスクレイピングシステム 包括的デモンストレーション

このファイルは以下を実演します：
1. 生HTMLデータの取得と表示
2. 前処理データの生成と表示  
3. LLM抽出結果の表示
4. 異なるスクレイピング手法の比較
5. カスタムスキーマの使用例
"""

import asyncio
import os
import sys
import json
import time
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional

# パスの設定
sys.path.append(os.path.join(os.path.dirname(__file__), 'banner_maker', 'src'))

from llm_scraper import LLMWebScraper

# 環境変数の読み込み
load_dotenv()

class ProductInfo(BaseModel):
    """カスタム商品情報スキーマ（デモ用）"""
    product_name: Optional[str] = Field(description="商品名")
    brand: Optional[str] = Field(description="ブランド名")
    price: Optional[str] = Field(description="価格")
    availability: Optional[str] = Field(description="在庫状況")
    description: Optional[str] = Field(description="商品説明")
    features: Optional[List[str]] = Field(description="主要機能")
    category: Optional[str] = Field(description="カテゴリ")

def print_section(title: str, content: str = ""):
    """セクション表示用のヘルパー関数"""
    print("\n" + "="*80)
    print(f"📋 {title}")
    print("="*80)
    if content:
        print(content)

def print_subsection(title: str):
    """サブセクション表示用のヘルパー関数"""
    print(f"\n🔹 {title}")
    print("-" * 60)

def truncate_text(text: str, max_length: int = 200) -> str:
    """テキストを指定長さで切り詰める"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

async def demonstrate_scraping_process(url: str, site_name: str):
    """スクレイピングプロセス全体のデモンストレーション"""
    
    print_section(f"{site_name} のスクレイピングデモンストレーション", f"URL: {url}")
    
    # API キーの確認
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ エラー: GOOGLE_API_KEY が設定されていません")
        print("   .envファイルにAPI キーを設定してください:")
        print("   GOOGLE_API_KEY='your-api-key-here'")
        return

    # スクレイパー初期化
    scraper = LLMWebScraper(api_key)
    
    try:
        # ステップ1: 生HTMLデータの取得
        print_subsection("ステップ1: 生HTMLデータの取得")
        print("🔄 HTML取得中...")
        
        start_time = time.time()
        raw_html, method_used = await scraper._get_raw_html_with_method(url)
        fetch_time = time.time() - start_time
        
        if raw_html:
            print(f"✅ HTML取得成功！")
            print(f"📊 取得方法: {method_used}")
            print(f"⏱️  取得時間: {fetch_time:.2f}秒")
            print(f"📏 データサイズ: {len(raw_html):,} 文字")
            print(f"🔍 HTMLプレビュー:")
            print(truncate_text(raw_html, 300))
        else:
            print("❌ HTML取得失敗")
            return
            
        # ステップ2: HTMLの前処理
        print_subsection("ステップ2: HTMLの前処理とクリーニング")
        print("🔄 前処理実行中...")
        
        start_time = time.time()
        preprocessed_content = scraper._preprocess_html_for_llm(raw_html)
        preprocess_time = time.time() - start_time
        
        print(f"✅ 前処理完了！")
        print(f"⏱️  処理時間: {preprocess_time:.2f}秒")
        print(f"📏 処理前サイズ: {len(raw_html):,} 文字")
        print(f"📏 処理後サイズ: {len(preprocessed_content):,} 文字")
        print(f"📉 圧縮率: {((len(raw_html) - len(preprocessed_content)) / len(raw_html) * 100):.1f}%")
        print(f"🔍 前処理後プレビュー:")
        print(truncate_text(preprocessed_content, 400))
        
        # 前処理データをファイルに保存
        preprocessed_file = scraper._save_preprocessed_data(url, preprocessed_content)
        if preprocessed_file:
            print(f"💾 前処理データ保存: {preprocessed_file}")
        
        # ステップ3: LLMによる構造化抽出
        print_subsection("ステップ3: LLMによる構造化データ抽出")
        print("🔄 LLM処理中...")
        
        start_time = time.time()
        llm_result = await scraper._extract_with_llm_structured(
            preprocessed_content, url, ProductInfo
        )
        llm_time = time.time() - start_time
        
        print(f"✅ LLM抽出完了！")
        print(f"⏱️  LLM処理時間: {llm_time:.2f}秒")
        print(f"🎯 信頼度スコア: {llm_result.get('extraction_confidence', 0):.2f}")
        print(f"🤖 使用モデル: {llm_result.get('model_used', 'unknown')}")
        
        # ステップ4: 抽出結果の詳細表示
        print_subsection("ステップ4: 抽出された構造化データ")
        extracted_data = llm_result.get('llm_extracted_data', {})
        
        if extracted_data:
            for key, value in extracted_data.items():
                if value and str(value).strip() not in ['', 'null', 'None', 'N/A']:
                    if isinstance(value, list):
                        print(f"• {key}: {', '.join(str(v) for v in value[:3])}{'...' if len(value) > 3 else ''}")
                    else:
                        display_value = truncate_text(str(value), 100)
                        print(f"• {key}: {display_value}")
        else:
            print("⚠️  抽出されたデータがありません")
        
        # ステップ5: 最終結果の生成と保存
        print_subsection("ステップ5: 最終結果の生成")
        
        final_result = {
            'url': url,
            'llm_extracted_data': extracted_data,
            'extraction_method': method_used,
            'confidence': llm_result.get('extraction_confidence', 0.0),
            'timestamp': time.time(),
            'model_used': scraper.model_name,
            'preprocessed_data_file': preprocessed_file,
            'performance_metrics': {
                'html_fetch_time': fetch_time,
                'preprocessing_time': preprocess_time,
                'llm_processing_time': llm_time,
                'total_time': fetch_time + preprocess_time + llm_time,
                'data_compression_ratio': f"{((len(raw_html) - len(preprocessed_content)) / len(raw_html) * 100):.1f}%"
            }
        }
        
        # 結果をファイルに保存
        result_filename = f"demo_result_{site_name.lower().replace(' ', '_')}.json"
        with open(result_filename, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 最終結果保存: {result_filename}")
        
        # パフォーマンスサマリー
        total_time = fetch_time + preprocess_time + llm_time
        print_subsection("パフォーマンスサマリー")
        print(f"⚡ 合計処理時間: {total_time:.2f}秒")
        print(f"   - HTML取得: {fetch_time:.2f}秒 ({fetch_time/total_time*100:.1f}%)")
        print(f"   - 前処理: {preprocess_time:.2f}秒 ({preprocess_time/total_time*100:.1f}%)")
        print(f"   - LLM処理: {llm_time:.2f}秒 ({llm_time/total_time*100:.1f}%)")
        
        return final_result
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        print(f"📝 詳細:")
        traceback.print_exc()
        return None

async def compare_methods():
    """異なるスクレイピング手法の比較デモ"""
    
    print_section("スクレイピング手法比較デモ")
    
    test_urls = [
        ("https://creditcard-get.net/genre/s008pt-2/?code=loget-002", "クレジットカード比較サイト"),
        ("https://www.yodobashi.com/product/100000001005807664/", "ヨドバシカメラ商品ページ")
    ]
    
    results = []
    
    for url, site_name in test_urls:
        print(f"\n🌐 テスト対象: {site_name}")
        result = await demonstrate_scraping_process(url, site_name)
        if result:
            results.append((site_name, result))
    
    # 比較サマリー
    if len(results) >= 2:
        print_section("手法比較サマリー")
        
        for site_name, result in results:
            method = result['extraction_method']
            confidence = result['confidence']
            total_time = result['performance_metrics']['total_time']
            print(f"🔹 {site_name}:")
            print(f"   - 使用手法: {method}")
            print(f"   - 信頼度: {confidence:.2f}")
            print(f"   - 処理時間: {total_time:.2f}秒")
            print(f"   - 商品名: {result['llm_extracted_data'].get('product_name', 'N/A')}")

async def demonstrate_schema_flexibility():
    """スキーマの柔軟性デモンストレーション（概念説明のみ）"""
    
    print_section("スキーマ柔軟性の説明")
    
    print("🔧 カスタムスキーマ機能について:")
    print("   - デフォルトスキーマ以外にも、用途に応じたカスタムスキーマを定義可能")
    print("   - 例: 不動産情報、求人情報、ニュース記事など特定分野に特化")
    print("   - Pydanticを使用した型安全なスキーマ定義")
    print("\n💡 カスタムスキーマ例:")
    print("   class RealEstateInfo(BaseModel):")
    print("       property_type: str = Field(description='物件種別')")
    print("       price: str = Field(description='価格')")
    print("       location: str = Field(description='所在地')")
    print("       floor_area: str = Field(description='床面積')")
    print("       nearest_station: str = Field(description='最寄り駅')")
    print("\n📝 使用方法:")
    print("   result = await scraper.scrape_page_with_llm(")
    print("       url, extraction_schema=RealEstateInfo)")
    print("\n✨ この機能により、様々な分野のウェブサイトに対応可能です")

async def main():
    """メインデモンストレーション関数"""
    
    print("🚀 LLMスクレイピングシステム 包括的デモンストレーション")
    print("="*80)
    print("このデモでは以下の機能を実演します:")
    print("1. 生HTMLデータの取得")
    print("2. HTMLの前処理とクリーニング")
    print("3. LLMによる構造化抽出")
    print("4. 異なるサイトでの手法比較")
    print("5. スキーマ柔軟性の説明")
    print("="*80)
    
    try:
        # メイン比較デモ
        await compare_methods()
        
        # スキーマ柔軟性の説明
        await demonstrate_schema_flexibility()
        
        # 最終サマリー
        print_section("デモンストレーション完了")
        print("✅ すべてのデモが完了しました")
        print("\n📁 生成されたファイル:")
        print("   - demo_result_*.json - 各サイトの抽出結果")
        print("   - preprocessed_*.txt - 前処理されたデータ")
        print("\n📖 詳細な技術仕様については LLM_SCRAPER_DOCUMENTATION.md を参照してください")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  デモが中断されました")
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🎬 LLMスクレイピングシステム デモンストレーション開始")
    print("=" * 80)
    
    asyncio.run(main())
    
    print("\n🎭 デモンストレーション終了")
    print("ありがとうございました！")