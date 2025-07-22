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
        
        system_prompt = """君は最良のコピーライターだ. ユーザーのクリックを引き出す、正確で・競争力のある広告バナー向けコピーを作って欲しい。広告バナー画像に適切にオーバーレイできる2文以下の短いセンテンスを生成すること。"""
        #system_prompt = """You are an expert marketing copywriter. Generate concise, compelling banner copy that drives action. Each variant should be 1-2 short sentences max, suitable for banner overlays."""
        
        # Define copy variants with enhanced background prompt generation
        copy_variants = [
            {
                "type": "benefit",
                "instruction": "Focus on the main benefit or value proposition. What problem does this solve?",
                "tone": "clear and benefit-focused",
                "bg_instruction": "Create a background that visually reinforces trust, quality, and value delivery"
            },
            {
                "type": "urgency", 
                "instruction": "Create urgency and immediate action. Use time-sensitive language.",
                "tone": "urgent and action-driving",
                "bg_instruction": "Create a background with dynamic energy that motivates immediate action"
            },
            {
                "type": "promo",
                "instruction": "Highlight deals, offers, or promotional aspects. Make it sales-focused.",
                "tone": "promotional and enticing",
                "bg_instruction": "Create a background that feels celebratory and highlights special offers"
            },
            {
                "type": "neutral",
                "instruction": "Create straightforward, factual copy without hype. Focus on clear information.",
                "tone": "professional and informative",
                "bg_instruction": "Create a clean, professional background that supports clear communication"
            },
            {
                "type": "playful",
                "instruction": "Use friendly, approachable language that feels personal and engaging.",
                "tone": "friendly and conversational",
                "bg_instruction": "Create a warm, approachable background that feels welcoming and friendly"
            }
        ]
        
        # Single optimized prompt to generate ALL 5 variants in one call
        user_prompt = f"""Analyze this business content and create 5 complete marketing copy variants with matching background prompts:

BUSINESS CONTENT:
- Title: {title}
- Description: {description}
- Page Content: {text_content[:800]}
- Brand Context: {brand_context}

CRITICAL: Each background prompt must be tailored to its specific copy message and the business type. Consider the product/service nature, target audience, and copy tone when creating background descriptions.

TASK: Create ALL 5 variants in one response:

1. BENEFIT variant: Focus on main value proposition. What problem does this solve? (clear and benefit-focused tone)
2. URGENCY variant: Create urgency and immediate action. Use time-sensitive language. (urgent and action-driving tone)
3. PROMO variant: Highlight deals, offers, promotional aspects. Sales-focused. (promotional and enticing tone)
4. NEUTRAL variant: Straightforward, factual copy without hype. Clear information. (professional and informative tone)
5. PLAYFUL variant: Friendly, approachable language that feels personal. (friendly and conversational tone)

REQUIREMENTS FOR EACH:
- Length: 1-2 sentences maximum
- Banner-ready text for overlay
- Include sophisticated background prompt based on business analysis
- Background: 絶対に文字・ロゴ・テキスト・文章・記号を含めない（ABSOLUTELY NO text, logos, words, readable elements）
- Background: 抽象的な大気的要素のみ（gradients, shapes, textures, atmospheric elements only）
- Background: Must complement the specific copy message and tone
- Professional marketing quality

OUTPUT FORMAT (exactly):
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
    base_title = title or "Transform Your Business"
    
    fallback_variants = [
        {
            "type": "benefit",
            "text": f"Discover the power of {base_title.lower()}. Get results fast.",
            "tone": "benefit-focused",
            "char_count": 0,
            "background_prompt": "文字・ロゴ・テキストを一切含まない抽象的なプロフェッショナル背景：柔らかなブルーとグレーのトーンでクリーンでモダンなグラデーション、控えめな幾何学的形状、信頼と品質を強調する純粋に抽象的な要素のみ",
            "visual_theme": "professional"
        },
        {
            "type": "urgency",
            "text": "Limited time offer. Act now before it's too late!",
            "tone": "urgent",
            "char_count": 0,
            "background_prompt": "文字・ロゴ・テキストを一切含まない抽象的な緊急感背景：鮮やかなレッドとオレンジのグラデーションで動的なモーションブラー効果、斜めのエネルギーライン、視覚的緊張感と即座性を生み出す純粋に抽象的な要素のみ",
            "visual_theme": "dynamic"
        },
        {
            "type": "promo", 
            "text": "Special launch pricing. Save big today only.",
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