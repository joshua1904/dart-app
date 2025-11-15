from django import template
from django.conf import settings
from django.templatetags.static import static
import os

register = template.Library()


@register.simple_tag
def preact_bundle() -> str:
    """
    Return the static URL to the built Preact bundle in static/assets, without
    hardcoding the hashed filename.
    Prefers files matching 'index-*.js' and falls back to the first '.js' file.
    """
    assets_dir = os.path.join(settings.BASE_DIR, "static", "assets")
    try:
        files = [f for f in os.listdir(assets_dir) if f.endswith(".js")]
    except FileNotFoundError:
        return ""

    if not files:
        return ""

    index_candidates = [f for f in files if f.startswith("index-") and f.endswith(".js")]
    chosen = index_candidates[0] if index_candidates else files[0]
    return static(f"assets/{chosen}")


