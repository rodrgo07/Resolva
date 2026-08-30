import re
import html
from typing import Optional

def sanitize_html_content(raw_html: Optional[str]) -> str:
    """
    Sanitiza HTML removendo tags executaveis (<script>, <iframe>, <object>, <embed>, <applet>),
    atributos inline de javascript (onload, onclick, on*), estilos perigosos e esquemas javascript:.
    """
    if not raw_html:
        return ""

    content = raw_html

    # Remove tags perigosas
    dangerous_tags = ["script", "iframe", "object", "embed", "applet", "form", "meta", "base", "link"]
    for tag in dangerous_tags:
        pattern = re.compile(rf"<\s*{tag}\b[^>]*>.*?<\s*/\s*{tag}\s*>", re.IGNORECASE | re.DOTALL)
        content = pattern.sub("", content)
        self_closing = re.compile(rf"<\s*{tag}\b[^>]*/>", re.IGNORECASE)
        content = self_closing.sub("", content)

    # Remove manipuladores on* inline (ex: onload, onerror, onclick)
    event_handler_pattern = re.compile(r'\s*on\w+\s*=\s*(["\'][^"\']*["\']|[^\s>]+)', re.IGNORECASE)
    content = event_handler_pattern.sub("", content)

    # Remove javascript: e data: urls
    js_url_pattern = re.compile(r'(href|src)\s*=\s*(["\'])(?:javascript|data):.*?\2', re.IGNORECASE)
    content = js_url_pattern.sub(r'\1="#"', content)

    return content

def html_to_plain_text(raw_html: Optional[str]) -> str:
    """Converte HTML em texto puro legivel para resumos e IA"""
    if not raw_html:
        return ""
    
    # Remove tags com regex
    clean = re.sub(r"<style.*?>.*?</style>", "", raw_html, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r"<script.*?>.*?</script>", "", clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r"<[^>]+>", " ", clean)
    clean = html.unescape(clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean
