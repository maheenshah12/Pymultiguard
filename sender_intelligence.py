"""
Sender Intelligence - Uses web search to get REAL information about email senders.
"""
import re
from typing import Dict


class SenderIntelligence:
    """Gets real information about email senders using web search."""

    def __init__(self, web_search_func=None):
        self.web_search = web_search_func

    def lookup_sender(self, sender_email: str, sender_domain: str) -> Dict:
        """
        Look up real information about the sender using web search.

        Returns:
        - company_name: Name of the company
        - description: What they do
        - legitimacy: legitimate/suspicious/unknown
        - industry: Type of business
        - found_info: Whether we found real data
        """
        if not self.web_search:
            return self._no_search_fallback(sender_domain)

        try:
            # Search for the company
            query = f"{sender_domain} company what is"
            search_results = self.web_search(query)

            # Parse search results
            company_info = self._parse_search_results(search_results, sender_domain)
            return company_info

        except Exception as e:
            return self._no_search_fallback(sender_domain)

    def _parse_search_results(self, results: str, domain: str) -> Dict:
        """Parse web search results to extract company info."""
        # This is a simplified parser - in production you'd use more sophisticated NLP
        results_lower = results.lower()

        # Try to find company description
        description = "No description available"

        # Look for common description patterns
        if domain.replace('.com', '').replace('.ai', '') in results_lower:
            # Extract a sentence that mentions the domain
            sentences = results.split('.')
            for sentence in sentences[:5]:  # Check first 5 sentences
                if domain.replace('.com', '').replace('.ai', '') in sentence.lower():
                    description = sentence.strip()
                    break

        # Determine legitimacy
        legitimacy = "unknown"
        if any(word in results_lower for word in ['scam', 'fraud', 'spam', 'phishing']):
            legitimacy = "suspicious"
        elif any(word in results_lower for word in ['company', 'official', 'legitimate', 'trusted']):
            legitimacy = "legitimate"

        # Try to determine industry
        industry = "Unknown"
        industries = {
            'software': ['software', 'saas', 'platform', 'app', 'technology'],
            'marketing': ['marketing', 'advertising', 'promotion', 'campaign'],
            'education': ['education', 'learning', 'course', 'training'],
            'finance': ['finance', 'banking', 'payment', 'money'],
            'ecommerce': ['shop', 'store', 'ecommerce', 'retail']
        }

        for industry_name, keywords in industries.items():
            if any(keyword in results_lower for keyword in keywords):
                industry = industry_name.capitalize()
                break

        return {
            'company_name': domain.split('.')[0].capitalize(),
            'description': description[:200] if len(description) > 200 else description,
            'legitimacy': legitimacy,
            'industry': industry,
            'found_info': True
        }

    def _no_search_fallback(self, domain: str) -> Dict:
        """Fallback when web search is not available."""
        return {
            'company_name': domain.split('.')[0].capitalize(),
            'description': 'Web search not available',
            'legitimacy': 'unknown',
            'industry': 'Unknown',
            'found_info': False
        }


def lookup_sender_info(sender_email: str, web_search_func=None) -> Dict:
    """Convenience function to lookup sender information."""
    # Extract domain
    match = re.search(r'@([a-zA-Z0-9.-]+)', sender_email)
    domain = match.group(1) if match else sender_email

    intelligence = SenderIntelligence(web_search_func)
    return intelligence.lookup_sender(sender_email, domain)
