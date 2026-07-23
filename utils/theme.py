"""
Theme configuration for the application UI.
Defines color palettes, fonts, and styling constants for dark and light modes.
"""


class Colors:
    """Professional color palette inspired by premium ERP/fintech applications."""
    
    # ── Dark Mode ──────────────────────────────────────────────────────
    class Dark:
        # Backgrounds
        BG_PRIMARY = "#0f1117"        # Main background — deep dark
        BG_SECONDARY = "#1a1d2e"      # Cards, sidebar
        BG_TERTIARY = "#232738"        # Elevated surfaces
        BG_HOVER = "#2a2e42"           # Hover state
        BG_SELECTED = "#333754"        # Selected/active state
        
        # Accents
        ACCENT_GOLD = "#d4a843"        # Primary accent — gold (jewellery theme)
        ACCENT_GOLD_HOVER = "#e6bc5a"  # Gold hover
        ACCENT_GOLD_DIM = "#8b7230"    # Muted gold
        ACCENT_BLUE = "#4a9eff"        # Secondary accent — links, info
        
        # Text
        TEXT_PRIMARY = "#f0f0f5"       # Main text
        TEXT_SECONDARY = "#9ca3b4"     # Subdued text
        TEXT_MUTED = "#6b7280"         # Very subdued
        TEXT_ON_ACCENT = "#0f1117"     # Text on gold buttons
        
        # Borders
        BORDER = "#2a2e42"             # Default border
        BORDER_LIGHT = "#333754"       # Lighter border
        
        # Status Colors
        SUCCESS = "#34d399"            # Green — positive
        WARNING = "#fbbf24"            # Yellow — warning
        ERROR = "#f87171"              # Red — error/danger
        INFO = "#60a5fa"               # Blue — info
        
        # Table
        TABLE_ROW_ALT = "#1e2233"      # Alternating row
        TABLE_HEADER = "#232738"       # Header background
        TABLE_SELECTED = "#2d3a5c"     # Selected row
        
        # Sidebar
        SIDEBAR_BG = "#0d0f16"         # Sidebar background
        SIDEBAR_ACTIVE = "#1a1d2e"     # Active menu item
        SIDEBAR_HOVER = "#161928"      # Hover menu item
    
    # ── Light Mode ─────────────────────────────────────────────────────
    class Light:
        # Backgrounds
        BG_PRIMARY = "#f8f9fc"         # Main background
        BG_SECONDARY = "#ffffff"       # Cards
        BG_TERTIARY = "#f0f1f5"        # Elevated surfaces
        BG_HOVER = "#e8e9f0"           # Hover state
        BG_SELECTED = "#dde0ec"        # Selected state
        
        # Accents
        ACCENT_GOLD = "#b8922e"        # Primary accent — darker gold for contrast
        ACCENT_GOLD_HOVER = "#d4a843"  # Gold hover
        ACCENT_GOLD_DIM = "#e5d5a0"    # Muted gold
        ACCENT_BLUE = "#2563eb"        # Secondary accent
        
        # Text
        TEXT_PRIMARY = "#1a1d2e"       # Main text
        TEXT_SECONDARY = "#4b5563"     # Subdued text
        TEXT_MUTED = "#9ca3af"         # Very subdued
        TEXT_ON_ACCENT = "#ffffff"     # Text on gold buttons
        
        # Borders
        BORDER = "#e5e7eb"             # Default border
        BORDER_LIGHT = "#f0f1f5"       # Lighter border
        
        # Status Colors
        SUCCESS = "#059669"
        WARNING = "#d97706"
        ERROR = "#dc2626"
        INFO = "#2563eb"
        
        # Table
        TABLE_ROW_ALT = "#f3f4f8"
        TABLE_HEADER = "#e8eaf0"
        TABLE_SELECTED = "#dbeafe"
        
        # Sidebar
        SIDEBAR_BG = "#ffffff"
        SIDEBAR_ACTIVE = "#f0f1f5"
        SIDEBAR_HOVER = "#f8f9fc"


class Fonts:
    """Font configurations. Uses Segoe UI (Windows native) with fallbacks."""
    
    FAMILY = "Segoe UI"
    FAMILY_MONO = "Consolas"
    
    # Sizes
    SIZE_HEADING_XL = 32
    SIZE_HEADING_LG = 26
    SIZE_HEADING = 22
    SIZE_SUBHEADING = 18
    SIZE_BODY = 16
    SIZE_SMALL = 14
    SIZE_TINY = 12
    
    # Weights
    WEIGHT_BOLD = "bold"
    WEIGHT_NORMAL = "normal"
    
    # Presets (family, size, weight)
    HEADING_XL = (FAMILY, SIZE_HEADING_XL, WEIGHT_BOLD)
    HEADING_LG = (FAMILY, SIZE_HEADING_LG, WEIGHT_BOLD)
    HEADING = (FAMILY, SIZE_HEADING, WEIGHT_BOLD)
    SUBHEADING = (FAMILY, SIZE_SUBHEADING, WEIGHT_BOLD)
    BODY = (FAMILY, SIZE_BODY, WEIGHT_NORMAL)
    BODY_BOLD = (FAMILY, SIZE_BODY, WEIGHT_BOLD)
    SMALL = (FAMILY, SIZE_SMALL, WEIGHT_NORMAL)
    SMALL_BOLD = (FAMILY, SIZE_SMALL, WEIGHT_BOLD)
    TINY = (FAMILY, SIZE_TINY, WEIGHT_NORMAL)
    MONO = (FAMILY_MONO, SIZE_BODY, WEIGHT_NORMAL)


class Spacing:
    """Consistent spacing values."""
    
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32
    XXXL = 48
    
    # Padding presets
    CARD_PADDING = 20
    PAGE_PADDING = 24
    FORM_GAP = 12
    SECTION_GAP = 24


class Dimensions:
    """Standard widget dimensions."""
    
    BUTTON_HEIGHT = 38
    BUTTON_WIDTH = 120
    INPUT_HEIGHT = 38
    CORNER_RADIUS = 8
    CARD_CORNER_RADIUS = 12
    STAT_CARD_WIDTH = 200
    STAT_CARD_HEIGHT = 120
    NAV_CARD_WIDTH = 180
    NAV_CARD_HEIGHT = 140
    SIDEBAR_ICON_SIZE = 20


def get_theme(mode: str = "dark"):
    """
    Get the color theme for the specified mode.
    
    Args:
        mode: 'dark' or 'light'
    
    Returns:
        Colors.Dark or Colors.Light class
    """
    if mode == "light":
        return Colors.Light
    return Colors.Dark
