import os
from typing import List, Dict
import openai
import asyncio


def setup_openai_client() -> openai.OpenAI:
    """
    Initialize OpenAI client for copy generation
    """
    return openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def generate_copy_and_visual_prompts(
    text_content: str,
    title: str = "",
    description: str = "",
    brand_context: str = ""
) -> List[Dict]:
    """
    Generate 5 marketing copy variants with corresponding visual/background prompts using GPT-4.1
    Variants: benefit, urgency, promo, neutral, playful
    """
    try:
        client = setup_openai_client()
        
        # Prepare context for copy generation
        context = f"""
        Website Title: {title}
        Description: {description}
        Page Content: {text_content[:800]}
        Brand Context: {brand_context}
        """.strip()
        
        system_prompt = """君は日本のトップクラスのコピーライターだ。必ず日本語で、ユーザーのクリックを引き出す正確で競争力のある広告バナー向けコピーを作成すること。広告バナー画像に適切にオーバーレイできる2文以下の短い日本語センテンスを生成すること。出力は必ず日本語のみで行う。"""
        
        # Define copy variants with enhanced background prompt generation
        copy_variants = [
            {
                "type": "benefit",
                "instruction": "主要なベネフィットや価値提案に焦点を当てる。どんな問題を解決するか？",
                "tone": "明確でベネフィット重視",
                "bg_instruction": "信頼性、品質、価値提供を視覚的に補強する背景を作成"
            },
            {
                "type": "urgency", 
                "instruction": "緊急性と即座のアクションを作り出す。時間限定の言葉を使用する。",
                "tone": "緊急性があり行動を促す",
                "bg_instruction": "即座のアクションを促すダイナミックなエネルギーを持つ背景を作成"
            },
            {
                "type": "promo",
                "instruction": "お得情報、オファー、プロモーション要素をハイライト。セールス重視にする。",
                "tone": "プロモーション的で魅力的",
                "bg_instruction": "特別オファーをハイライトし、お祝い感のある背景を作成"
            },
            {
                "type": "neutral",
                "instruction": "誇張なしに、事実に基づく分かりやすいコピーを作成。明確な情報に焦点を当てる。",
                "tone": "プロフェッショナルで情報的",
                "bg_instruction": "明確なコミュニケーションをサポートする、クリーンでプロフェッショナルな背景を作成"
            },
            {
                "type": "playful",
                "instruction": "親しみやすく、個人的で魅力的なフレンドリーな言葉を使用する。",
                "tone": "親しみやすく会話的",
                "bg_instruction": "温かく親しみやすい、歓迎する印象を与える背景を作成"
            }
        ]
        
        # Single optimized prompt to generate ALL 5 variants in one call
        user_prompt = f"""このビジネスコンテンツを分析し、マッチングする背景プロンプトと合わせて5つの完全なマーケティングコピーバリエーションを日本語で作成してください：

ビジネスコンテンツ:
- タイトル: {title}
- 説明: {description}
- ページコンテンツ: {text_content[:800]}
- ブランドコンテキスト: {brand_context}

重要: 各背景プロンプトは、その特定のコピーメッセージとビジネスタイプに合わせてカスタマイズしてください。商品・サービスの性質、ターゲットオーディエンス、コピーのトーンを考慮して背景の説明を作成してください。

タスク: すべての5つのバリエーションを1つの回答で作成：

1. BENEFIT バリエーション: 主要価値提案に焦点。どんな問題を解決するか？（明確でベネフィット重視のトーン）
2. URGENCY バリエーション: 緊急性と即座のアクションを作成。時間限定の言葉を使用。（緊急性があり行動を促すトーン）
3. PROMO バリエーション: お得情報、オファー、プロモーション要素をハイライト。セールス重視。（プロモーション的で魅力的なトーン）
4. NEUTRAL バリエーション: 誇張なしに事実に基づく分かりやすいコピー。明確な情報。（プロフェッショナルで情報的なトーン）
5. PLAYFUL バリエーション: 親しみやすく個人的な印象のフレンドリーな言葉。（親しみやすく会話的なトーン）

各バリエーションの要件:
- 長さ: 最大1-2文
- バナーオーバーレイ用のテキスト
- ビジネス分析に基づく洗練された背景プロンプトを含める
- 背景: 絶対に文字・ロゴ・テキスト・文章・記号を含めない（ABSOLUTELY NO text, logos, words, readable elements）
- 背景: 抽象的な大気的要素のみ（gradients, shapes, textures, atmospheric elements only）
- 背景: 特定のコピーメッセージとトーンを補完する必要がある
- プロフェッショナルマーケティング品質
- すべて日本語で出力

出力フォーマット（正確に）:
BENEFIT:
COPY: [benefit copy here]
BACKGROUND: 文字・ロゴ・テキストを一切含まない抽象的なマーケティングバナー背景を作成：[この特定のベネフィットコピーに合う色彩・雰囲気・ムードを詳しく描写、ビジネスタイプに合うビジュアルスタイル、純粋に抽象的な要素のみ]

URGENCY:
COPY: [urgency copy here] 
BACKGROUND: 文字・ロゴ・テキストを一切含まない抽象的なマーケティングバナー背景を作成：[この特定の緊急性コピーに合うダイナミックな色彩・エネルギー・緊急感のある雰囲気を詳しく描写、視覚的緊張感、純粋に抽象的な要素のみ]

PROMO:
COPY: [promo copy here]
BACKGROUND: 文字・ロゴ・テキストを一切含まない抽象的なマーケティングバナー背景を作成：[この特定のプロモーションコピーを強化する祝祭的な色彩・プロモーション雰囲気を詳しく描写、視覚的興奮感、純粋に抽象的な要素のみ]

NEUTRAL:
COPY: [neutral copy here]
BACKGROUND: 文字・ロゴ・テキストを一切含まない抽象的なマーケティングバナー背景を作成：[この特定の情報的コピーをサポートするクリーンでプロフェッショナルな雰囲気を詳しく描写、ミニマルな視覚要素、純粋に抽象的な要素のみ]

PLAYFUL:
COPY: [playful copy here]
BACKGROUND: 文字・ロゴ・テキストを一切含まない抽象的なマーケティングバナー背景を作成：[この特定のフレンドリーなコピーに合う温かく親しみやすい雰囲気を詳しく描写、親しみやすいビジュアルスタイル、純粋に抽象的な要素のみ]"""
        
        # Single LLM call instead of loop
        models_to_try = ["gpt-4.1-mini", "gpt-4.1", "gpt-4.1-nano", "gpt-4o-mini"]
        
        response = None
        for model in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                )
                print(f"Copy generation successful with model: {model}")
                break
            except Exception as model_error:
                print(f"Model {model} failed: {model_error}")
                continue
        
        results = []
        
        if response is None:
            print("All models failed, using fallback copy")
            return generate_fallback_copy_with_prompts(text_content, title)
        
        # Parse the single response containing all 5 variants
        response_text = response.choices[0].message.content.strip()
        
        # Parse all variants from single response
        for variant in copy_variants:
            variant_type = variant["type"].upper()
            
            # Extract copy and background for this variant
            copy_text = ""
            background_prompt = ""
            
            # Find the section for this variant
            lines = response_text.split('\n')
            in_variant_section = False
            
            for line in lines:
                if line.startswith(f'{variant_type}:'):
                    in_variant_section = True
                    continue
                elif any(line.startswith(f'{other["type"].upper()}:') for other in copy_variants if other != variant):
                    in_variant_section = False
                    continue
                    
                if in_variant_section:
                    if line.startswith('COPY:'):
                        copy_text = line.replace('COPY:', '').strip()
                    elif line.startswith('BACKGROUND:'):
                        background_prompt = line.replace('BACKGROUND:', '').strip()
            
            # Fallback if parsing fails for this variant
            if not copy_text:
                copy_text = f"Discover {variant['type']} solutions today!"
            if not background_prompt:
                background_prompt = f"文字・ロゴ・テキストを一切含まない抽象的な{variant['type']}マーケティング背景：{variant['tone']}メッセージトーンに合うプロフェッショナルな大気デザイン、純粋に抽象的な要素のみ"
            
            results.append({
                "type": variant["type"],
                "text": copy_text,
                "tone": variant["tone"],
                "char_count": len(copy_text),
                "background_prompt": background_prompt,
            })
        
        return results
        
    except Exception as e:
        # Fallback copy variants if API fails
        return generate_fallback_copy_with_prompts(text_content, title)


def generate_fallback_copy_with_prompts(text_content: str, title: str = "") -> List[Dict]:
    """
    Generate basic fallback copy variants with background prompts when API is unavailable
    """
    base_title = title or "あなたのビジネスを変革"
    
    fallback_variants = [
        {
            "type": "benefit",
            "text": f"{base_title}の力を発見しよう。素早く結果を実感。",
            "tone": "benefit-focused",
            "char_count": 0,
            "background_prompt": "文字・ロゴ・テキストを一切含まない抽象的なプロフェッショナル背景：柔らかなブルーとグレーのトーンでクリーンでモダンなグラデーション、控えめな幾何学的形状、信頼と品質を強調する純粋に抽象的な要素のみ",
            "visual_theme": "professional"
        },
        {
            "type": "urgency",
            "text": "期間限定オファー。手遅れになる前に今すぐ行動！",
            "tone": "urgent",
            "char_count": 0,
            "background_prompt": "文字・ロゴ・テキストを一切含まない抽象的な緊急感背景：鮮やかなレッドとオレンジのグラデーションで動的なモーションブラー効果、斜めのエネルギーライン、視覚的緊張感と即座性を生み出す純粋に抽象的な要素のみ",
            "visual_theme": "dynamic"
        },
        {
            "type": "promo", 
            "text": "特別ローンチ価格。今日だけの大特価。",
            "tone": "promotional",
            "char_count": 0,
            "background_prompt": "文字・ロゴ・テキストを一切含まない抽象的なプロモーション背景：ゴールデンイエローと温かいオレンジでお祝いのバーストパターン、放射状の光効果、スパークル要素で祝祭的な雰囲気の純粋に抽象的な要素のみ",
            "visual_theme": "celebratory"
        }
    ]
    
    # Update character counts
    for variant in fallback_variants:
        variant["char_count"] = len(variant["text"])
    
    return fallback_variants


def generate_fallback_copy(text_content: str, title: str = "") -> List[Dict]:
    """
    Legacy function for backward compatibility - redirects to new function
    """
    variants = generate_fallback_copy_with_prompts(text_content, title)
    # Remove background prompts for legacy compatibility
    for variant in variants:
        variant.pop('background_prompt', None)
        variant.pop('visual_theme', None)
    return variants


def optimize_copy_for_banner(copy_text: str, max_chars: int = 60) -> str:
    """
    Optimize copy length for banner display
    """
    if len(copy_text) <= max_chars:
        return copy_text
    
    # Try to truncate at sentence boundary
    sentences = copy_text.split('. ')
    if len(sentences) > 1 and len(sentences[0]) <= max_chars:
        return sentences[0] + '.'
    
    # Truncate with ellipsis
    return copy_text[:max_chars-3] + '...'


async def generate_copy_async(
    text_content: str,
    title: str = "",
    description: str = ""
) -> List[Dict]:
    """
    Async wrapper for copy generation
    """
    return await asyncio.get_event_loop().run_in_executor(
        None, generate_copy_variants, text_content, title, description
    )


def select_best_copy_for_banner(variants: List[Dict], max_chars: int = 50, manual_selection: bool = False) -> Dict:
    """
    Select the best copy variant for banner use based on length and impact
    If manual_selection is True, returns all variants for user selection
    """
    # Filter by character limit
    suitable_variants = [v for v in variants if v['char_count'] <= max_chars]
    
    if not suitable_variants:
        # Use shortest variant and truncate
        for variant in variants:
            variant['text'] = optimize_copy_for_banner(variant['text'], max_chars)
            variant['char_count'] = len(variant['text'])
        suitable_variants = variants
    
    # If manual selection is requested, return all suitable variants
    if manual_selection:
        return {"mode": "manual", "variants": suitable_variants}
    
    # Auto-select: Prefer benefit, urgency, promo in that order
    priority_types = ['benefit', 'urgency', 'promo']
    
    for ptype in priority_types:
        matching = [v for v in suitable_variants if v['type'] == ptype]
        if matching:
            return matching[0]
    
    # Return first suitable variant
    return suitable_variants[0]