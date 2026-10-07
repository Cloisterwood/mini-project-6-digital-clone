from pathlib import Path

from digital_clone.style.email_loader import (
    clean_body,
    is_sent_folder,
    load_fixture_emails,
    parse_raw_email,
)

RAW = """Message-ID: <123.JavaMail.evans@thyme>
Date: Mon, 5 Mar 2001 09:15:00 -0800 (PST)
From: kay.mann@enron.com
To: ben@enron.com, suzanne@enron.com
Subject: Turbine agreement

Hi Ben,

Please review the draft.

Thanks,
Kay
-----Original Message-----
From: Ben
Old quoted text that should be removed.
"""


def test_parse_raw_email():
    msg = parse_raw_email("mann-k/sent/1.", RAW)
    assert msg.sender == "kay.mann@enron.com"
    assert msg.recipients == ["ben@enron.com", "suzanne@enron.com"]
    assert msg.subject == "Turbine agreement"
    assert "Old quoted text" not in msg.body
    assert msg.timestamp is not None
    assert msg.folder == "mann-k/sent/1."


def test_clean_body_strips_forwards():
    text = "Real content here.\n---------------------- Forwarded by Kay Mann\njunk"
    assert clean_body(text).strip() == "Real content here."


def test_parse_rejects_empty_body():
    raw = "From: kay.mann@enron.com\nTo: a@b.com\nSubject: x\n\n\n"
    assert parse_raw_email("mann-k/sent/2.", raw) is None


def test_is_sent_folder():
    assert is_sent_folder("mann-k/sent/12.")
    assert is_sent_folder("mann-k/_sent_mail/3.")
    assert is_sent_folder("mann-k/sent_items/9.")
    assert not is_sent_folder("mann-k/inbox/1.")


def test_load_fixture_emails():
    fixture = Path(__file__).parent / "fixtures" / "sample_emails.json"
    emails = load_fixture_emails(fixture)
    assert len(emails) >= 12
    assert all(e.sender == "kay.mann@enron.com" for e in emails)
