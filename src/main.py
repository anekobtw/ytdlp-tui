import asyncio

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Center, HorizontalGroup
from textual.widgets import Button, Header, Input, ProgressBar
from yt_dlp import YoutubeDL


class ytdlp_cli(App):
    theme = "tokyo-night"
    TITLE = "ytdlp-tui"
    SUB_TITLE = "Paste a URL and start downloading instantly."
    CSS_PATH = "style.tcss"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        yield Center(ProgressBar(id="progressbar", classes="default"))

        yield Center(Input(placeholder="Video URL", id="url-input", classes="default"))

        yield HorizontalGroup(
            Input(placeholder="Start time", id="url-start-time", classes="default"),
            Input(placeholder="End time", id="url-end-time", classes="default"),
            classes="default centered",
        )

        yield Center(Button(label="Download", variant="primary", id="dl-button", classes="default"))

    @on(Input.Submitted)
    def submitted(self, event: Input.Changed) -> None:
        self.download(event.value)

    @on(Button.Pressed)
    def pressed(self, event: Button.Pressed) -> None:
        self.download(self.query_one("#url-input", Input).value)

    @work(exclusive=True, exit_on_error=False, thread=True)
    async def download(self, url: str) -> None:
        opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/b[ext=mp4]",
            "quiet": True,
            "progress_hooks": [self.progress_hook],
        }

        with YoutubeDL(opts) as ydl:
            try:
                self.query_one("#url-input", Input).disabled = True
                self.query_one("#dl-button", Button).disabled = True
                ydl.download(url)
                self.notify(message="Your video has been successfully downloaded!")

            except Exception as e:
                self.notify(
                    title="Error occured while downloading!",
                    message=str(e),
                    severity="error",
                )

            finally:
                self.query_one("#url-input", Input).disabled = False
                self.query_one("#dl-button", Button).disabled = False

    def progress_hook(self, d):
        self.query_one("#progressbar", ProgressBar).update(
            total=d.get("total_bytes") or d.get("total_bytes_estimate") or 0,
            progress=d.get("downloaded_bytes", 0),
        )


if __name__ == "__main__":
    app = ytdlp_cli()
    asyncio.run(app.run_async())
