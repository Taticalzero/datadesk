"""
app/templates.py
Workaround para bug do cache do Jinja2 no Python 3.14.
Renderiza templates diretamente via Jinja2, sem Jinja2Templates do Starlette.
"""
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.responses import HTMLResponse


class _NullCache:
    """Cache no-op: corrige TypeError 'unhashable type: dict' no Python 3.14."""
    def get(self, key):              return None
    def __contains__(self, key):    return False
    def __setitem__(self, key, v):  pass
    def __getitem__(self, key):     raise KeyError(key)
    def setdefault(self, key, v=None): return v


_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html"]),
    auto_reload=True,
)
_env.cache = _NullCache()


def render(name: str, context: dict) -> HTMLResponse:
    """Renderiza um template e retorna HTMLResponse."""
    html = _env.get_template(name).render(**context)
    return HTMLResponse(html)
