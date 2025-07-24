import asyncio

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Center, HorizontalGroup
from textual.widgets import Button, Header, Input, ProgressBar
from yt_dlp import YoutubeDL


class ytdlp_cli(App):
    theme = "tokyo-night"
    TITLE = "ytdlp-cli"
    SUB_TITLE = "Paste a URL and start downloading instantly."
    CSS_PATH = "style.tcss"

    async def on_mount(self) -> None:
        await self.mount(Header(show_clock=True))

        await self.mount(Center(ProgressBar(id="progressbar")))

        await self.mount(
            HorizontalGroup(
                Input(placeholder="Video URL", type="text", id="url-input"),
                Button(label="Download", variant="primary", id="dl-button"),
                classes="container",
            )
        )

    @on(Input.Submitted)
    async def submitted(self, event: Input.Changed) -> None:
        self.download(event.value)

    @on(Button.Pressed)
    async def pressed(self, event: Button.Pressed) -> None:
        self.download(self.query_one("#url-input", Input).value)

    @work(exclusive=True, exit_on_error=False, thread=True)
    async def download(self, url: str) -> None:
        opts = {
            "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",
            "quiet": True,
            "progress_hooks": [self.progress_hook],
        }

        with YoutubeDL(opts) as ydl:
            try:
                self.query_one("#url-input", Input).disabled = True
                self.query_one("#dl-button", Button).disabled = True
                ydl.download(url)
            except Exception as e:
                self.notify(
                    title="Error occured while downloading!",
                    message=str(e),
                    severity="error",
                )
            else:
                self.notify(message="Your video has been successfully downloaded!")
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
