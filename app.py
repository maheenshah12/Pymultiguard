"""
PyMultiGuard Web Application
Flask backend for email security analysis
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import asyncio
from datetime import datetime

# Import existing modules
from imap_reader import get_unread_emails
from groq_spam_classifier import classify_email_groq
from sender_intelligence import lookup_sender_info
from data_collection_analyzer import analyze_data_collection
from email_source_analyzer import analyze_email_source
from link_safety_analyzer import analyze_email_links

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_emails():
    """Analyze emails endpoint."""
    try:
        data = request.json
        limit = data.get('limit', 5)

        # Fetch emails
        emails = get_unread_emails(limit=limit)

        if not emails:
            return jsonify({
                'success': False,
                'error': 'No emails found or connection error'
            })

        # Analyze each email
        results = []
        for email_data in emails:
            result = analyze_single_email(email_data)
            results.append(result)

        return jsonify({
            'success': True,
            'total_emails': len(results),
            'results': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def analyze_single_email(email_data):
    """Analyze a single email and return results."""
    # Spam classification
    classification = classify_email_sync(email_data)

    # Sender intelligence
    sender_info = lookup_sender_info(email_data.get('from', ''))

    # Data collection analysis
    data_analysis = analyze_data_collection(email_data)

    # Email source tracking
    source_info = analyze_email_source(email_data)

    # Link safety analysis
    link_analysis = analyze_email_links(
        email_data.get('body', ''),
        email_data.get('from', '')
    )

    return {
        'email_id': email_data.get('email_id', 'unknown'),
        'from': email_data.get('from', 'Unknown'),
        'subject': email_data.get('subject', 'No Subject'),
        'date': email_data.get('date', 'Unknown'),
        'category': email_data.get('category', 'Primary'),
        'classification': classification,
        'sender_intelligence': sender_info,
        'data_collection': data_analysis,
        'email_source': source_info,
        'link_safety': link_analysis
    }


def classify_email_sync(email_data):
    """Synchronous wrapper for async classify_email_groq."""
    try:
        email_text = f"""
From: {email_data.get('from', '')}
Subject: {email_data.get('subject', '')}
Body: {email_data.get('body', '')}
"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            classify_email_groq(
                email_text,
                email_id=email_data.get('email_id', 'unknown'),
                anonymize_pii=True
            )
        )
        loop.close()

        return {
            'is_spam': result.is_spam,
            'confidence': int(result.confidence * 100),
            'reason': result.reason,
            'indicators': result.indicators
        }
    except Exception as e:
        return {
            'is_spam': False,
            'confidence': 50,
            'reason': f'Classification error: {str(e)}',
            'indicators': []
        }


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
