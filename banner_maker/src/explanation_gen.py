"""
Creative Explanation Generator
AI-powered insights for advertising creative development
"""

import os
import openai
import re
from typing import Dict, List
from urllib.parse import urlparse


def generate_creative_explanation(text_content: str, title: str, description: str, url: str) -> Dict:
    """
    Generate comprehensive creative explanation using scraped content
    
    Args:
        text_content: Full text content from the landing page
        title: Page title
        description: Meta description
        url: Original URL for context
        
    Returns:
        Dictionary containing structured explanation with insights
    """
    
    # Analyze the brand and product from URL
    domain = urlparse(url).netloc.replace('www.', '')
    brand_context = _extract_brand_context(domain, title, text_content)
    
    # Generate the explanation using OpenAI - Japanese prompt for better efficiency
    prompt = f"""このランディングページのコンテンツを分析し、効果的な広告クリエイティブ制作のためのインサイトを提供してください。

ページ情報:
- URL: {url}
- タイトル: {title}
- 説明: {description}
- コンテンツ: {text_content[:800]}...

以下の構成で分析結果を提供してください:

1. **商品・サービス概要** (2文程度)
2. **ターゲットオーディエンス** (3つのポイント)
3. **主要セールスポイント** (3-4つのポイント)
4. **クリエイティブ方向性** (3つのポイント)
5. **メッセージング戦略** (2-3つのポイント)
6. **CTA提案** (2-3つの選択肢)

HTMLフォーマットで出力し、<h3>でセクション見出し、<ul><li>でポイント、<p>で段落を使用してください。実用的で実行可能な内容にしてください。"""

    try:
        # Use same client setup as copy_gen.py
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        models_to_try = ["gpt-4.1-mini", "gpt-4.1", "gpt-4.1-nano", "gpt-4o-mini"]
        
        response = None
        for model in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "あなたは広告心理学と消費者行動に詳しいマーケティング戦略家です。"},
                        {"role": "user", "content": prompt}
                    ],
                )
                break
            except Exception as model_error:
                print(f"Model {model} failed: {model_error}")
                continue
        
        if response is None:
            print("All models failed, using fallback explanation")
            return _generate_fallback_explanation(text_content, title, description, brand_context)
        
        explanation_html = response.choices[0].message.content.strip()
        
        # Extract key metrics and insights for structured data
        insights = _extract_key_insights(text_content, explanation_html)
        
        return {
            'html_content': explanation_html,
            'insights': insights,
            'brand_context': brand_context,
            'target_audience': _extract_target_audience(explanation_html),
            'key_messages': _extract_key_messages(explanation_html),
            'creative_direction': _extract_creative_direction(explanation_html)
        }
        
    except Exception as e:
        print(f"Explanation generation failed: {e}")
        # Fallback explanation if OpenAI fails
        return _generate_fallback_explanation(text_content, title, description, brand_context)


def _extract_brand_context(domain: str, title: str, content: str) -> str:
    """Extract brand context from domain and content"""
    
    # Common brand patterns
    brand_indicators = {
        'ecommerce': ['shop', 'store', 'buy', 'product', 'cart', 'checkout'],
        'saas': ['software', 'app', 'platform', 'tool', 'service'],
        'education': ['course', 'learn', 'training', 'education', 'teach'],
        'healthcare': ['health', 'medical', 'clinic', 'doctor', 'treatment'],
        'finance': ['finance', 'bank', 'investment', 'loan', 'insurance'],
        'food': ['restaurant', 'food', 'recipe', 'delivery', 'cuisine'],
        'travel': ['travel', 'hotel', 'booking', 'vacation', 'trip']
    }
    
    content_lower = content.lower()
    title_lower = title.lower()
    
    # Identify brand category
    category_scores = {}
    for category, keywords in brand_indicators.items():
        score = sum(1 for keyword in keywords if keyword in content_lower or keyword in title_lower)
        if score > 0:
            category_scores[category] = score
    
    primary_category = max(category_scores, key=category_scores.get) if category_scores else 'general'
    
    return f"{domain} ({primary_category.title()})"


def _extract_key_insights(content: str, explanation_html: str) -> Dict:
    """Extract structured insights from content and explanation"""
    
    insights = {
        'content_length': len(content),
        'word_count': len(content.split()),
        'has_pricing': bool(re.search(r'[\$¥€£]\s*\d+|price|pricing|cost', content.lower())),
        'has_testimonials': bool(re.search(r'review|testimonial|customer|rating', content.lower())),
        'has_urgency': bool(re.search(r'limited|exclusive|sale|discount|offer', content.lower())),
        'has_social_proof': bool(re.search(r'thousand|million|popular|best|award', content.lower()))
    }
    
    return insights


def _extract_target_audience(explanation_html: str) -> List[str]:
    """Extract target audience insights from explanation"""
    
    # Simple extraction - in practice, you'd use more sophisticated NLP
    audience_section = re.search(r'Target Audience.*?(?=<h3>|$)', explanation_html, re.DOTALL | re.IGNORECASE)
    if audience_section:
        # Extract bullet points
        bullets = re.findall(r'<li>(.*?)</li>', audience_section.group(0))
        return [re.sub(r'<[^>]+>', '', bullet).strip() for bullet in bullets[:3]]
    
    return []


def _extract_key_messages(explanation_html: str) -> List[str]:
    """Extract key messaging points from explanation"""
    
    messaging_section = re.search(r'Messaging.*?(?=<h3>|$)', explanation_html, re.DOTALL | re.IGNORECASE)
    if messaging_section:
        bullets = re.findall(r'<li>(.*?)</li>', messaging_section.group(0))
        return [re.sub(r'<[^>]+>', '', bullet).strip() for bullet in bullets[:3]]
    
    return []


def _extract_creative_direction(explanation_html: str) -> List[str]:
    """Extract creative direction points from explanation"""
    
    creative_section = re.search(r'Creative Direction.*?(?=<h3>|$)', explanation_html, re.DOTALL | re.IGNORECASE)
    if creative_section:
        bullets = re.findall(r'<li>(.*?)</li>', creative_section.group(0))
        return [re.sub(r'<[^>]+>', '', bullet).strip() for bullet in bullets[:3]]
    
    return []


def _generate_fallback_explanation(text_content: str, title: str, description: str, brand_context: str) -> Dict:
    """Generate fallback explanation when OpenAI is unavailable"""
    
    # Analyze content for basic insights
    has_pricing = bool(re.search(r'[\$¥€£]\s*\d+|price|pricing|cost', text_content.lower()))
    has_testimonials = bool(re.search(r'review|testimonial|customer|rating', text_content.lower()))
    
    html_content = f"""
    <h3>商品・サービス概要</h3>
    <p>ページタイトル「{title}」に基づくと、{description or 'お客様に価値を提供する'}サービスのようです。</p>
    
    <h3>主要インサイト</h3>
    <ul>
        <li>コンテンツ量: {len(text_content)}文字で{'詳細な' if len(text_content) > 1000 else '簡潔な'}情報提供</li>
        <li>{'価格情報あり - 具体的な価値を強調' if has_pricing else '価格より価値提案を重視'}</li>
        <li>{'顧客の声あり - 社会的証明を活用' if has_testimonials else '社会的証明要素の追加を検討'}</li>
        <li>ブランド特性: {brand_context}</li>
    </ul>
    
    <h3>クリエイティブ推奨事項</h3>
    <ul>
        <li>タイトルから主要価値提案を強調</li>
        <li>ブランドトーンに合うクリーンでプロフェッショナルなデザイン</li>
        <li>ページ内容に基づく明確なコール・トゥ・アクション</li>
        <li>コンテンツスタイルから想定されるターゲット層への配慮</li>
    </ul>
    """
    
    return {
        'html_content': html_content,
        'insights': _extract_key_insights(text_content, html_content),
        'brand_context': brand_context,
        'target_audience': ['ページコンテンツに基づく一般的なオーディエンス'],
        'key_messages': ['価値重視のメッセージング', 'プロフェッショナルなトーン'],
        'creative_direction': ['クリーンなデザイン', '明確なCTA', 'ブランドに適したビジュアル']
    }