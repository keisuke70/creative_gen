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
        
        system_prompt = """You are an expert marketing copywriter. Generate concise, compelling banner copy that drives action. Each variant should be 1-2 short sentences max, suitable for banner overlays."""
        
        # Define copy variants with specific instructions and visual themes
        copy_variants = [
            {
                "type": "benefit",
                "instruction": "Focus on the main benefit or value proposition. What problem does this solve?",
                "tone": "clear and benefit-focused",
                "visual_theme": "clean, modern, professional environment emphasizing quality and reliability"
            },
            {
                "type": "urgency", 
                "instruction": "Create urgency and immediate action. Use time-sensitive language.",
                "tone": "urgent and action-driving",
                "visual_theme": "dynamic, energetic background with motion elements and vibrant colors"
            },
            {
                "type": "promo",
                "instruction": "Highlight deals, offers, or promotional aspects. Make it sales-focused.",
                "tone": "promotional and enticing",
                "visual_theme": "celebratory, eye-catching background with warm lighting and promotional feel"
            }
        ]
        
        results = []
        
        for variant in copy_variants:
            # Generate copy and visual prompt in one call (concise prompt for speed)
            user_prompt = f"""Content: {context}

Create {variant['type']} marketing copy + background prompt:

Copy: {variant['instruction']} | Tone: {variant['tone']} | Max 2 sentences | Banner overlay text

Background: {variant['visual_theme']} atmosphere

Format:
COPY: [copy here]
BACKGROUND: [background here]"""
            
            # Try GPT-4.1-mini first, then fallback to other models (May 2025 models)
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
            
            if response is None:
                print(f"All models failed for {variant['type']}, using fallback copy")
                copy_text = f"Discover {variant['type']} solutions today!"
                background_prompt = variant['visual_theme']
            else:
                response_text = response.choices[0].message.content.strip()
                
                # Parse the response
                copy_text = ""
                background_prompt = ""
                
                lines = response_text.split('\n')
                for line in lines:
                    if line.startswith('COPY:'):
                        copy_text = line.replace('COPY:', '').strip()
                    elif line.startswith('BACKGROUND:'):
                        background_prompt = line.replace('BACKGROUND:', '').strip()
                
                # Fallback if parsing fails
                if not copy_text:
                    copy_text = response_text.split('\n')[0][:100]
                if not background_prompt:
                    background_prompt = variant['visual_theme']
            
            results.append({
                "type": variant["type"],
                "text": copy_text,
                "tone": variant["tone"],
                "char_count": len(copy_text),
                "background_prompt": background_prompt,
                "visual_theme": variant["visual_theme"]
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
            "background_prompt": "clean, modern, professional environment emphasizing quality and reliability",
            "visual_theme": "professional"
        },
        {
            "type": "urgency",
            "text": "Limited time offer. Act now before it's too late!",
            "tone": "urgent",
            "char_count": 0,
            "background_prompt": "dynamic, energetic background with motion elements and vibrant colors",
            "visual_theme": "dynamic"
        },
        {
            "type": "promo", 
            "text": "Special launch pricing. Save big today only.",
            "tone": "promotional",
            "char_count": 0,
            "background_prompt": "celebratory, eye-catching background with warm lighting and promotional feel",
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