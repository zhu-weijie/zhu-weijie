import feedparser
import httpx
import os
import pathlib
import re
from dotenv import load_dotenv

load_dotenv()

MAX_POSTS = 12
MAX_PROJECTS = 4
MAX_DIAGRAMS = 15
GITHUB_USERNAME = "zhu-weijie"
BLOG_FEED_URL = "https://zhu-weijie.github.io/rss.xml"
DIAGRAMS_FEED_URL = "https://zhu-weijie.github.io/diagrams/rss.xml"  # New feed URL

SKIP_REPOS = {"zhu-weijie", "zhu-weijie.github.io"}


def replace_chunk(content, marker, chunk):
    """Replaces a marked chunk of text in a string."""
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    chunk = "<!-- {} starts -->\n{}\n<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)


def fetch_blog_entries():
    """Fetches the most recent blog entries from the feed."""
    entries = feedparser.parse(BLOG_FEED_URL)["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
        }
        for entry in entries
    ]


def fetch_diagram_entries():
    """Fetches the most recent diagram entries from the feed."""
    entries = feedparser.parse(DIAGRAMS_FEED_URL)["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
        }
        for entry in entries
    ]


def fetch_github_projects(token):
    """Fetches the most recently updated public repos for a user."""
    headers = {"Authorization": f"bearer {token}"}
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?sort=pushed&direction=desc&type=owner&per_page=100"

    response = httpx.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch repos: {response.status_code} - {response.text}"
        )

    repos = response.json()
    return [
        {
            "name": repo["name"],
            "url": repo["html_url"],
            "description": repo["description"] or "No description provided.",
        }
        for repo in repos
        if not repo["fork"] and repo["name"] not in SKIP_REPOS
    ]


if __name__ == "__main__":
    root = pathlib.Path(__file__).parent.resolve()
    readme_path = root / "README.md"
    readme_contents = readme_path.read_text()

    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable is not set!")

    posts = fetch_blog_entries()[:MAX_POSTS]
    posts_md = "\n\n".join(["* [{title}]({url})".format(**post) for post in posts])
    rewritten_readme = replace_chunk(readme_contents, "blog", posts_md)

    projects = fetch_github_projects(github_token)[:MAX_PROJECTS]
    projects_md = "\n\n".join(
        [
            "* [{name}]({url})<br/>{description}".format(**project)
            for project in projects
        ]
    )
    rewritten_readme = replace_chunk(rewritten_readme, "recent_projects", projects_md)

    diagrams = fetch_diagram_entries()[:MAX_DIAGRAMS]
    diagrams_md = "\n\n".join(
        ["* [{title}]({url})".format(**diagram) for diagram in diagrams]
    )
    rewritten_readme = replace_chunk(rewritten_readme, "diagrams", diagrams_md)

    readme_path.write_text(rewritten_readme)
    print("Successfully updated README with posts, projects, and diagrams.")
