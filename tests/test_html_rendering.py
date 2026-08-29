from components.html import normalize_html


def test_multiline_html_does_not_leave_markdown_code_indentation():
    markup = """
        <div class="outer">
            <div class="first">First</div>

            <div class="header-meta">
                <span class="meta-label">System Status</span>
            </div>
        </div>
    """
    normalized = normalize_html(markup)
    assert '<div class="header-meta">' in normalized
    assert all(not line.startswith(("    ", "\t")) for line in normalized.splitlines())
    assert "\n\n" not in normalized


def test_normalization_preserves_preescaped_untrusted_text():
    markup = '<div class="message">&lt;script&gt;alert(1)&lt;/script&gt;</div>'
    assert normalize_html(markup) == markup
