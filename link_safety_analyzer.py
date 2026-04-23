"""
Link Safety Analyzer - Analyzes URLs in emails for security threats.
Detects phishing, malware, credential harvesting, and other threats.
"""
import re
from typing import Dict, List
from urllib.parse import urlparse, parse_qs


class LinkSafetyAnalyzer:
    """Analyzes links in emails for security threats."""

    def __init__(self):
        self.suspicious_patterns = []

    def analyze_links(self, email_body: str, sender_domain: str) -> Dict:
        """
        Analyze all links in email for security threats.

        Returns:
        - links_found: List of all URLs
        - total_links: Count
        - dangerous_links: Count of dangerous links
        - suspicious_links: Count of suspicious links
        - safe_links: Count of safe links
        - analysis: Detailed analysis of each link
        """
        # Extract all URLs
        urls = self._extract_urls(email_body)

        if not urls:
            return {
                'links_found': [],
                'total_links': 0,
                'dangerous_links': 0,
                'suspicious_links': 0,
                'safe_links': 0,
                'analysis': [],
                'overall_risk': 'none'
            }

        # Analyze each link
        analyses = []
        dangerous_count = 0
        suspicious_count = 0
        safe_count = 0

        for url in urls[:10]:  # Limit to first 10 links
            analysis = self._analyze_single_link(url, sender_domain)
            analyses.append(analysis)

            if analysis['safety_level'] == 'dangerous':
                dangerous_count += 1
            elif analysis['safety_level'] == 'suspicious':
                suspicious_count += 1
            else:
                safe_count += 1

        # Determine overall risk
        if dangerous_count > 0:
            overall_risk = 'high'
        elif suspicious_count > 2:
            overall_risk = 'high'
        elif suspicious_count > 0:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'

        return {
            'links_found': urls[:10],
            'total_links': len(urls),
            'dangerous_links': dangerous_count,
            'suspicious_links': suspicious_count,
            'safe_links': safe_count,
            'analysis': analyses,
            'overall_risk': overall_risk
        }

    def _extract_urls(self, text: str) -> List[str]:
        """Extract all URLs from text."""
        # Regex to find URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        return list(set(urls))  # Remove duplicates

    def _analyze_single_link(self, url: str, sender_domain: str) -> Dict:
        """Analyze a single link for threats."""
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
        query = parsed.query

        threats = []
        safety_level = 'safe'
        what_happens = "Legitimate link"
        recommendation = "Safe to click"

        # Check 1: HTTPS vs HTTP
        if parsed.scheme == 'http':
            threats.append("Unencrypted connection (HTTP) - data can be intercepted")
            safety_level = 'suspicious'

        # Check 2: Shortened URLs (can hide malicious destinations)
        shortened_domains = ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly',
                            'short.link', 'tiny.cc', 'is.gd', 'buff.ly']
        if any(short in domain.lower() for short in shortened_domains):
            threats.append("Shortened URL - hides real destination")
            safety_level = 'suspicious'
            what_happens = "Redirects to unknown website - could be phishing or malware"
            recommendation = "DO NOT CLICK - shortened URLs hide the real destination"

        # Check 3: Suspicious keywords in URL
        phishing_keywords = ['login', 'signin', 'verify', 'account', 'secure',
                            'update', 'confirm', 'password', 'banking', 'paypal',
                            'suspended', 'locked', 'urgent', 'action-required']

        url_lower = url.lower()
        found_keywords = [kw for kw in phishing_keywords if kw in url_lower]

        if len(found_keywords) >= 2:
            threats.append(f"Phishing keywords detected: {', '.join(found_keywords[:3])}")
            safety_level = 'dangerous'
            what_happens = "PHISHING ATTEMPT - Tries to steal your login credentials"
            recommendation = "NEVER CLICK - This is a credential harvesting attack"

        # Check 4: Domain mismatch with sender
        if sender_domain and sender_domain not in domain:
            # Check if it's a known legitimate redirect
            legitimate_redirects = ['click.', 'link.', 'track.', 'email.', 'mail.']
            is_legit_redirect = any(domain.startswith(prefix) for prefix in legitimate_redirects)

            if not is_legit_redirect and safety_level != 'dangerous':
                threats.append(f"Domain mismatch: Link goes to {domain}, not {sender_domain}")
                if safety_level == 'safe':
                    safety_level = 'suspicious'

        # Check 5: IP address instead of domain (very suspicious)
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain):
            threats.append("Uses IP address instead of domain name")
            safety_level = 'dangerous'
            what_happens = "MALWARE RISK - Legitimate sites use domain names, not IPs"
            recommendation = "NEVER CLICK - Likely malware or phishing"

        # Check 6: Suspicious TLDs (top-level domains)
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.work']
        if any(domain.endswith(tld) for tld in suspicious_tlds):
            threats.append("Suspicious domain extension (commonly used by scammers)")
            safety_level = 'dangerous'
            what_happens = "HIGH RISK - These domains are cheap and often used for scams"
            recommendation = "DO NOT CLICK - Very high scam probability"

        # Check 7: Typosquatting (misspelled popular domains)
        typosquatting_targets = {
            'google': ['gooogle', 'googel', 'gogle'],
            'facebook': ['faceb00k', 'facebok', 'faceboook'],
            'paypal': ['paypai', 'paypa1', 'paypall'],
            'amazon': ['amazom', 'amaz0n', 'amazonn'],
            'microsoft': ['micros0ft', 'microsft', 'micosoft']
        }

        for legit, typos in typosquatting_targets.items():
            if any(typo in domain.lower() for typo in typos):
                threats.append(f"TYPOSQUATTING - Fake {legit.capitalize()} site")
                safety_level = 'dangerous'
                what_happens = f"PHISHING - Impersonates {legit.capitalize()} to steal credentials"
                recommendation = "NEVER CLICK - This is a fake website designed to steal your data"

        # Check 8: Tracking parameters (privacy concern, not dangerous)
        tracking_params = ['utm_', 'fbclid', 'gclid', 'ref=', 'source=']
        if any(param in query for param in tracking_params):
            if safety_level == 'safe':
                threats.append("Contains tracking parameters (monitors your clicks)")

        # Check 9: Suspicious path patterns
        if '/wp-admin' in path or '/admin' in path:
            threats.append("Links to admin panel - unusual for legitimate emails")
            if safety_level == 'safe':
                safety_level = 'suspicious'

        # Check 10: Data exfiltration patterns
        if len(query) > 200:  # Very long query string
            threats.append("Extremely long URL - may contain encoded malware")
            safety_level = 'dangerous'
            what_happens = "MALWARE RISK - Long URLs can hide malicious code"
            recommendation = "DO NOT CLICK - Possible malware delivery"

        # Determine what happens if clicked (if not already set)
        if safety_level == 'safe' and not threats:
            what_happens = "Opens legitimate website - safe to visit"
            recommendation = "Safe to click"
        elif safety_level == 'suspicious' and what_happens == "Legitimate link":
            what_happens = "May track your activity or redirect unexpectedly"
            recommendation = "Click with caution - verify the destination first"

        return {
            'url': url,
            'domain': domain,
            'safety_level': safety_level,
            'threats': threats,
            'what_happens': what_happens,
            'recommendation': recommendation,
            'threat_count': len(threats)
        }


def analyze_email_links(email_body: str, sender_email: str) -> Dict:
    """Convenience function to analyze links in email."""
    # Extract sender domain
    sender_domain = ""
    match = re.search(r'@([a-zA-Z0-9.-]+)', sender_email)
    if match:
        sender_domain = match.group(1)

    analyzer = LinkSafetyAnalyzer()
    return analyzer.analyze_links(email_body, sender_domain)
