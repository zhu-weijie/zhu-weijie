import feedparser
import pathlib
import re

MAX_POSTS = 8
BLOG_FEED_URL = "https://zhu-weijie.github.io/rss.xml"

def replace_chunk(content, marker, chunk):
    """Replaces a marked chunk of text in a string."""
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    # This is the corrected line with the third argument for .format()
    chunk = "<!-- {} starts -->\n{}\n<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)

def fetch_blog_entries():
    """Fetches the most recent blog entries from the feed."""
    entries = feedparser.parse(BLOG_FEED_URL)["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": entry["published"].split("T")[0],
        }
        for entry in entries
    ]

if __name__ == "__main__":
    root = pathlib.Path(__file__).parent.resolve()
    readme_path = root / "README.md"
    
    # It's safer to read the file first, then open it again for writing.
    readme_contents = readme_path.read_text()

    # Fetch and format blog posts
    posts = fetch_blog_entries()[:MAX_POSTS]
    posts_md = "\n\n".join(
        ["* [{title}]({url}) - {published}".format(**post) for post in posts]
    )

    # Update the README with the new blog posts
    rewritten_readme = replace_chunk(readme_contents, "blog", posts_md)
    readme_path.write_text(rewritten_readme)

    print("Successfully updated README with latest blog posts.")
    