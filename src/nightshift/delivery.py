"""Telegram delivery via Composio."""

from __future__ import annotations

from nightshift.config import DeliveryConfig
from nightshift.integrations import execute_action
from nightshift.models import MorningBrief


class TelegramDelivery:
    def __init__(self, config: DeliveryConfig) -> None:
        self.config = config

    async def send(self, brief: MorningBrief) -> None:
        if not self.config.enabled:
            print("[delivery] Telegram disabled — skipping send")
            return

        if not brief.sections:
            print("[delivery] Empty brief — nothing to send")
            return

        message = brief.summary

        # Split into chunks if too long for Telegram (4096 char limit)
        chunks = self._split_message(message, max_len=4000)

        for chunk in chunks:
            execute_action(
                "TELEGRAM_SEND_MESSAGE",
                {
                    "chat_id": self.config.telegram_chat_id,
                    "text": chunk,
                },
            )
        print(f"[delivery] Sent {len(chunks)} message(s) to Telegram")

    @staticmethod
    def _split_message(text: str, max_len: int = 4000) -> list[str]:
        if len(text) <= max_len:
            return [text]
        chunks: list[str] = []
        while text:
            if len(text) <= max_len:
                chunks.append(text)
                break
            # Split at last newline before limit
            split_at = text.rfind("\n", 0, max_len)
            if split_at == -1:
                split_at = max_len
            chunks.append(text[:split_at])
            text = text[split_at:].lstrip("\n")
        return chunks
