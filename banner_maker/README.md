# AI Banner Maker - クリエイティブアセット管理プラットフォーム

AI搭載のコンテンツ分析、画像抽出、コピー生成、Canva連携によるマーケティングアセット作成のためのプロフェッショナルWebアプリケーション。

## 🎯 機能概要

**入力**: ランディングページURL → **出力**: Canvaで使用可能な整理されたクリエイティブアセット

**例**: `https://www.yodobashi.com/product/12345/` → 抽出画像、AI生成マーケティングコピー、クリエイティブインサイト、適切な寸法のCanva空白デザイン

## 🚀 主要機能

### **🔍 高度なWeb分析**

#### **強化されたスクレイピング技術**
- **プラットフォーム特化最適化** - ヨドバシ、Amazon等の専用CSSセレクターで高精度抽出対応可能
- **3層階層抽出システム** - Platform特化 → Primary → Secondary の優先度別コンテンツ抽出
- **広範囲tag対応** - 200+種類のHTMLセレクターで網羅的なコンテンツキャプチャ
- **重複除去システム** - 同一内容の自動フィルタリングで高品質テキスト抽出

#### **アンチボット保護システム**
- **ハイブリッド戦略**: まずPlaywright（高性能ブラウザー）でアクセス、失敗時はRequests（軽量方式）に自動切替
- **ステルス技術による人間らしい動作の模擬**:
  - `navigator.webdriver`プロパティの偽装で自動化ツールであることを隠す
  - 実際のChromeブラウザーと同じUser-AgentとHTTPヘッダーを使用
  - ランダム遅延とマウス移動でヒューマンライクな操作を再現
- **複数リトライ機構** - 3段階のタイムアウト戦略で異なる方法を試行し確実にデータを取得

#### **動的コンテンツ完全対応**
- **JavaScript実行環境** - Playwright Chromiumで完全なブラウザー環境
- **無限スクロール対応** - 自動スクロール＋高さ検知で遅延読み込みコンテンツを完全取得
- **レイジーローディング処理** - 画像・テキストの段階的読み込み完了を待機
- **Dynamic DOM監視** - コンテンツ変更を検知して追加情報を取得

### **🖼️ インテリジェント画像管理**
- **スマート画像抽出** - Webページから高品質画像を自動検出・フィルタリング
- **多フォーマット対応** - PNG、JPG、JPEG、GIF、WebP（最大16MB）
- **ドラッグ&ドロップ対応** - Webページから画像を抽出、または独自画像をアップロード
- **自動クリーンアップ** - 一時ファイルとストレージを効率的に管理

### **✍️ AI搭載コピー生成**
- **複数バリエーション** - 5つのコピースタイル: ベネフィット、緊急性、プロモ、ニュートラル、親しみやすさ
- **スマート選択** - ライブプレビューと編集機能付きの手動選択
- **背景プロンプト** - 各コピーにAI背景生成プロンプトを含める
- **キャッシュシステム** - 効率性のため重複処理を回避

### **💡 クリエイティブインサイト＆解説**
- **包括的分析** - AI生成マーケティングインサイトとクリエイティブ方向性
- **ターゲットオーディエンス** - 詳細なオーディエンス分析と動機
- **セールスポイント** - 主要メリットと感情トリガーの特定
- **クリエイティブ方向性** - ビジュアルスタイル、カラー、タイポグラフィの推奨
- **メッセージング戦略** - ヘッドラインアプローチとトーンガイダンス
- **CTA提案** - 複数のコール・トゥ・アクションバリエーション

### **🎨 先進的AI背景生成**
- **3画像同時生成** - 1回のリクエストで3つの高品質バリエーション背景を作成
- **自動翻訳機能** - 日本語プロンプトを自動的に英語に翻訳して最適な画像品質を実現
- **アスペクト比自動調整** - 選択したバナーサイズに応じて最適なアスペクト比で生成
- **Canva自動統合** - 生成された全背景を自動的にCanvaにアップロード

### **🔗 シームレスCanva統合**
- **OAuth認証** - Canvaアカウントへの安全な接続
- **スマートアップロード** - 全アセットをCanvaライブラリに自動アップロード
- **適切な整理** - 正確な寸法とプロジェクト名で空白デザインを作成
- **複数フォーマット** - 全標準バナーサイズとソーシャルメディア形式をサポート

## 🏗️ 完全ワークフロー

```
ランディングページURL → 
  ↓
Webスクレイピング（アンチボット強化） →
  ↓
画像抽出 + コピー生成 + クリエイティブインサイト →
  ↓
オプション: AI背景生成 →
  ↓
アセットのCanvaアップロード + 空白デザイン作成
```

### **ステップバイステップ プロセス**

1. **📱 URL入力**: 任意のランディングページURLを入力
2. **🔄 自動分析**: プラットフォーム特化最適化でAIがコンテンツをスクレイピング
3. **🖼️ 画像抽出**: 高品質画像を自動抽出・表示
4. **✍️ コピー生成**: 背景プロンプト付きの5つのマーケティングコピーバリエーション
5. **💡 インサイト取得**: 包括的クリエイティブ戦略と推奨事項
6. **🎨 オプション背景**: コピーにマッチしたAI背景を生成
7. **📤 Canvaに送信**: 全アセットをアップロード、適切な寸法で空白デザインを作成
8. **🎯 Canvaで作成**: 提供されたアセットを使用して最終クリエイティブを構築

## 💻 インストール＆セットアップ

### **前提条件**
- Python 3.8以上
- Google Gemini API キー（Gemini 2.5 Flash Lite および Imagen 4.0 アクセス）
- Canva開発者アカウント（OAuth連携用）

### **🤖 使用AI技術詳細**

各機能で使用されているAIモデル：

#### **コピー生成（`copy_gen.py`）**
- **プライマリ**: `gemini-2.5-flash-lite` - 5つのマーケティングコピーバリエーション生成
- **機能**: Benefit、Urgency、Promo、Neutral、Playful の5スタイル生成
- **同時処理**: 単一API呼び出しで全バリエーションを効率的に生成

#### **クリエイティブインサイト生成（`explanation_gen.py`）**
- **プライマリ**: `gemini-2.5-flash-lite` - 包括的マーケティング分析
- **機能**: ターゲット分析、セールスポイント、クリエイティブ方向性、メッセージング戦略

#### **AI背景生成（`background_gen.py`）**
- **プライマリ**: `imagen-4.0-generate-preview-06-06` - 最新の高品質背景画像生成
- **翻訳機能**: `gemini-2.5-flash-lite`による日本語→英語プロンプト翻訳
- **3画像同時生成**: 1回のリクエストで3つのバリエーション背景を生成
- **アスペクト比対応**: バナーサイズに応じた最適なアスペクト比（1:1、3:4、4:3、9:16、16:9）
- **自動アップロード**: 生成された全背景をCanvaに自動アップロード


#### **Windows:**
```powershell
# 通常は追加のシステム依存関係は不要
# Visual C++ Redistributableが必要な場合があります
```

### **ステップ1: 環境セットアップ**

#### **🚀 推奨方法: 自動インストールスクリプト**

**Linux/Mac/WSL:**
```bash
# creative_genディレクトリに移動
cd /path/to/creative_gen

# 全ての依存関係を自動インストール（推奨）
cd banner_maker
sudo ./install_all_deps.sh

# sudoなしでも実行可能（一部の機能は制限される場合があります）
./install_all_deps.sh
```

**Windows PowerShell:**
```powershell
# creative_genディレクトリに移動
cd C:\path\to\creative_gen

# PowerShellの実行ポリシーを設定（初回のみ）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 全ての依存関係を自動インストール（推奨）
cd banner_maker
.\install_all_deps.ps1

# 管理者権限で実行する場合（推奨）
# 右クリック → "管理者として実行" でPowerShellを開いてから実行
```

#### **手動インストール方法:**

**Linux/Mac/WSL:**
```bash
# creative_genディレクトリに移動（banner_makerの親ディレクトリ）
cd /path/to/creative_gen  # プロジェクトのルートディレクトリに置き換えてください

# 仮想環境が存在しない場合は作成
if [ ! -d "venv" ]; then
    echo "仮想環境を作成中..."
    python3 -m venv venv
fi

# 仮想環境をアクティベート
source venv/bin/activate

# banner_makerディレクトリに移動して依存関係をインストール
cd banner_maker
pip install -r requirements.txt

# Playwrightブラウザとシステム依存関係をインストール
playwright install chromium
playwright install-deps chromium
```

**Windows PowerShell:**
```powershell
# creative_genディレクトリに移動（banner_makerの親ディレクトリ）
cd C:\path\to\creative_gen  # プロジェクトのルートディレクトリに置き換えてください

# 仮想環境が存在しない場合は作成
if (-not (Test-Path "venv")) {
    Write-Host "仮想環境を作成中..."
    python -m venv venv
}

# 仮想環境をアクティベート
venv\Scripts\Activate.ps1

# banner_makerディレクトリに移動して依存関係をインストール
cd banner_maker
pip install -r requirements.txt

# Playwrightブラウザとシステム依存関係をインストール
playwright install chromium
playwright install-deps chromium
```

### **ステップ2: 環境設定**

`.env.example`と同じ階層に`.env`ファイルを作成:

```bash
# Google Gemini設定
GOOGLE_API_KEY='your-google-gemini-api-key-here'

# Canva OAuth設定（オプション - Canva連携用）
CANVA_CLIENT_ID='your-canva-client-id'
CANVA_CLIENT_SECRET='your-canva-client-secret'
CANVA_REDIRECT_URI='http://localhost:5000/auth/canva/callback'
```

### **ステップ3: アプリケーション開始**

#### **クイックスタート（推奨）:**
```bash
# Linux/Mac/WSL
./start_web_app.sh

# Windows PowerShell
.\start_web_app.ps1
```

#### **手動開始:**
```bash
# creative_genディレクトリから環境をアクティベート
source ../venv/bin/activate  # Linux/Mac/WSL (banner_makerディレクトリから実行)
# ..\venv\Scripts\Activate.ps1  # Windows (banner_makerディレクトリから実行)

# または、creative_genディレクトリから:
# source venv/bin/activate && cd banner_maker  # Linux/Mac/WSL
# venv\Scripts\Activate.ps1 && cd banner_maker  # Windows

# Webサーバーを開始
cd web_app
python run.py
```

**アクセス: http://localhost:5000**

## 🎨 使用方法

### **Web インターフェースワークフロー**

1. **🔗 Canvaに接続**（オプションですが推奨）
   - ヘッダーの「Connect to Canva」をクリック
   - OAuthでアプリケーションを承認

2. **📝 ランディングページURL入力**
   - 商品ページ、ブログ記事、またはランディングページを入力
   - システムが自動でプラットフォームを検出（ヨドバシ、Amazonなど）

3. **🖼️ 画像の抽出＆管理**
   - 「Extract Images」をクリックして高品質画像を検索
   - 抽出エリアからアップロードエリアに画像をドラッグ
   - またはドラッグ&ドロップで独自画像をアップロード

4. **✍️ マーケティングコピー生成**
   - 「Generate Copy」をクリックして5つのAI生成バリエーション
   - お好みのコピースタイルを選択し、必要に応じて編集
   - 各コピーには背景生成プロンプトが含まれます

5. **💡 クリエイティブインサイト取得**（オプション）
   - 「Generate Explanation」をクリックして包括的分析
   - ターゲットオーディエンスインサイト、セールスポイント、クリエイティブ方向性を受領
   - セクションをクリップボードにコピーして参考に

6. **🎨 AI背景生成**（オプション）
   - 「Generate AI Background」をクリックして3つのバリエーション背景を同時生成
   - 日本語プロンプトが自動的に英語に翻訳されて最適な画像品質を実現
   - 生成された3つの背景から好みのものを選択
   - 全背景が自動的にCanvaにアップロード

7. **📤 Canvaに送信**
   - 「Send to Canva」をクリックして全アセットをアップロード
   - 適切な寸法で空白デザインを作成
   - 全画像と背景がCanvaライブラリで利用可能

8. **🎯 Canvaで作成**
   - Canvaで作成されたデザインを開く
   - アップロードされたアセットを使用して最終クリエイティブを構築
   - 生成されたコピーとクリエイティブインサイトを適用

## 🔧 高度な機能

### **アンチボットWebスクレイピング**
- **ハイブリッドアプローチ**: Playwright → Requests フォールバックで最大成功率
- **プラットフォーム最適化**: 主要ECサイト用特別セレクター
- **ステルスモード**: 検知システムを回避する高度な技術
- **エラー回復**: 自動リトライとフォールバック機能

### **プラットフォーム特化サポート可能**
- **✅ ヨドバシカメラ**: 商品ページの完全分析（動作確認済み）
- **⚙️ Amazon**: 商品タイトル・特徴抽出（特化サポート可能）
- **⚙️ 楽天**: 商品詳細・説明（特化サポート可能）
- **⚙️ Shopify**: 一般的な商品ページサポート（特化サポート可能）
- **⚙️ WordPress**: ブログ・記事コンテンツ（特化サポート可能）

### **インテリジェントキャッシング**
- **コンテンツキャッシュ**: 同一URLでの重複スクレイピングを回避
- **コピーキャッシュ**: 生成されたバリエーションをクイックアクセス用に保存
- **セッション管理**: インタラクション間でユーザー状態を維持
- **自動クリーンアップ**: ストレージと一時ファイルを管理

### **ファイル管理システム**
- **スマートアップロード**: 複数フォーマットとサイズを処理
- **抽出統合**: Web画像をシームレスに処理
- **一時処理**: Canvaアップロード後にクリーンアップ
- **エラー回復**: アップロード失敗の堅牢な処理

## 📡 API リファレンス

### **コアエンドポイント**

#### **POST /api/generate-copy**
マーケティングコピーバリエーション生成
```json
{
  "url": "https://example.com/product"
}
```

#### **POST /api/generate-explanation** 
クリエイティブインサイトと戦略生成
```json
{
  "url": "https://example.com/product"
}
```

#### **POST /api/extract-images**
WebページからImage抽出
```json
{
  "url": "https://example.com/product"
}
```

#### **POST /api/generate-background**
AI背景生成（Canva認証必要）- 3画像同時生成
```json
{
  "custom_background_prompt": "プロフェッショナルなマーケティング背景を作成してください",
  "banner_size": "FB_SQUARE"
}
```

#### **POST /api/generate**
アセットをCanvaにアップロード（認証必要）
```json
{
  "url": "https://example.com/product",
  "size": "MD_RECT",
  "variant_idx": 0,
  "product_image_paths": ["/path/to/image.jpg"],
  "background_asset_id": "optional-bg-id"
}
```

### **ファイルアップロードエンドポイント**

#### **POST /api/upload**
商品画像アップロード
```
Content-Type: multipart/form-data
file: 画像ファイル（最大16MB）
```

#### **POST /api/proxy-image**
Web画像ダウンロード・変換
```json
{
  "url": "https://example.com/image.jpg",
  "filename": "product-image"
}
```



### **SaaS商品キャンペーン**
```
入力: https://myapp.com/features/
↓
出力:
- 機能スクリーンショット・モックアップ
- 価値提案を強調するベネフィット重視コピー
- B2Bオーディエンスインサイトとメッセージング戦略
- クリーン、プロフェッショナル背景
- 各種広告プラットフォーム用バナーテンプレート
```

## 🔒 セキュリティ＆プライバシー

### **データ保護**
- **一時処理**: スクレイピングコンテンツは処理後破棄
- **セキュアアップロード**: ファイル検証・サニタイゼーション
- **セッション分離**: セッション別ユーザーデータ分離
- **OAuthセキュリティ**: 適切なスコープによる安全なCanva統合

### **ファイルセキュリティ**
- **タイプ検証**: 許可された画像形式のみ受付
- **サイズ制限**: ファイル1つあたり最大16MB
- **自動クリーンアップ**: 処理後一時ファイル削除
- **パスサニタイゼーション**: ディレクトリトラバーサル攻撃防止

## 📊 パフォーマンス＆コスト

### **生成時間**
- Webスクレイピング: 5-15秒（アンチボット対策含む）
- コピー生成: 10-20秒（5バリエーション）
- クリエイティブインサイト: 15-25秒（包括的分析）
- 背景生成: 20-30秒（高品質AI）
- Canvaアップロード: 5-15秒（ファイル数による）

### **API コスト（推定）**
- **コピー生成**: 約$0.01-0.03 / リクエスト（Gemini 2.5 Flash Lite使用）
- **クリエイティブインサイト**: 約$0.02-0.04 / リクエスト（Gemini 2.5 Flash Lite使用）
- **AI背景生成**: 約$0.06-0.12 / 3画像（Imagen 4.0 Generate Preview使用）
- **翻訳処理**: 約$0.01 / リクエスト（Gemini 2.5 Flash Lite使用）
- **完全ワークフロー合計**: 約$0.10-0.20

#### **Google Gemini AIの利点**
- **高性能・低コスト**: OpenAIと比較して優れたコストパフォーマンス
- **日本語最適化**: 日本語処理に特化した高品質出力
- **最新画像生成**: Imagen 4.0による最先端の画像品質
- **統合プラットフォーム**: テキストと画像生成の統合API

## 🛠️ 技術アーキテクチャ

### **コアコンポーネント**
- **拡張スクレイパー**: `src/enhanced_scraper.py` - 高度Webコンテンツ抽出
- **コピージェネレーター**: `src/copy_gen.py` - AI搭載マーケティングコピー作成
- **インサイトジェネレーター**: `src/explanation_gen.py` - クリエイティブ戦略分析
- **Canva統合**: `src/canva_oauth.py` + `src/simple_canva_upload.py`
- **Webインターフェース**: `web_app/` - Flask ベースユーザーインターフェース

### **主要技術**
- **バックエンド**: Flask、Google Gemini API、Playwright、Requests
- **フロントエンド**: HTML5、JavaScript ES6、TailwindCSS、FontAwesome
- **AI統合**: Gemini 2.5 Flash Lite（テキスト生成）、Imagen 4.0（画像生成）
- **ストレージ**: 自動クリーンアップ付きローカルファイルシステム
- **認証**: Canva統合用OAuth 2.0
- **画像処理**: フォーマット変換用PIL/Pillow



## 🔧 トラブルシューティング

### **よくある問題**

**「スクレイピング失敗」**
- URLがアクセス可能か確認
- プラットフォームがリクエストをブロックしている可能性（システムがフォールバックを試行）
- インターネット接続を確認

**「コピー生成失敗」**
- Google Gemini API キーとクレジットを確認
- API キーがGemini 2.5 Flash Liteアクセス権を持っているか確認
- APIレート制限を確認

**「Canva接続問題」**
- Canva OAuth認証情報を確認
- リダイレクトURI設定を確認
- 適切なスコープがリクエストされているか確認

**「ファイルアップロード問題」**
- ファイルサイズ（16MB制限）を確認
- ファイル形式（PNG、JPG、JPEG、GIF、WebP）を確認
- 十分なディスク容量があるか確認