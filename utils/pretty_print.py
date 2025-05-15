# utils/pretty_print.py

# Color list for each platform
colors = {
    "Codeforces": "#4B8BBE",
    "CodeChef": "#5B8C5A",
    "AtCoder": "#F7A7A6",
}


def get_color(platform: str) -> str:
    """
    Get the color associated with a platform.
    If the platform is not recognized, return a default color.
    """
    return colors.get(platform, "#0d6efd")  # Default to blue if platform not found
