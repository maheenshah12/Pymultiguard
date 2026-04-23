"""
Data Collection Analyzer - Detects what personal data the sender has about you.
"""
import re
from typing import Dict, List


class DataCollectionAnalyzer:
    """Analyzes what personal data the sender has collected about you."""

    def analyze_data_collection(self, email_data: Dict) -> Dict:
        """
        Analyze what personal data the sender has about you.

        Returns:
        - has_email: Always true (they sent you email)
        - has_name: Do they know your name?
        - has_location: Do they know your location?
        - has_interests: Do they know your interests?
        - is_tracking: Are they tracking you?
        - personalization_level: minimal/moderate/extensive
        - data_points: List of specific data they have
        - risk_assessment: What this means for your privacy
        """
        sender = email_data.get('from', '')
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')

        data_points = []

        # Always have email
        data_points.append("Your email address")

        # Check for name usage
        has_name = self._check_name_usage(body, subject)
        if has_name:
            data_points.append("Your name (personalized greeting)")

        # Check for location data
        location_info = self._check_location_data(body, subject)
        if location_info:
            data_points.append(f"Your location: {location_info}")

        # Check for interest/behavior tracking
        interests = self._check_interest_tracking(body, subject)
        if interests:
            data_points.extend([f"Interest in: {i}" for i in interests[:3]])

        # Check for tracking mechanisms
        tracking = self._check_tracking(body)
        if tracking:
            data_points.extend(tracking)

        # Determine personalization level
        personalization_level = self._calculate_personalization_level(
            has_name, location_info, interests, tracking
        )

        # Risk assessment
        risk = self._assess_privacy_risk(len(data_points), tracking, personalization_level)

        return {
            'has_email': True,
            'has_name': has_name,
            'has_location': bool(location_info),
            'has_interests': bool(interests),
            'is_tracking': bool(tracking),
            'personalization_level': personalization_level,
            'data_points': data_points,
            'data_count': len(data_points),
            'risk_assessment': risk
        }

    def _check_name_usage(self, body: str, subject: str) -> bool:
        """Check if they use your actual name (not generic greeting)."""
        body_lower = body.lower()

        # Generic greetings mean they DON'T have your name
        generic = ['dear customer', 'dear user', 'dear friend', 'hi there',
                   'hello there', 'dear valued']

        for generic_greeting in generic:
            if generic_greeting in body_lower[:200]:
                return False

        # Personalized greetings suggest they have your name
        personalized = ['hi [a-z]+', 'hello [a-z]+', 'dear [a-z]+']

        for pattern in personalized:
            if re.search(pattern, body_lower[:200]):
                # Make sure it's not "hi team" or other generic
                if not re.search(r'hi (team|everyone|all|folks)', body_lower[:200]):
                    return True

        return False

    def _check_location_data(self, body: str, subject: str) -> str:
        """Check if they mention your location."""
        text = (body + ' ' + subject).lower()

        # Common location indicators
        location_patterns = [
            r'in ([A-Z][a-z]+ ?[A-Z]?[a-z]*)',  # "in New York"
            r'near you',
            r'your area',
            r'local to you',
            r'your city',
            r'your country'
        ]

        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                if match.groups():
                    return match.group(1)
                return "detected"

        return None

    def _check_interest_tracking(self, body: str, subject: str) -> List[str]:
        """Check if they reference your interests or behavior."""
        text = (body + ' ' + subject).lower()
        interests = []

        # Behavioral tracking phrases
        tracking_phrases = {
            'based on your': 'browsing history',
            'you might like': 'preference tracking',
            'recommended for you': 'recommendation algorithm',
            'because you': 'behavior tracking',
            'your recent': 'activity monitoring',
            'you viewed': 'browsing tracking',
            'you searched': 'search history',
            'similar to': 'preference profiling'
        }

        for phrase, interest_type in tracking_phrases.items():
            if phrase in text:
                interests.append(interest_type)

        return interests

    def _check_tracking(self, body: str) -> List[str]:
        """Check for tracking mechanisms."""
        tracking = []
        body_lower = body.lower()

        # Tracking pixels
        if 'pixel' in body_lower or 'track' in body_lower:
            tracking.append("Email tracking (open/read detection)")

        # Unique links
        if re.search(r'https?://[^\s]+\?[^\s]*id=', body):
            tracking.append("Unique tracking links (click monitoring)")

        # Analytics
        if 'analytics' in body_lower or 'utm_' in body_lower:
            tracking.append("Marketing analytics tracking")

        return tracking

    def _calculate_personalization_level(self, has_name, location, interests, tracking):
        """Calculate how personalized the email is."""
        score = 0

        if has_name:
            score += 2
        if location:
            score += 2
        if interests:
            score += len(interests)
        if tracking:
            score += 1

        if score == 0:
            return "minimal"
        elif score <= 3:
            return "moderate"
        else:
            return "extensive"

    def _assess_privacy_risk(self, data_count, tracking, personalization_level):
        """Assess privacy risk based on data collection."""
        if personalization_level == "extensive" or (tracking and data_count > 4):
            return {
                'level': 'high',
                'message': 'They have significant data about you and are actively tracking your behavior'
            }
        elif personalization_level == "moderate" or tracking:
            return {
                'level': 'medium',
                'message': 'They have some personal data and may be tracking you'
            }
        else:
            return {
                'level': 'low',
                'message': 'They only have your email address with minimal other data'
            }


def analyze_data_collection(email_data: Dict) -> Dict:
    """Convenience function."""
    analyzer = DataCollectionAnalyzer()
    return analyzer.analyze_data_collection(email_data)
