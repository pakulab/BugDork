from contextlib import contextmanager

from alive_progress import alive_bar


@contextmanager
def progress(total: int, title: str = "BugDork"):
    with alive_bar(bar="blocks", title=title, total=total, enrich_print=False) as bar:
        yield bar
