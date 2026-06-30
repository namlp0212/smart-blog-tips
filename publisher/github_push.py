"""Auto-commit and push output/ to GitHub after each pipeline run."""

import subprocess
import os
from rich.console import Console

console = Console()
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))


def _run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
    return result.returncode, (result.stdout + result.stderr).strip()


def push_output(post_titles: list[str] = None):
    """Stage output/, commit, and push to GitHub."""
    # Stage output folder + data/published.json
    code, out = _run(["git", "add", "output/", "data/published.json"])
    if code != 0:
        console.print(f"[red]git add failed: {out}[/red]")
        return False

    # Check if there's anything to commit
    code, out = _run(["git", "diff", "--cached", "--quiet"])
    if code == 0:
        console.print("[yellow]Nothing new to commit.[/yellow]")
        return True

    # Commit
    if post_titles:
        msg = f"Add {len(post_titles)} post(s): {', '.join(post_titles[:3])}"
        if len(post_titles) > 3:
            msg += f" (+{len(post_titles) - 3} more)"
    else:
        msg = "Update blog posts"

    code, out = _run(["git", "commit", "-m", msg])
    if code != 0:
        console.print(f"[red]git commit failed: {out}[/red]")
        return False
    console.print(f"[green]Committed:[/green] {msg}")

    # Push
    code, out = _run(["git", "push", "origin", "main"])
    if code != 0:
        console.print(f"[red]git push failed: {out}[/red]")
        console.print("[dim]Make sure you've added the GitHub remote:[/dim]")
        console.print("[dim]  git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git[/dim]")
        return False

    console.print("[green]Pushed to GitHub successfully.[/green]")
    return True


def has_remote() -> bool:
    """Check if GitHub remote is configured."""
    code, out = _run(["git", "remote", "get-url", "origin"])
    return code == 0 and "github.com" in out
