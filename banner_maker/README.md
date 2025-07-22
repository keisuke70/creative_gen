# AI Banner Maker - クリエイティブアセット管理プラットフォーム

AI搭載のコンテンツ分析、画像抽出、コピー生成、Canva連携によるマーケティングアセット作成のためのプロフェッショナルWebアプリケーション。

## 🎯 機能概要

**入力**: ランディングページURL → **出力**: Canvaで使用可能な整理されたクリエイティブアセット

**例**: `https://www.yodobashi.com/product/12345/` → 抽出画像、AI生成マーケティングコピー、クリエイティブインサイト、適切な寸法のCanva空白デザイン

## 🚀 主要機能

### **🔍 高度なWeb分析**
- **強化されたスクレイピング** - プラットフォーム特化セレクターで2-10倍のコンテンツ抽出
- **アンチボット保護** - Playwright + Requests ハイブリッドフォールバックシステムで検知を回避
- **プラットフォーム最適化** - ヨドバシ、Amazon、楽天、Shopify、WordPressを特別サポート
- **動的コンテンツ対応** - JavaScript、無限スクロール、遅延読み込みに対応

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

### **🎨 オプショナルAI背景生成**
- **コンテキスト認識** - 選択したコピーとブランドにマッチした背景を生成
- **テキストフリーデザイン** - オーバーレイテキストに最適な純粋な抽象背景
- **プロフェッショナル品質** - 適切なムードとスタイルのマーケティング対応背景

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
- OpenAI API キー（GPT-4.1およびDALL-Eアクセス）
- Canva開発者アカウント（OAuth連携用）

### **ステップ1: 環境セットアップ**

#### **Linux/Mac/WSL:**
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
playwright install chromium
```

#### **Windows PowerShell:**
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
playwright install chromium
```

#### **シンプルなステップバイステップ（初回セットアップ）:**
```bash
# 1. プロジェクトディレクトリに移動
cd /path/to/creative_gen

# 2. 仮想環境を作成（初回のみ）
python3 -m venv venv  # Linux/Mac/WSL
# python -m venv venv  # Windows

# 3. 仮想環境をアクティベート
source venv/bin/activate  # Linux/Mac/WSL
# venv\Scripts\Activate.ps1  # Windows

# 4. banner_makerに移動して依存関係インストール
cd banner_maker
pip install -r requirements.txt
playwright install chromium
```

### **ステップ2: 環境設定**

`banner_maker`ディレクトリに`.env`ファイルを作成:

```bash
# OpenAI設定
OPENAI_API_KEY='sk-proj-your-openai-key-here'

# Canva OAuth設定（オプション - Canva連携用）
CANVA_CLIENT_ID='your-canva-client-id'
CANVA_CLIENT_SECRET='your-canva-client-secret'
CANVA_REDIRECT_URI='http://localhost:5000/auth/canva/callback'

# アプリケーション設定
FLASK_ENV=development
PORT=5000
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
   - 「Generate AI Background」をクリックしてマッチング背景を作成
   - 選択したコピーとブランドコンテキストに合わせたプロンプトを使用

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

### **プラットフォーム特化サポート**
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
AI背景生成（Canva認証必要）
```json
{
  "url": "https://example.com/product",
  "selected_copy": {...},
  "custom_background_prompt": "..."
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

## 🎯 使用例

### **Eコマース商品マーケティング**
```
入力: https://www.yodobashi.com/product/100000001005807664/
↓
出力: 
- 商品画像を抽出・最適化
- 5つのマーケティングコピーバリエーション（ベネフィット、緊急性、プロモなど）
- ターゲットオーディエンス分析とセールスポイント
- 商品カテゴリにマッチしたAI背景
- 全アセット付きのCanvaデザイン
```

### **ブログコンテンツプロモーション**
```
入力: https://myblog.com/10-productivity-tips/
↓
出力:
- 記事画像・グラフィック抽出
- ソーシャルメディアコピーバリエーション
- コンテンツマーケティング戦略インサイト
- 引用カード用プロフェッショナル背景
- 複数ソーシャル形式のCanvaテンプレート
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
- コピー生成: 約$0.02-0.05 / リクエスト（GPT-4.1 mini）
- クリエイティブインサイト: 約$0.03-0.07 / リクエスト（GPT-4.1 mini）
- 背景生成: 約$0.04-0.08 / 画像（DALL-E）
- **完全ワークフロー合計**: 約$0.09-0.20

## 🛠️ 技術アーキテクチャ

### **コアコンポーネント**
- **拡張スクレイパー**: `src/enhanced_scraper.py` - 高度Webコンテンツ抽出
- **コピージェネレーター**: `src/copy_gen.py` - AI搭載マーケティングコピー作成
- **インサイトジェネレーター**: `src/explanation_gen.py` - クリエイティブ戦略分析
- **Canva統合**: `src/canva_oauth.py` + `src/simple_canva_upload.py`
- **Webインターフェース**: `web_app/` - Flask ベースユーザーインターフェース

### **主要技術**
- **バックエンド**: Flask、OpenAI API、Playwright、Requests
- **フロントエンド**: HTML5、JavaScript ES6、TailwindCSS、FontAwesome
- **ストレージ**: 自動クリーンアップ付きローカルファイルシステム
- **認証**: Canva統合用OAuth 2.0
- **画像処理**: フォーマット変換用PIL/Pillow

### **データフロー**
```
URL入力 → スクレイピング（Playwright/Requests） → コンテンツ分析 → 
AI処理（コピー/インサイト/背景） → Canvaアップロード → 
ユーザーインターフェース更新 → アセット管理
```

## 🔧 トラブルシューティング

### **よくある問題**

**「スクレイピング失敗」**
- URLがアクセス可能か確認
- プラットフォームがリクエストをブロックしている可能性（システムがフォールバックを試行）
- インターネット接続を確認

**「コピー生成失敗」**
- OpenAI API キーとクレジットを確認
- API キーがGPT-4.1アクセス権を持っているか確認
- APIレート制限を確認

**「Canva接続問題」**
- Canva OAuth認証情報を確認
- リダイレクトURI設定を確認
- 適切なスコープがリクエストされているか確認

**「ファイルアップロード問題」**
- ファイルサイズ（16MB制限）を確認
- ファイル形式（PNG、JPG、JPEG、GIF、WebP）を確認
- 十分なディスク容量があるか確認

### **デバッグモード**
```bash
# 詳細ログを有効化
export FLASK_DEBUG=1
export FLASK_ENV=development
python run.py
```

## 📈 ロードマップ＆今後の機能

### **予定されている機能強化**
- **🔮 より多くのAIモデル**: 追加画像生成モデルのサポート
- **📱 モバイル最適化**: レスポンシブデザイン改善
- **🎨 スタイル転送**: 生成背景にブランドスタイルを適用
- **📊 分析ダッシュボード**: 使用量と生成成功率の追跡
- **🔄 バッチ処理**: 複数URLの同時処理
- **🎯 A/Bテスト**: テスト用複数クリエイティブバリエーション生成

### **統合拡張**
- **Adobe Creative Suite**: Photoshop/Illustratorへのエクスポート
- **Figma統合**: Figmaへの直接アセットエクスポート
- **ソーシャルメディアAPI**: プラットフォームへの直接投稿
- **CRM統合**: マーケティング自動化ツールとの連携

## 🆘 サポート＆ドキュメント

### **ヘルプの取得**
1. セットアップと使用方法についてはこのREADMEを確認
2. 上記のトラブルシューティングセクションを確認
3. エンドポイント詳細についてはAPIドキュメントを確認
4. すべての依存関係と認証情報が適切に設定されているか確認

### **ファイル構造リファレンス**
```
banner_maker/
├── .env                      # 環境設定
├── requirements.txt          # Python 依存関係
├── start_web_app.sh         # Linux/Mac 起動スクリプト
├── start_web_app.ps1        # Windows 起動スクリプト
├── src/                     # コア機能
│   ├── enhanced_scraper.py  # 高度Webスクレイピング
│   ├── copy_gen.py          # AIコピー生成
│   ├── explanation_gen.py   # クリエイティブインサイト
│   ├── canva_oauth.py       # Canva認証
│   └── simple_canva_upload.py # アセットアップロード
├── web_app/                 # Webインターフェース
│   ├── app.py               # Flaskアプリケーション
│   ├── run.py               # 開発サーバー
│   ├── templates/index.html # メインインターフェース
│   ├── static/js/app.js     # フロントエンドロジック
│   └── uploads/             # 一時ファイルストレージ
└── documentation/           # 追加ドキュメント
    ├── scraper_improvements_ja.md
    └── ファイルアップロード機能.md
```

---

**プロフェッショナルなマーケティングアセットを作成する準備はできましたか？** 🚀

**セットアップ時間**: 5-10分  
**初回クリエイティブ**: 2-3分で準備完了  
**最適用途**: Eコマース、SaaS、コンテンツマーケティング、ソーシャルメディアキャンペーン

`./start_web_app.sh`（Linux/Mac）または`.\start_web_app.ps1`（Windows）を実行してhttp://localhost:5000を開いて始めましょう！