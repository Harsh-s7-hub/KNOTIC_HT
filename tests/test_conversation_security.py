from components.conversation import escape_timeline_item


def test_transcript_dynamic_values_are_html_escaped():
    unsafe = {"type": "message", "role": "caller", "text": "<script>alert('x')</script>",
              "time": "<img src=x onerror=alert(1)>", "name": "<b>attacker</b>", "lang": "HI<EN"}
    safe = escape_timeline_item(unsafe)
    assert "<script>" not in safe["text"]
    assert "&lt;script&gt;" in safe["text"]
    assert "<img" not in safe["time"]
    assert safe["name"] == "&lt;b&gt;attacker&lt;/b&gt;"
    assert safe["lang"] == "HI&lt;EN"
