from pathlib import Path

from youtrack_peristalsis.md_format import (
    ArticleMarkdown,
    parse_article_markdown,
    read_article_file,
    write_article_file,
)


def test_roundtrip_frontmatter(tmp_path: Path) -> None:
    original = ArticleMarkdown(
        summary="Test Title",
        content="## Hello\n\nBody text.",
        id_readable="NP-A-1",
        article_id="226-0",
        project="NP",
        parent_article="NP-A-7",
    )
    path = tmp_path / "NP-A-1.md"
    write_article_file(path, original)
    parsed = read_article_file(path)
    assert parsed.summary == original.summary
    assert parsed.content == original.content
    assert parsed.id_readable == original.id_readable
    assert parsed.project == original.project


def test_parse_quoted_summary() -> None:
    text = '---\nsummary: "Title: with colon"\n---\n\nBody\n'
    md = parse_article_markdown(text)
    assert md.summary == "Title: with colon"
    assert md.content == "Body\n"
