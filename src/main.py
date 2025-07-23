import asyncio

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, Center, Middle
from textual.widgets import Button, Header, Input, ProgressBar
from yt_dlp import YoutubeDL


class ytdlp_cli(App):
    TITLE = "ytdlp-cli"
    SUB_TITLE = "Paste a URL and start downloading instantly."
    CSS_PATH = "style.tcss"

    def on_mount(self) -> None:
        self.theme = "tokyo-night"

    def compose(self) -> ComposeResult:
        self.progress_bar = ProgressBar(id="prbar")
        self.input = Input(placeholder="Video URL", type="text", id="url-input")
        self.dl_button = Button(label="Download", variant="primary", id="dl-button")

        yield Header(show_clock=True)
        
        yield Center(self.progress_bar)
        
        yield HorizontalGroup(
            self.input,
            self.dl_button,
            classes="container",
        )

    @on(Input.Submitted, "#url-input")
    async def submitted(self, event: Input.Changed) -> None:
        self.download(event.value)

    @on(Button.Pressed, "#dl-button")
    async def pressed(self, event: Button.Pressed) -> None:
        self.download(self.input.value)

    @work(exclusive=True, exit_on_error=False, thread=True)
    async def download(self, url: str) -> None:
        opts = {
            "format": "best",
            "quiet": True,
            "progress_hooks": [self.progress_hook],
        }

        with YoutubeDL(opts) as ydl:
            try:
                self.input.disabled = True
                self.dl_button.disabled = True
                ydl.download(url)
            except Exception as e:
                self.notify(title="Error occured while downloading!", message=str(e), severity="error")
            else:
                self.notify(message="Your video has been successfully downloaded!")
            finally:
                self.input.disabled = False
                self.dl_button.disabled = False

    def progress_hook(self, d):
        self.progress_bar.update(total=d.get("total_bytes") or d.get("total_bytes_estimate") or 0, progress=d.get("downloaded_bytes", 0))


if __name__ == "__main__":
    app = ytdlp_cli()
    app.run()
