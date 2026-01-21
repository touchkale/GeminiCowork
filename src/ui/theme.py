# Theme Configuration
"""
Professional Google/Gemini-inspired theme for the application.
Based on Google Material Design 3 with Gemini color accents.
"""

# =============================================================================
# COLOR PALETTE - Google Material Design 3 with Gemini accents
# =============================================================================

COLORS = {
    # Background colors - Deep dark theme
    "bg_primary": "#0F0F0F",           # Main background (Google dark)
    "bg_secondary": "#1A1A1A",         # Cards, panels
    "bg_tertiary": "#242424",          # Elevated surfaces
    "bg_elevated": "#2D2D2D",          # Hover states, dropdowns
    "bg_input": "#1E1E1E",             # Input fields
    
    # Surface colors
    "surface": "#1A1A1A",
    "surface_dim": "#131313",
    "surface_bright": "#2D2D2D",
    "surface_container": "#1E1E1E",
    "surface_container_high": "#282828",
    
    # Text colors
    "text_primary": "#E8EAED",          # Primary text (Google light)
    "text_secondary": "#9AA0A6",        # Secondary text
    "text_tertiary": "#5F6368",         # Muted text
    "text_accent": "#8AB4F8",           # Accent text (Google Blue)
    "text_on_accent": "#0F0F0F",        # Text on accent background
    
    # Gemini gradient colors
    "gemini_blue": "#4285F4",           # Google Blue
    "gemini_purple": "#A855F7",         # Purple accent
    "gemini_pink": "#EC4899",           # Pink accent
    "gemini_cyan": "#22D3EE",           # Cyan accent
    
    # Accent colors
    "accent_primary": "#8AB4F8",        # Light Google Blue
    "accent_secondary": "#A855F7",      # Purple
    "accent_hover": "#AECBFA",          # Lighter blue on hover
    
    # Status colors
    "success": "#34A853",               # Google Green
    "warning": "#FBBC04",               # Google Yellow
    "error": "#EA4335",                 # Google Red
    "info": "#4285F4",                  # Google Blue
    
    # Border colors
    "border": "#3C4043",                # Default border
    "border_subtle": "#2D2D2D",         # Subtle border
    "border_focus": "#8AB4F8",          # Focus state
    
    # Special colors
    "user_bubble": "#1A73E8",           # User message blue
    "ai_bubble": "#1E1E1E",             # AI message dark
    "code_bg": "#1A1A1A",               # Code block background
    "scrollbar": "#5F6368",             # Scrollbar color
    "scrollbar_hover": "#80868B",       # Scrollbar hover
}

# =============================================================================
# TYPOGRAPHY - Google Sans inspired
# =============================================================================

FONTS = {
    "family": "Segoe UI",               # Windows default (similar to Google Sans)
    "family_mono": "Cascadia Code",     # Monospace for code
    "family_display": "Segoe UI",       # Display headings
    
    # Font sizes
    "size_display": 28,                 # Large display text
    "size_heading": 20,                 # Section headings
    "size_title": 16,                   # Card titles
    "size_body": 14,                    # Body text
    "size_small": 12,                   # Small text, captions
    "size_tiny": 11,                    # Very small annotations
    
    # Line heights
    "line_height_tight": 1.2,
    "line_height_normal": 1.5,
    "line_height_relaxed": 1.75,
}

# =============================================================================
# SPACING - Material Design 8dp grid
# =============================================================================

SPACING = {
    "xs": 4,    # 4px
    "sm": 8,    # 8px
    "md": 16,   # 16px
    "lg": 24,   # 24px
    "xl": 32,   # 32px
    "xxl": 48,  # 48px
}

# =============================================================================
# BORDER RADIUS - Rounded corners
# =============================================================================

RADIUS = {
    "xs": 4,    # Small elements
    "sm": 8,    # Buttons, inputs
    "md": 12,   # Cards, panels
    "lg": 16,   # Large cards
    "xl": 24,   # Modal dialogs
    "full": 999, # Fully rounded (pills)
}

# =============================================================================
# SHADOWS (for reference, CTk doesn't support directly)
# =============================================================================

SHADOWS = {
    "sm": "0 1px 2px rgba(0,0,0,0.3)",
    "md": "0 4px 6px rgba(0,0,0,0.4)",
    "lg": "0 10px 15px rgba(0,0,0,0.5)",
    "xl": "0 20px 25px rgba(0,0,0,0.6)",
}

# =============================================================================
# ANIMATIONS
# =============================================================================

ANIMATION = {
    "fast": 150,        # Quick transitions
    "normal": 250,      # Standard transitions
    "slow": 400,        # Slow, deliberate animations
}

# =============================================================================
# WINDOW CONFIGURATION
# =============================================================================

WINDOW = {
    "width": 1400,
    "height": 900,
    "min_width": 1000,
    "min_height": 700,
}

# =============================================================================
# COMPONENT SIZES
# =============================================================================

SIZES = {
    "sidebar_width": 280,
    "sidebar_collapsed": 72,
    "header_height": 56,
    "input_height": 44,
    "button_height": 40,
    "icon_size": 24,
    "avatar_size": 36,
}

# =============================================================================
# ICONS (Unicode symbols for UI elements)
# =============================================================================

ICONS = {
    # Navigation
    "menu": "☰",
    "close": "✕",
    "back": "←",
    "forward": "→",
    "expand": "▼",
    "collapse": "▲",
    
    # Actions
    "add": "+",
    "remove": "−",
    "edit": "✎",
    "delete": "🗑",
    "copy": "📋",
    "paste": "📄",
    "send": "➤",
    "search": "🔍",
    "settings": "⚙",
    "refresh": "↻",
    
    # Status
    "success": "✓",
    "error": "✕",
    "warning": "⚠",
    "info": "ℹ",
    "loading": "◌",
    
    # Files
    "folder": "📁",
    "file": "📄",
    "code": "{ }",
    
    # Other
    "star": "★",
    "chat": "💬",
    "user": "👤",
    "ai": "✦",
    "gemini": "✦",
}

# =============================================================================
# THEME HELPER FUNCTIONS
# =============================================================================

def get_gradient_colors():
    """Return Gemini gradient colors for special effects."""
    return [COLORS["gemini_blue"], COLORS["gemini_purple"], COLORS["gemini_pink"]]

def get_button_style(variant="primary"):
    """Get button style configuration."""
    styles = {
        "primary": {
            "fg_color": COLORS["accent_primary"],
            "hover_color": COLORS["accent_hover"],
            "text_color": COLORS["text_on_accent"],
        },
        "secondary": {
            "fg_color": "transparent",
            "hover_color": COLORS["bg_elevated"],
            "text_color": COLORS["text_primary"],
            "border_color": COLORS["border"],
        },
        "ghost": {
            "fg_color": "transparent",
            "hover_color": COLORS["bg_tertiary"],
            "text_color": COLORS["text_secondary"],
        },
        "danger": {
            "fg_color": COLORS["error"],
            "hover_color": "#D32F2F",
            "text_color": "#FFFFFF",
        },
        "success": {
            "fg_color": COLORS["success"],
            "hover_color": "#2E7D32",
            "text_color": "#FFFFFF",
        },
    }
    return styles.get(variant, styles["primary"])
