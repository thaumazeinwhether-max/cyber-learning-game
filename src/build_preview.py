"""プレビューHTMLを再構築する。利用者のJSや外部URLはブラウザーへ渡さない。"""

import html
import posixpath
import secrets
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

TAGS = set("main section article header footer nav aside div span p h1 h2 h3 h4 h5 h6 ul ol li dl dt dd pre code blockquote strong em b i u small br hr table thead tbody tfoot tr th td caption form label input textarea button select option fieldset legend details summary a img".split())
VOID = {"input", "br", "hr", "img"}
ATTRIBUTES = {"id", "class", "title", "lang", "role", "name", "value", "type", "placeholder", "for", "rows", "cols", "min", "max", "step", "maxlength", "minlength", "required", "disabled", "checked", "selected", "multiple", "colspan", "rowspan", "alt"}
DROP_CONTENT = {"script", "iframe", "object", "svg", "math", "noscript", "template", "title"}


def local_path(value, current="/"):
    if not isinstance(value, str) or len(value) > 500:
        raise ValueError("プレビューのパスが長すぎます。")
    decoded = unquote(value)
    parts = urlsplit(decoded)
    if parts.scheme or parts.netloc or "\\" in decoded or any(ord(c) < 32 for c in decoded):
        raise ValueError("プレビューはプロジェクト内のパスだけを開けます。")
    path = posixpath.normpath(posixpath.join(posixpath.dirname(current), parts.path or current))
    if not path.startswith("/"):
        path = "/" + path
    return path + ("?" + parts.query if parts.query else "")


class PreviewHTML(HTMLParser):
    def __init__(self, files, path):
        super().__init__(convert_charrefs=True)
        self.files = files
        self.path = path
        self.output = []
        self.css = []
        self.dropped = []
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        if self.dropped:
            if tag in DROP_CONTENT:
                self.dropped.append(tag)
            return
        if tag in DROP_CONTENT:
            self.dropped.append(tag)
            return
        if tag == "style":
            self.in_style = True
            return
        if tag == "link":
            attributes = dict(attrs)
            if attributes.get("rel", "").lower() == "stylesheet":
                try:
                    name = local_path(attributes.get("href", ""), self.path).split("?")[0].lstrip("/")
                    if name.endswith(".css") and name in self.files:
                        self.css.append(self.files[name])
                except ValueError:
                    pass
            return
        if tag not in TAGS:
            return
        safe = []
        for key, value in attrs:
            value = value or ""
            if key in ATTRIBUTES or key.startswith("aria-"):
                safe.append((key, value))
            elif key == "style":
                safe.append((key, value))
            elif (tag == "a" and key == "href") or (tag == "form" and key == "action"):
                try:
                    safe.append(("data-build-path", local_path(value, self.path)))
                except ValueError:
                    pass
            elif tag == "form" and key == "method":
                safe.append(("data-build-method", "POST" if value.upper() == "POST" else "GET"))
        if tag == "a":
            safe.extend([("href", "#"), ("role", "link")])
        attributes = "".join(f' {key}="{html.escape(value, quote=True)}"' for key, value in safe)
        self.output.append(f"<{tag}{attributes}>")

    def handle_endtag(self, tag):
        if self.dropped:
            if tag == self.dropped[-1]:
                self.dropped.pop()
            return
        if tag == "style":
            self.in_style = False
        elif tag in TAGS and tag not in VOID:
            self.output.append(f"</{tag}>")

    def handle_data(self, data):
        if self.dropped:
            return
        if self.in_style:
            self.css.append(data)
        else:
            self.output.append(html.escape(data))


def make_preview(source, files, path="/"):
    parser = PreviewHTML(files, path)
    parser.feed(source[:300_000])
    parser.close()
    nonce = secrets.token_hex(24)
    # CSSからstyle要素を閉じられないようにする。外部CSS/画像URLはCSPでも遮断する。
    css = "\n".join(parser.css).replace("<", "\\3c ")
    policy = ("default-src 'none'; connect-src 'none'; img-src 'none'; media-src 'none'; "
              "font-src 'none'; frame-src 'none'; worker-src 'none'; object-src 'none'; "
              "base-uri 'none'; form-action 'none'; style-src 'unsafe-inline'; "
              f"script-src 'nonce-{nonce}'")
    bridge = '''
document.addEventListener('submit', event => {
  event.preventDefault();
  const form = event.target;
  const data = Object.fromEntries(new FormData(form).entries());
  parent.postMessage({type: 'build-request', token: TOKEN,
    path: form.getAttribute('data-build-path') || '/',
    method: form.getAttribute('data-build-method') || 'GET', data}, '*');
});
document.addEventListener('click', event => {
  const link = event.target.closest('a');
  if (!link) return;
  event.preventDefault();
  const path = link.getAttribute('data-build-path');
  if (path) parent.postMessage({type: 'build-request', token: TOKEN,
    path, method: 'GET', data: {}}, '*');
});
'''.replace("TOKEN", repr(nonce))
    document = (f'<!doctype html><html lang="ja"><head><meta charset="utf-8">'
                f'<meta http-equiv="Content-Security-Policy" content="{html.escape(policy, quote=True)}">'
                '<meta name="referrer" content="no-referrer"><meta name="viewport" content="width=device-width, initial-scale=1">'
                f'<style>{css}</style></head><body>{"".join(parser.output)}'
                f'<script nonce="{nonce}">{bridge}</script></body></html>')
    return {"document": document, "token": nonce}
