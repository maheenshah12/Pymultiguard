"""
Email Source Analyzer - Determines how spammers got your email address.
"""
import re
from typing import Dict, List


class EmailSourceAnalyzer:
    """Analyzes how the sender obtained your email address."""

    def __init__(self):
        self.analysis_results = []

    def analyze_email_source(self, email_data: Dict) -> Dict:
        """
        Analyze where and how the sender got your email address.

        Returns dict with:
        - source: Where they got it (data breach, purchased list, website signup, etc.)
        - method: How they obtained it (scraping, breach, legitimate signup, etc.)
        - confidence: How confident we are (0-100%)
        - evidence: List of evidence supporting this conclusion
        - risk_level: high/medium/low
        """
        sender = email_data.get('from', '')
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')

        # Extract domain from sender
        sender_domain = self._extract_domain(sender)

        # Analyze various indicators
        sources = []

        # Check for legitimate signup FIRST (highest priority)
        legitimate = self._check_legitimate_signup(sender, body, subject)
        if legitimate:
            sources.append(legitimate)

        # Check for purchased email list indicators
        purchased_list = self._check_purchased_list_indicators(sender, body, subject)
        if purchased_list:
            sources.append(purchased_list)

        # Check for data breach indicators
        breach_analysis = self._check_data_breach_indicators(sender, body)
        if breach_analysis:
            sources.append(breach_analysis)

        # Check for web scraping indicators
        scraping = self._check_web_scraping_indicators(sender, body)
        if scraping:
            sources.append(scraping)

        # Check for social media harvesting
        social_media = self._check_social_media_harvesting(sender, body)
        if social_media:
            sources.append(social_media)

        # Return most likely source
        if sources:
            # Sort by confidence
            sources.sort(key=lambda x: x['confidence'], reverse=True)
            return sources[0]
        else:
            # Default fallback with better explanation
            return {
                'source': 'Likely Purchased List or Data Leak',
                'method': 'Your email was probably obtained through a data broker, leaked database, or web scraping',
                'confidence': 40,
                'evidence': [
                    'No direct relationship with sender',
                    'Unsolicited commercial email',
                    'You did not sign up for this service'
                ],
                'risk_level': 'medium',
                'explanation': 'This sender has your email but you never gave it to them directly. Most likely from a purchased marketing list or data leak.'
            }

    def _extract_domain(self, email: str) -> str:
        """Extract domain from email address."""
        match = re.search(r'@([a-zA-Z0-9.-]+)', email)
        return match.group(1) if match else ''

    def _check_data_breach_indicators(self, sender: str, body: str) -> Dict:
        """Check if email came from a data breach."""
        indicators = []
        confidence = 0

        # Check for suspicious domains
        suspicious_domains = ['promo', 'marketing', 'deals', 'offers']
        sender_lower = sender.lower()

        for domain in suspicious_domains:
            if domain in sender_lower:
                indicators.append(f"Suspicious domain keyword: '{domain}'")
                confidence += 15

        # Check for generic mass-mailing patterns
        if 'unsubscribe' in body.lower() and 'list' in body.lower():
            indicators.append("Mass mailing list detected")
            confidence += 20

        # Check for no personalization
        if 'dear customer' in body.lower() or 'dear user' in body.lower():
            indicators.append("Generic greeting (no personalization)")
            confidence += 25

        if confidence > 30:
            return {
                'source': 'Data Breach or Leaked Database',
                'method': 'Your email was likely exposed in a data breach or sold on dark web',
                'confidence': min(confidence, 85),
                'evidence': indicators,
                'risk_level': 'high',
                'explanation': 'Sender has your email but no personal details - typical of breached databases'
            }
        return None

    def _check_purchased_list_indicators(self, sender: str, body: str, subject: str) -> Dict:
        """Check if email came from a purchased marketing list."""
        indicators = []
        confidence = 0

        # Check for marketing agency patterns
        marketing_patterns = ['promo', 'marketing', 'deals', 'offers', 'campaign']
        sender_lower = sender.lower()

        for pattern in marketing_patterns:
            if pattern in sender_lower:
                indicators.append(f"Marketing domain detected: '{pattern}'")
                confidence += 25

        # Personal name in sender (like "Kate @" or "Matt from") suggests marketing
        if re.search(r'(^|\s)(kate|matt|john|sarah|mike|alex)\s*(from|@)', sender_lower):
            indicators.append("Personal name in sender (marketing tactic)")
            confidence += 30

        # Marketing keywords
        marketing_keywords = ['limited time', 'act now', 'exclusive offer', 'special deal',
                             'discount', 'save', 'free', 'click here', 'don\'t miss',
                             'expires soon', 'last chance']

        body_lower = body.lower()
        subject_lower = subject.lower()

        keyword_count = 0
        for keyword in marketing_keywords:
            if keyword in body_lower or keyword in subject_lower:
                keyword_count += 1
                if keyword_count <= 3:  # Only show first 3
                    indicators.append(f"Marketing language: '{keyword}'")
                confidence += 8

        # Check for tracking pixels/links
        if 'track' in body_lower or 'pixel' in body_lower or 'analytics' in body_lower:
            indicators.append("Email tracking detected")
            confidence += 15

        # Check for unsubscribe with list ID
        if re.search(r'list[-_]?id|mailing[-_]?list', body_lower):
            indicators.append("Commercial mailing list ID found")
            confidence += 25

        # Generic greeting is common in purchased lists
        if re.search(r'(dear|hi|hello)\s+(customer|user|friend|there)', body_lower):
            indicators.append("Generic greeting (no personalization)")
            confidence += 20

        if confidence > 50:
            return {
                'source': 'Purchased Email Marketing List',
                'method': 'Your email was sold to marketers by a third-party data broker',
                'confidence': min(confidence, 85),
                'evidence': indicators[:5],  # Top 5 evidence
                'risk_level': 'medium',
                'explanation': 'This company bought your email from a data broker or marketing list provider. They never had direct contact with you before.'
            }
        return None

    def _check_web_scraping_indicators(self, sender: str, body: str) -> Dict:
        """Check if email was scraped from websites."""
        indicators = []
        confidence = 0

        # Check for automated/bot-like patterns
        if re.search(r'no-?reply', sender.lower()):
            indicators.append("No-reply sender (automated system)")
            confidence += 20

        # Check for generic content
        if len(body) < 200:
            indicators.append("Very short email (automated)")
            confidence += 15

        # Check for lack of personalization
        if 'hi' in body.lower()[:50] and '@' not in body[:200]:
            indicators.append("Generic greeting without name")
            confidence += 20

        if confidence > 35:
            return {
                'source': 'Web Scraping / Public Directory',
                'method': 'Your email was scraped from a public website, forum, or directory',
                'confidence': min(confidence, 70),
                'evidence': indicators,
                'risk_level': 'medium',
                'explanation': 'Automated bots collected your email from publicly visible sources'
            }
        return None

    def _check_legitimate_signup(self, sender: str, body: str, subject: str) -> Dict:
        """Check if this is from a legitimate service you signed up for."""
        indicators = []
        confidence = 0

        # Known legitimate services (expanded list)
        legitimate_services = {
            'github': 'GitHub',
            'google': 'Google',
            'microsoft': 'Microsoft',
            'amazon': 'Amazon',
            'linkedin': 'LinkedIn',
            'facebook': 'Facebook',
            'twitter': 'Twitter',
            'stackoverflow': 'Stack Overflow',
            'duolingo': 'Duolingo',
            'vercel': 'Vercel',
            'replit': 'Replit',
            'stackblitz': 'StackBlitz',
            'pictory': 'Pictory.ai',
            'codecombat': 'CodeCombat',
            'npm': 'NPM',
            'descript': 'Descript',
            'wellfound': 'Wellfound',
            'openai': 'OpenAI',
            'anthropic': 'Anthropic'
        }

        sender_lower = sender.lower()
        service_name = None

        for domain, name in legitimate_services.items():
            if domain in sender_lower:
                indicators.append(f"Recognized service: {name}")
                service_name = name
                confidence += 50

        # Check for account-related content
        account_keywords = ['account', 'verify', 'confirm', 'welcome', 'password',
                           'security', 'settings', 'profile', 'update', 'notification']

        body_lower = body.lower()
        subject_lower = subject.lower()

        for keyword in account_keywords:
            if keyword in body_lower or keyword in subject_lower:
                indicators.append(f"Account-related content: '{keyword}'")
                confidence += 8

        # Check for personalized content
        if 'your' in body_lower[:200]:
            indicators.append("Personalized content detected")
            confidence += 10

        if confidence > 50:
            explanation = f"You signed up for {service_name or 'this service'} and provided your email during registration"
            return {
                'source': f'Direct Signup: {service_name or "Service"}',
                'method': 'You voluntarily provided your email when creating an account',
                'confidence': min(confidence, 95),
                'evidence': indicators,
                'risk_level': 'low',
                'explanation': explanation
            }
        return None

    def _check_social_media_harvesting(self, sender: str, body: str) -> Dict:
        """Check if email was harvested from social media."""
        indicators = []
        confidence = 0

        # Social media related keywords
        social_keywords = ['connect', 'network', 'follow', 'profile', 'linkedin',
                          'facebook', 'twitter', 'instagram']

        body_lower = body.lower()

        for keyword in social_keywords:
            if keyword in body_lower:
                indicators.append(f"Social media keyword: '{keyword}'")
                confidence += 15

        if confidence > 30:
            return {
                'source': 'Social Media Harvesting',
                'method': 'Your email was collected from your social media profile or connections',
                'confidence': min(confidence, 75),
                'evidence': indicators,
                'risk_level': 'medium',
                'explanation': 'Email harvested from social media platforms or professional networks'
            }
        return None


def analyze_email_source(email_data: Dict) -> Dict:
    """Convenience function to analyze email source."""
    analyzer = EmailSourceAnalyzer()
    return analyzer.analyze_email_source(email_data)
