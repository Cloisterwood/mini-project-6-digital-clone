"""Parse the Kaggle Enron emails.csv (columns: file, message) into EmailMessage."""
import json
from email import policy
from email.parser import Parser
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Optional

from digital_clone.models import EmailMessage

QUOTE_MARKERS = [
    "-----Original Message-----",
    "---------------------- Forwarded by",
    "----- Forwarded by",
    "To:\t",  # embedded reply headers in some Enron bodies
]
SENT_FOLDER_TOKENS = ("/sent", "/_sent_mail", "/sent_items")
MIN_BODY_WORDS = 5


def is_sent_folder(file_label: str) -> bool:
    return any(tok in f"/{file_label.lower()}" for tok in SENT_FOLDER_TOKENS)


def clean_body(text: str) -> str:
    for marker in QUOTE_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
    return text.strip()


def parse_raw_email(file_label: str, raw: str) -> Optional[EmailMessage]:
    msg = Parser(policy=policy.default).parsestr(raw)
    body = clean_body(msg.get_payload() or "")
    if len(body.split()) < MIN_BODY_WORDS:
        return None
    try:
        ts = parsedate_to_datetime(msg["Date"]) if msg["Date"] else None
    except (TypeError, ValueError):
        ts = None
    recipients = [a.strip() for a in (msg["To"] or "").replace("\n", " ").split(",") if a.strip()]
    return EmailMessage(
        sender=(msg["From"] or "").strip(),
        recipients=recipients,
        subject=(msg["Subject"] or "").strip(),
        body=body,
        timestamp=ts,
        folder=file_label,
    )


def load_enron_csv(csv_path: Path, employee_folder: str, employee_email: str,
                   limit: Optional[int] = None) -> list[EmailMessage]:
    import pandas as pd  # local import: heavy dep not needed by unit tests

    emails: list[EmailMessage] = []
    for df in pd.read_csv(csv_path, chunksize=20_000):
        subset = df[df["file"].str.startswith(f"{employee_folder}/")]
        subset = subset[subset["file"].apply(is_sent_folder)]
        for _, row in subset.iterrows():
            msg = parse_raw_email(row["file"], row["message"])
            if msg and msg.sender.lower() == employee_email.lower():
                emails.append(msg)
                if limit and len(emails) >= limit:
                    return emails
    return emails


def load_fixture_emails(path: Path) -> list[EmailMessage]:
    return [EmailMessage.model_validate(e) for e in json.loads(Path(path).read_text())]
