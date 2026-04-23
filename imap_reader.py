import imaplib
import email
from email.header import decode_header
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, IMAP_HOST, IMAP_PORT


def get_imap_connection():
    """Connect and login to IMAP server."""
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    return mail


def get_unread_emails(limit=None):
    """Fetch unread emails from inbox."""
    mail = get_imap_connection()
    mail.select("INBOX")

    status, messages = mail.search(None, "UNSEEN")
    email_ids = messages[0].split()

    if limit:
        email_ids = email_ids[:limit]

    emails = []
    for eid in email_ids:
        status, msg_data = mail.fetch(eid, "(RFC822 X-GM-LABELS)")
        raw_email = msg_data[0][1]

        # Extract Gmail labels
        gmail_labels = ""
        for item in msg_data:
            if isinstance(item, bytes):
                item_str = item.decode('utf-8', errors='ignore')
                if 'X-GM-LABELS' in item_str:
                    gmail_labels = item_str
                    break

        category = detect_gmail_category(gmail_labels)
        parsed = parse_email(raw_email, eid, category)
        if parsed:
            emails.append(parsed)

    mail.logout()
    return emails


def detect_gmail_category(labels_str: str) -> str:
    """Detect Gmail category from X-GM-LABELS response."""
    if not labels_str:
        return "Primary"

    labels_upper = labels_str.upper()

    if "\\IMPORTANT" in labels_upper and "\\CATEGORY_PROMOTIONS" in labels_upper:
        return "Promotions"
    elif "\\CATEGORY_PROMOTIONS" in labels_upper:
        return "Promotions"
    elif "\\CATEGORY_SOCIAL" in labels_upper:
        return "Social"
    elif "\\CATEGORY_UPDATES" in labels_upper:
        return "Updates"
    elif "\\CATEGORY_FORUMS" in labels_upper:
        return "Forums"
    else:
        return "Primary"


def decode_str(value):
    """Decode encoded email header strings."""
    if not value:
        return ""
    decoded, encoding = decode_header(value)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding or "utf-8", errors="ignore")
    return decoded


def parse_email(raw_email: bytes, email_id, category="Primary") -> dict:
    """Parse raw email bytes into a structured dict."""
    msg = email.message_from_bytes(raw_email)

    subject = decode_str(msg.get("Subject", ""))
    from_addr = decode_str(msg.get("From", ""))
    to_addr = decode_str(msg.get("To", ""))
    message_id = msg.get("Message-ID", "")

    body = extract_body(msg)

    return {
        "email_id": email_id.decode() if isinstance(email_id, bytes) else email_id,
        "subject": subject,
        "from": from_addr,
        "to": to_addr,
        "message_id": message_id,
        "body": body,
        "category": category,
    }


def extract_body(msg) -> str:
    """Extract plain text body from email (handles multipart)."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                charset = part.get_content_charset() or "utf-8"
                return part.get_payload(decode=True).decode(charset, errors="ignore")
    else:
        if msg.get_content_type() == "text/plain":
            charset = msg.get_content_charset() or "utf-8"
            return msg.get_payload(decode=True).decode(charset, errors="ignore")
    return ""


def mark_as_read(email_id):
    """Mark an email as read (seen) by its IMAP ID."""
    mail = get_imap_connection()
    mail.select("INBOX")
    mail.store(email_id, "+FLAGS", "\\Seen")
    mail.logout()


def move_to_spam(email_id):
    """Move an email to the Spam folder."""
    mail = get_imap_connection()
    mail.select("INBOX")

    # Copy to [Gmail]/Spam folder
    result = mail.copy(email_id, "[Gmail]/Spam")

    if result[0] == 'OK':
        # Delete from inbox (mark for deletion)
        mail.store(email_id, '+FLAGS', '\\Deleted')
        # Expunge to permanently remove
        mail.expunge()
        mail.logout()
        return True
    else:
        mail.logout()
        return False


def get_all_folders():
    """List all available IMAP folders."""
    mail = get_imap_connection()
    status, folders = mail.list()
    mail.logout()
    return folders if status == 'OK' else []
