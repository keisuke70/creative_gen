"""
Creative Explanation Generator
AI-powered insights for advertising creative development
"""

import os
from google import genai
from google.genai import types
import re
from typing import Dict, List
from urllib.parse import urlparse


def generate_creative_explanation(text_content: str, title: str, description: str, url: str, llm_extracted_data: Dict = None) -> Dict:
    """
    Generate comprehensive creative explanation using scraped content and LLM extracted data
    
    Args:
        text_content: Full text content from the landing page
        title: Page title
        description: Meta description
        url: Original URL for context
        llm_extracted_data: Rich structured data extracted by LLM
        
    Returns:
        Dictionary containing structured explanation with insights
    """
    
    # Analyze the brand and product from URL
    domain = urlparse(url).netloc.replace('www.', '')
    brand_context = _extract_brand_context(domain, title, text_content)
    
    # Prepare enhanced context using LLM extracted data
    if llm_extracted_data is None:
        llm_extracted_data = {}
    
    # Build rich information for analysis
    info_parts = [
        f"- URL: {url}",
        f"- タイトル: {title}",
        f"- 説明: {description}"
    ]
    
    # Add detailed LLM extracted information
    if llm_extracted_data.get('product_name'):
        info_parts.append(f"- 商品名: {llm_extracted_data['product_name']}")
    
    if llm_extracted_data.get('brand_name'):
        info_parts.append(f"- ブランド名: {llm_extracted_data['brand_name']}")
        
    if llm_extracted_data.get('product_description'):
        info_parts.append(f"- 商品説明: {llm_extracted_data['product_description']}")
        
    if llm_extracted_data.get('category'):
        info_parts.append(f"- カテゴリ: {llm_extracted_data['category']}")
        
    if llm_extracted_data.get('key_features'):
        features = llm_extracted_data['key_features']
        if isinstance(features, list):
            info_parts.append(f"- 主要機能: {', '.join(features)}")
        else:
            info_parts.append(f"- 主要機能: {features}")
            
    if llm_extracted_data.get('unique_selling_points'):
        info_parts.append(f"- 独自の強み: {llm_extracted_data['unique_selling_points']}")
        
    if llm_extracted_data.get('target_audience'):
        info_parts.append(f"- ターゲット層: {llm_extracted_data['target_audience']}")
        
    if llm_extracted_data.get('price_info'):
        info_parts.append(f"- 価格情報: {llm_extracted_data['price_info']}")
        
    if llm_extracted_data.get('call_to_action'):
        info_parts.append(f"- 呼びかけ: {llm_extracted_data['call_to_action']}")
        
    if llm_extracted_data.get('availability'):
        info_parts.append(f"- 利用可能性: {llm_extracted_data['availability']}")
        
    if llm_extracted_data.get('reviews_sentiment'):
        info_parts.append(f"- レビュー傾向: {llm_extracted_data['reviews_sentiment']}")
        
    if llm_extracted_data.get('specifications'):
        specs = llm_extracted_data['specifications']
        if isinstance(specs, dict):
            specs_text = ', '.join([f"{k}: {v}" for k, v in specs.items()])
            info_parts.append(f"- 仕様: {specs_text}")
        else:
            info_parts.append(f"- 仕様: {specs}")
    
    # Fallback to basic content if no LLM data
    if not any(llm_extracted_data.values()):
        info_parts.append(f"- コンテンツ: {text_content[:800]}...")
    
    page_info = "\n".join(info_parts)
    
    # Generate the explanation using Gemini - Japanese prompt to ensure Japanese output
    prompt = f"""以下のランディングページを分析し、広告クリエイティブ制作のインサイトを提供してください。

ページ情報:
{page_info}

以下の構成で分析結果を出力してください:

<h3>商品・サービス概要</h3>
<p>[2文程度で商品・サービスの概要を説明]</p>

<h3>ターゲットオーディエンス</h3>
<ul>
<li>[第1のターゲット層]</li>
<li>[第2のターゲット層]</li>
<li>[第3のターゲット層]</li>
</ul>

<h3>主要セールスポイント</h3>
<ul>
<li>[セールスポイント1]</li>
<li>[セールスポイント2]</li>
<li>[セールスポイント3]</li>
<li>[セールスポイント4]</li>
</ul>

<h3>クリエイティブ方向性</h3>
<ul>
<li>[クリエイティブ方向性1]</li>
<li>[クリエイティブ方向性2]</li>
<li>[クリエイティブ方向性3]</li>
</ul>

<h3>メッセージング戦略</h3>
<ul>
<li>[メッセージング戦略1]</li>
<li>[メッセージング戦略2]</li>
<li>[メッセージング戦略3]</li>
</ul>

<h3>CTA提案</h3>
<ul>
<li>[CTA案1]</li>
<li>[CTA案2]</li>
<li>[CTA案3]</li>
</ul>

上記の構造を厳密に守り、HTMLタグのみで出力してください。"""

    try:
        # Use Gemini client setup
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        client = genai.Client(api_key=api_key)

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="マーケティング専門家として、指定されたHTML構造に従って日本語で分析結果を出力してください。余計な前置きや挨拶は不要です。",
                    temperature=0.7,
                    max_output_tokens=2000
                )
            )
        except Exception as model_error:
            print(f"Gemini API failed: {model_error}")
            response = None
        
        if response is None:
            print("All models failed, using fallback explanation")
            return _generate_fallback_explanation(text_content, title, description, brand_context)
        
        explanation_html = response.text.strip()
        
        # Remove markdown code block markers if present
        if explanation_html.startswith('```html'):
            explanation_html = explanation_html[7:]  # Remove ```html
        if explanation_html.startswith('```'):
            explanation_html = explanation_html[3:]  # Remove ```
        if explanation_html.endswith('```'):
            explanation_html = explanation_html[:-3]  # Remove trailing ```
        
        explanation_html = explanation_html.strip()
        
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
        # Fallback explanation if Gemini fails
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
    """Generate fallback explanation when Gemini is unavailable"""
    
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