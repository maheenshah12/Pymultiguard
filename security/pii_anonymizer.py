"""
PII (Personally Identifiable Information) Anonymization Module.
Detects and masks sensitive information before sending to external APIs.
"""
import re
import hashlib
from typing import Dict, List, Tuple


class PIIAnonymizer:
    """Detects and anonymizes PII in email content."""

    def __init__(self, anonymize_emails=True, anonymize_phones=True, anonymize_names=True):
        self.anonymize_emails = anonymize_emails
        self.anonymize_phones = anonymize_phones
        self.anonymize_names = anonymize_names
        self.pii_found = []  # Track what PII was found

    # Regex patterns for PII detection
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'

    # Common name patterns (simplified - real implementation would use NER)
    NAME_INDICATORS = ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Dear', 'Hi', 'Hello']

    def anonymize(self, text: str, preserve_structure=True) -> Tuple[str, List[Dict]]:
        """
        Anonymize PII in text.

        Returns:
            Tuple of (anonymized_text, pii_found_list)
        """
        if not text:
            return text, []

        anonymized = text
        self.pii_found = []

        # Anonymize emails
        if self.anonymize_emails:
            anonymized, email_pii = self._anonymize_emails(anonymized, preserve_structure)
            self.pii_found.extend(email_pii)

        # Anonymize phone numbers
        if self.anonymize_phones:
            anonymized, phone_pii = self._anonymize_phones(anonymized, preserve_structure)
            self.pii_found.extend(phone_pii)

        # Anonymize potential names (basic implementation)
        if self.anonymize_names:
            anonymized, name_pii = self._anonymize_names(anonymized, preserve_structure)
            self.pii_found.extend(name_pii)

        return anonymized, self.pii_found

    def _anonymize_emails(self, text: str, preserve_structure: bool) -> Tuple[str, List[Dict]]:
        """Anonymize email addresses."""
        pii_found = []
        emails = re.findall(self.EMAIL_PATTERN, text)

        for email in emails:
            if preserve_structure:
                # Keep domain structure but hash local part
                local, domain = email.split('@')
                hashed = self._hash_value(local)[:8]
                replacement = f"{hashed}@{domain}"
            else:
                replacement = "[EMAIL_REDACTED]"

            text = text.replace(email, replacement)
            pii_found.append({
                'type': 'email',
                'original': email,
                'replacement': replacement,
                'hash': self._hash_value(email)
            })

        return text, pii_found

    def _anonymize_phones(self, text: str, preserve_structure: bool) -> Tuple[str, List[Dict]]:
        """Anonymize phone numbers."""
        pii_found = []
        phones = re.findall(self.PHONE_PATTERN, text)

        for phone_parts in phones:
            # Reconstruct the phone number
            phone = ''.join(phone_parts)

            if preserve_structure:
                # Keep last 4 digits, mask rest
                replacement = f"XXX-XXX-{phone_parts[2]}"
            else:
                replacement = "[PHONE_REDACTED]"

            # Replace various formats
            text = re.sub(
                r'\b(?:\+?1[-.]?)?\(?(' + phone_parts[0] + r')\)?[-.]?(' +
                phone_parts[1] + r')[-.]?(' + phone_parts[2] + r')\b',
                replacement,
                text
            )

            pii_found.append({
                'type': 'phone',
                'original': phone,
                'replacement': replacement,
                'hash': self._hash_value(phone)
            })

        return text, pii_found

    def _anonymize_names(self, text: str, preserve_structure: bool) -> Tuple[str, List[Dict]]:
        """Anonymize potential names (basic implementation)."""
        pii_found = []

        # Look for patterns like "Dear John" or "Hi Sarah"
        for indicator in self.NAME_INDICATORS:
            pattern = rf'{indicator}\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
            matches = re.findall(pattern, text)

            for name in matches:
                if preserve_structure:
                    # Replace with [NAME_X] where X is first letter
                    replacement = f"[NAME_{name[0]}]"
                else:
                    replacement = "[NAME_REDACTED]"

                text = text.replace(f"{indicator} {name}", f"{indicator} {replacement}")
                pii_found.append({
                    'type': 'name',
                    'original': name,
                    'replacement': replacement,
                    'hash': self._hash_value(name)
                })

        return text, pii_found

    def _hash_value(self, value: str) -> str:
        """Create SHA-256 hash of value for tracking."""
        return hashlib.sha256(value.encode()).hexdigest()

    def get_pii_summary(self) -> Dict:
        """Get summary of PII found."""
        summary = {
            'total_pii_found': len(self.pii_found),
            'emails': len([p for p in self.pii_found if p['type'] == 'email']),
            'phones': len([p for p in self.pii_found if p['type'] == 'phone']),
            'names': len([p for p in self.pii_found if p['type'] == 'name'])
        }
        return summary


def anonymize_email_data(email_data: Dict, preserve_structure=True) -> Tuple[Dict, List[Dict]]:
    """
    Anonymize PII in email data dictionary.

    Args:
        email_data: Dictionary with 'subject', 'from', 'body' keys
        preserve_structure: Keep structure of data (e.g., domain names)

    Returns:
        Tuple of (anonymized_email_data, pii_found_list)
    """
    anonymizer = PIIAnonymizer()
    anonymized_data = email_data.copy()
    all_pii = []

    # Anonymize subject
    if 'subject' in email_data:
        anonymized_data['subject'], pii = anonymizer.anonymize(
            email_data['subject'], preserve_structure
        )
        all_pii.extend(pii)

    # Anonymize from field
    if 'from' in email_data:
        anonymized_data['from'], pii = anonymizer.anonymize(
            email_data['from'], preserve_structure
        )
        all_pii.extend(pii)

    # Anonymize body
    if 'body' in email_data:
        anonymized_data['body'], pii = anonymizer.anonymize(
            email_data['body'], preserve_structure
        )
        all_pii.extend(pii)

    return anonymized_data, all_pii


if __name__ == "__main__":
    # Test anonymization
    test_email = {
        'subject': 'Meeting with John Smith',
        'from': 'john.smith@example.com',
        'body': '''
        Hi Sarah,

        Please call me at 555-123-4567 or email john.smith@example.com

        Best regards,
        John Smith
        '''
    }

    anonymized, pii_found = anonymize_email_data(test_email)

    print("Original:")
    print(test_email['body'])
    print("\nAnonymized:")
    print(anonymized['body'])
    print(f"\nPII Found: {len(pii_found)} items")
    for pii in pii_found:
        print(f"  - {pii['type']}: {pii['original']} -> {pii['replacement']}")
