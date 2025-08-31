import pathlib
import re


def replace_chunk(content, marker, chunk):
    """Replaces a marked chunk of text in a string."""
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    chunk = "<!-- {} starts -->\n{}\n<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)


if __name__ == "__main__":
    root = pathlib.Path(__file__).parent.resolve()
    readme_path = root / "README.md"
    readme_contents = readme_path.open().read()

    print("README build script executed.")
