# LLMスクレイピングシステム 詳細ドキュメント

## 概要

このシステムは、従来のCSSセレクタベースのスクレイピング手法を大幅に改良し、Google Gemini 2.5 Flash Liteを活用したインテリジェントなコンテンツ抽出システムです。様々なウェブサイトに対応し、アンチボット対策を回避しながら構造化データを自動抽出します。

## システムアーキテクチャ

### 主要コンポーネント

1. **LLMWebScraper** - メインのスクレイピングクラス
2. **HTML取得エンジン** - Playwright と requests の併用
3. **前処理エンジン** - HTMLをLLM最適化されたマークダウンに変換
4. **構造化抽出エンジン** - Gemini APIを使用した構造化データ抽出
5. **出力管理** - クリーンな結果形式と前処理データの分離保存

## 技術仕様

### 使用技術
- **LLMモデル**: Google Gemini 2.5 Flash Lite（安定版）
- **ブラウザ自動化**: Playwright（Chromium）
- **HTTPクライアント**: requests（高度なブラウザ偽装）
- **HTMLパーサー**: selectolax
- **マークダウン変換**: html2text
- **スキーマ定義**: Pydantic

### データフロー

```
URL入力 → HTML取得 → 前処理 → LLM抽出 → 構造化出力
   ↓         ↓        ↓       ↓        ↓
  指定    PlayWright  HTML→MD  Gemini   JSON
         ↓          ノイズ除去  API    + ファイル
      requests      最適化   構造化
      (フォールバック)  (12KB制限) 出力
```

## HTML取得戦略

### 2段階フォールバック方式

#### 1. Playwright（優先方式）
- **利点**: JavaScript実行、動的コンテンツ対応
- **設定**: 5秒タイムアウト（高速失敗）
- **ステルス機能**: 
  - ユーザーエージェント偽装
  - ビューポート設定（1920x1080）
  - 自動化検出回避

#### 2. Requests（フォールバック）
- **利点**: アンチボット回避に効果的
- **特徴**: 
  - 複数ユーザーエージェントローテーション
  - 包括的ブラウザヘッダー偽装
  - リトライ機能（3回まで）
  - ランダム遅延

```python
# 使用例：ユーザーエージェント
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...',
    # ...
]
```

## HTML前処理システム

### 前処理の目的
1. **ノイズ除去**: 広告、ナビゲーション、フッターの削除
2. **トークン最適化**: LLM処理用に12KB以下に制限
3. **構造化**: マークダウン形式への変換

### 除去対象要素
```python
noise_selectors = [
    'script', 'style', 'noscript', 'meta', 'link',
    'nav', 'footer', 'header', 'aside',
    '.nav', '.navigation', '.menu', '.sidebar',
    '.ads', '.advertisement', '.banner-ad',
    '.social-share', '.social-media',
    '.cookie', '.gdpr', '.popup', '.modal',
    '.breadcrumb', '.pagination'
]
```

### 前処理フロー
1. **HTMLパース**: selectolaxによる高速パース
2. **要素除去**: ノイズ要素の削除
3. **マークダウン変換**: html2textによる変換
4. **テキストクリーニング**: 
   - 過剰な空白除去
   - 不要なパターン削除
   - 特殊文字の正規化
5. **長さ制限**: 12KB制限、文境界での切断

## LLM構造化抽出

### Pydanticスキーマ
デフォルトの抽出フィールド：

```python
class ExtractedContent(BaseModel):
    product_name: Optional[str] = Field(description="商品・サービス名")
    product_description: Optional[str] = Field(description="詳細説明")
    key_features: Optional[List[str]] = Field(description="主要機能・特徴")
    price_info: Optional[str] = Field(description="価格情報")
    brand_name: Optional[str] = Field(description="ブランド・会社名")
    category: Optional[str] = Field(description="カテゴリ")
    target_audience: Optional[str] = Field(description="対象顧客")
    unique_selling_points: Optional[str] = Field(description="独自性・差別化要因")
    call_to_action: Optional[str] = Field(description="行動喚起")
    availability: Optional[str] = Field(description="在庫・利用可能性")
    specifications: Optional[Dict[str, str]] = Field(description="技術仕様")
    reviews_sentiment: Optional[str] = Field(description="レビュー感情")
```

### カスタムスキーマ対応
用途に応じてカスタムスキーマを定義可能：

```python
class ProductInfo(BaseModel):
    product_name: Optional[str] = Field(description="商品名")
    brand: Optional[str] = Field(description="ブランド名") 
    price: Optional[str] = Field(description="価格")
    # ... 独自フィールド
```

## 信頼度スコアリング

### 計算方式
```python
confidence = (completeness_score * 0.7) + (quality_score * 0.3)
```

#### 完全性スコア (70%重み)
- 非空フィールド数 ÷ 総フィールド数

#### 品質スコア (30%重み)
- product_name存在: +0.25
- product_description長さ(20文字以上): +0.25  
- key_features存在: +0.25
- brand_name/category存在: +0.25

## 出力フォーマット

### クリーン出力構造
```json
{
  "url": "https://example.com/product",
  "llm_extracted_data": {
    "product_name": "商品名",
    "product_description": "商品説明...",
    "key_features": ["特徴1", "特徴2"],
    "price_info": "¥1,000",
    // ... その他フィールド
  },
  "extraction_method": "playwright", // または "requests"
  "confidence": 0.95,
  "timestamp": 1753550565.848541,
  "model_used": "gemini-2.5-flash-lite",
  "preprocessed_data_file": "preprocessed_abc123def456.txt"
}
```

### 前処理データファイル
```
# Preprocessed Data for: https://example.com/product
# Generated at: 2025-07-27 02:22:44
# ============================================================

商品名: サンプル商品
価格: ¥1,000
在庫: 在庫あり

商品説明:
これは素晴らしい商品です...
```

## パフォーマンス最適化

### 高速化技術
1. **高速フェイル**: Playwright 5秒タイムアウト
2. **並列処理**: 複数ツール呼び出し対応
3. **キャッシュ**: HTML取得結果の一時保存
4. **トークン最適化**: 12KB制限による処理高速化

### 処理時間比較
- **従来手法**: 66秒（複数タイムアウト）
- **最適化後**: 7.6秒（高速フォールバック）

## 使用方法

### 基本的な使用例
```python
from llm_scraper import LLMWebScraper

# 初期化
scraper = LLMWebScraper(google_api_key="your-api-key")

# スクレイピング実行
result = await scraper.scrape_page_with_llm(
    url="https://example.com",
    save_preprocessed=True
)

print(f"抽出方法: {result['extraction_method']}")
print(f"信頼度: {result['confidence']}")
print(f"商品名: {result['llm_extracted_data']['product_name']}")
```

### カスタムスキーマ使用例
```python
from pydantic import BaseModel, Field

class CustomSchema(BaseModel):
    title: Optional[str] = Field(description="タイトル")
    content: Optional[str] = Field(description="内容")

result = await scraper.scrape_page_with_llm(
    url="https://example.com",
    extraction_schema=CustomSchema
)
```

## 対応サイト例

### 成功実績
- **Yodobashi.com**: requests方式で100%信頼度
- **クレジットカード比較サイト**: playwright方式で100%信頼度
- **ECサイト一般**: 高い成功率
- **企業情報サイト**: 良好な抽出品質

### アンチボット対策
- Cloudflare保護サイト: requests方式で対応
- JavaScript必須サイト: playwright方式で対応
- 複合保護サイト: 自動フォールバック

## エラーハンドリング

### 一般的なエラーと対処
1. **API制限**: レート制限考慮、リトライ機能
2. **接続エラー**: 自動フォールバック機能
3. **パース失敗**: エラーログ出力、緊急フォールバック
4. **ファイル保存失敗**: ログ出力、処理継続

## セキュリティ考慮事項

### データ保護
- API キーの環境変数管理
- 一時ファイルの適切な削除
- ログにおける機密情報の除外

### 利用規約遵守
- robots.txt の尊重
- アクセス頻度の制限
- 利用規約の確認推奨

## 今後の拡張予定

### 機能拡張
1. **多言語対応**: 英語、中国語等
2. **画像解析**: OCR、画像認識機能
3. **リアルタイム監視**: 価格変動監視
4. **バッチ処理**: 大量URL一括処理

### パフォーマンス改善
1. **キャッシュ機能**: Redis統合
2. **分散処理**: マルチワーカー対応
3. **ストリーミング**: 大容量コンテンツ対応

## 技術サポート

### ログレベル
- INFO: 通常の処理状況
- WARNING: 注意が必要な状況
- ERROR: エラー発生時

### デバッグ機能
- 前処理データの詳細出力
- API呼び出し詳細ログ
- パフォーマンス計測

## ライセンスと制約

### 使用制限
- Google GenAI API の利用規約に従う
- 対象サイトの利用規約を確認
- 商用利用時の追加考慮事項

### 免責事項
- スクレイピング結果の精度保証なし
- 対象サイトの変更による影響
- API制限による利用制約