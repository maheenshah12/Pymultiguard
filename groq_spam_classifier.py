"""Groq-compatible spam classifier without json_schema requirement."""
import json
import os
import time
from openai import AsyncOpenAI
from pydantic import BaseModel
from security.pii_anonymizer import PIIAnonymizer
from security.audit_logger import AuditLogger


class SpamClassification(BaseModel):
    is_spam: bool
    confidence: float
    reason: str
    indicators: list[str]


async def classify_email_groq(email_text: str, model_name: str = "llama-3.1-8b-instant",
                              email_id: str = None, anonymize_pii: bool = True) -> SpamClassification:
    """Classify email using Groq API without json_schema."""

    # Initialize audit logger
    audit_logger = AuditLogger()
    start_time = time.time()

    # Anonymize PII if enabled
    pii_found = []
    original_text = email_text
    if anonymize_pii:
        anonymizer = PIIAnonymizer()
        email_text, pii_found = anonymizer.anonymize(email_text, preserve_structure=True)

        # Log PII detection
        for pii in pii_found:
            audit_logger.log_pii_detection(
                email_id=email_id or "unknown",
                pii_type=pii['type'],
                pii_hash=pii['hash'],
                anonymized=True,
                context=f"Found in email before API call"
            )

    # Truncate email body to prevent rate limit issues (max ~3000 chars)
    if len(email_text) > 3000:
        email_text = email_text[:3000] + "\n[... truncated for length ...]"

    client = AsyncOpenAI(
        api_key=os.environ.get('OPENAI_API_KEY'),
        base_url=os.environ.get('OPENAI_BASE_URL', 'https://api.groq.com/openai/v1')
    )

    prompt = f"""You are an expert spam detection specialist. Analyze the following email and classify it as spam or legitimate.

Look for these spam indicators:
- Phishing attempts: fake login links, urgent account warnings, requests for credentials
- Suspicious sender domains: misspelled company names, unusual TLDs, free email services for business
- Urgency tactics: "act now", "limited time", "account suspended", "verify immediately"
- Too-good-to-be-true offers: lottery wins, inheritance, get-rich-quick schemes
- Poor grammar/spelling: unusual phrasing, excessive typos
- Suspicious links: shortened URLs, mismatched display text and actual URL
- Generic greetings: "Dear customer" instead of actual name
- Requests for money or personal information
- Excessive capitalization or exclamation marks

Legitimate email indicators:
- Known sender from reputable domain
- Personalized content with specific details
- Professional tone and proper grammar
- Expected communication (newsletters, receipts, work emails)
- No suspicious links or requests

Email to analyze:
{email_text}

Respond with ONLY a JSON object in this exact format (no other text):
{{
    "is_spam": true or false,
    "confidence": 0.0 to 1.0,
    "reason": "brief explanation",
    "indicators": ["indicator1", "indicator2"]
}}"""

    try:
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a spam detection expert. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

        response_time = time.time() - start_time
        content = response.choices[0].message.content.strip()

        # Estimate tokens used (rough estimate)
        tokens_used = len(email_text.split()) + len(content.split()) + 100

        # Log API call
        audit_logger.log_api_call(
            api_provider="groq",
            model_name=model_name,
            email_id=email_id or "unknown",
            tokens_used=tokens_used,
            response_time=response_time,
            status="success"
        )

        # Try to extract JSON if there's extra text
        if not content.startswith('{'):
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                content = content[start:end]

        result = json.loads(content)
        classification = SpamClassification(**result)

        # Log classification decision
        audit_logger.log_classification(
            email_id=email_id or "unknown",
            classification="spam" if classification.is_spam else "legitimate",
            confidence=classification.confidence,
            reason=classification.reason,
            indicators=classification.indicators,
            model_used=model_name,
            anonymized=anonymize_pii
        )

        return classification

    except json.JSONDecodeError as e:
        # Log failed API call
        audit_logger.log_api_call(
            api_provider="groq",
            model_name=model_name,
            email_id=email_id or "unknown",
            tokens_used=0,
            response_time=time.time() - start_time,
            status="failure",
            error_message=f"JSON parse error: {e}"
        )

        # Fallback classification
        return SpamClassification(
            is_spam=False,
            confidence=0.5,
            reason=f"Failed to parse response: {e}",
            indicators=[]
        )
    except Exception as e:
        # Log failed API call
        audit_logger.log_api_call(
            api_provider="groq",
            model_name=model_name,
            email_id=email_id or "unknown",
            tokens_used=0,
            response_time=time.time() - start_time,
            status="failure",
            error_message=str(e)
        )
        raise Exception(f"Error classifying email: {e}")
