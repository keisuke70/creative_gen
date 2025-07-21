#!/usr/bin/env python3
"""
Template specifications for Canva banner sizes and layouts.

This module defines the standard ad sizes and their corresponding layout specifications,
including positioning frames for different elements (background, hero, headline, etc.)
in percentage coordinates for scalable designs.

Safe-zone philosophy: Text should be ≥8pt with ≥20px margins from edges to ensure
readability across different display contexts and devices.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict


@dataclass
class Rect:
    """Rectangle definition in percentage coordinates (0-100)."""
    x_pct: float
    y_pct: float
    w_pct: float
    h_pct: float


@dataclass
class TemplateSpec:
    """Template specification for a specific ad size."""
    template_design_id: str  # Canva template ID (to be filled by devs)
    canvas_w: int
    canvas_h: int
    frames: Dict[str, Rect]  # Element positioning frames


class AdSize(Enum):
    """Standard advertising banner sizes."""
    MD_RECT = "md_rect"           # 300x250 - Medium Rectangle
    LG_RECT = "lg_rect"           # 336x280 - Large Rectangle  
    LEADERBOARD = "leaderboard"   # 728x90 - Leaderboard
    HALF_PAGE = "half_page"       # 300x600 - Half Page
    WIDE_SKYSCRAPER = "wide_skyscraper"  # 160x600 - Wide Skyscraper
    FB_RECT_1 = "fb_rect_1"       # 1200x628 - Facebook Rectangle
    FB_SQUARE = "fb_square"       # 1200x1200 - Facebook Square


# Template specifications with placeholder design IDs
TEMPLATE_MAP: Dict[AdSize, TemplateSpec] = {
    AdSize.MD_RECT: TemplateSpec(
        template_design_id="DAGtxgVmxBM",  # TODO: Paste actual Canva template ID
        canvas_w=300,
        canvas_h=250,
        frames={
            "background": Rect(0, 0, 100, 100),
            "hero": Rect(15, 20, 40, 60),
            "headline": Rect(60, 25, 35, 25),
            "subline": Rect(60, 55, 35, 20),
            "cta": Rect(60, 80, 30, 15)
        }
    ),
    
    AdSize.LG_RECT: TemplateSpec(
        template_design_id="DAGtxsPCibs",  # TODO: Paste actual Canva template ID
        canvas_w=336,
        canvas_h=280,
        frames={
            "background": Rect(0, 0, 100, 100),
            "hero": Rect(15, 18, 42, 64),
            "headline": Rect(62, 22, 33, 28),
            "subline": Rect(62, 52, 33, 22),
            "cta": Rect(62, 78, 32, 16)
        }
    ),
    
    AdSize.LEADERBOARD: TemplateSpec(
        template_design_id="DAGtxjOPpSI",  # TODO: Paste actual Canva template ID
        canvas_w=728,
        canvas_h=90,
        frames={
            "background": Rect(0, 0, 100, 100),
            "hero": Rect(5, 10, 25, 80),
            "headline": Rect(35, 15, 40, 35),
            "subline": Rect(35, 52, 40, 25),
            "cta": Rect(80, 25, 18, 50)
        }
    ),
    
    AdSize.HALF_PAGE: TemplateSpec(
        template_design_id="DAGtxk0xYzQ",  # TODO: Paste actual Canva template ID
        canvas_w=300,
        canvas_h=600,
        frames={
            "background": Rect(0, 0, 100, 100),
            "hero": Rect(10, 15, 80, 40),
            "headline": Rect(10, 60, 80, 15),
            "subline": Rect(10, 77, 80, 12),
            "cta": Rect(25, 92, 50, 6)
        }
    ),
    
    AdSize.WIDE_SKYSCRAPER: TemplateSpec(
        template_design_id="DAGtxuoKnCk",  # TODO: Paste actual Canva template ID
        canvas_w=160,
        canvas_h=600,
        frames={
            "background": Rect(0, 0, 100, 100),
            "hero": Rect(5, 10, 90, 35),
            "headline": Rect(5, 50, 90, 20),
            "subline": Rect(5, 72, 90, 16),
            "cta": Rect(10, 90, 80, 8)
        }
    ),
    
    AdSize.FB_RECT_1: TemplateSpec(
        template_design_id="DAGtxuT604w",  # TODO: Paste actual Canva template ID
        canvas_w=1200,
        canvas_h=628,
        frames={
            "background": Rect(0, 0, 100, 100),
            "hero": Rect(8, 15, 40, 70),
            "headline": Rect(52, 20, 42, 25),
            "subline": Rect(52, 48, 42, 20),
            "cta": Rect(52, 72, 35, 18)
        }
    ),
    
    AdSize.FB_SQUARE: TemplateSpec(
        template_design_id="DAGtxqZWoSk",  # TODO: Paste actual Canva template ID
        canvas_w=1200,
        canvas_h=1200,
        frames={
            "background": Rect(0, 0, 100, 100),
            "hero": Rect(15, 15, 70, 45),
            "headline": Rect(15, 65, 70, 15),
            "subline": Rect(15, 82, 70, 10),
            "cta": Rect(30, 94, 40, 5)
        }
    )
}


def scale_rect(rect: Rect, width: int, height: int) -> tuple[int, int, int, int]:
    """
    Convert percentage-based rectangle to pixel coordinates.
    
    Args:
        rect: Rectangle in percentage coordinates (0-100)
        width: Target canvas width in pixels
        height: Target canvas height in pixels
        
    Returns:
        Tuple of (x, y, width, height) in pixels
    """
    x = int(rect.x_pct * width / 100)
    y = int(rect.y_pct * height / 100) 
    w = int(rect.w_pct * width / 100)
    h = int(rect.h_pct * height / 100)
    
    return (x, y, w, h)