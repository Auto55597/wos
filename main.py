import logging

import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from core import app

console = Console()
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("wos")


def main() -> None:
    banner = Text("WOS  /  WORKSPACE OS\nCORE ENGINE  |  KERNEL ONLINE", style="bold cyan")
    console.print(Panel(banner, title="System Startup", border_style="cyan"))
    logger.info("Starting API at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
