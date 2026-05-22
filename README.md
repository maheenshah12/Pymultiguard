# PyMultiGuard - Email Security Analyzer

An advanced, privacy-first Information Security project designed to analyze inbound email intelligence, mitigate phishing risks, and enforce strict data privacy standards before external processing.

---

## 📸 Application Interface & Live Demonstration

### 🖥️ Desktop GUI Tool (Recommended for Presentation)
The professional desktop application interface features real-time visual analysis, interactive progress metrics, and intuitive threat indicator color-coding:
* **🟢 Green**: Safe / Verified
* **🟡 Yellow**: Suspicious / Warning (Review closely)
* **🔴 Red**: Malicious / High-Risk Threat Detected

![PyMultiGuard Main Dashboard Interface](screenshots/gui_dashboard.png)
<img width="1365" height="635" alt="Screenshot 2026-05-22 153711" src="https://github.com/user-attachments/assets/3c291507-f90f-4f8d-b370-23dd8bd7a5b1" />


### 📊 Privacy Dashboard & Analytics
Track PII masking efficiency, token consumption, and encryption logs directly through the visual management dashboard.

![loading part]
<img width="1351" height="628" alt="Screenshot 2026-05-22 153725" src="https://github.com/user-attachments/assets/50cc30ab-8719-40f3-bf29-0c1cc948ccf2" />

![Privacy Dashboard and System Metrics](screenshots/privacy_dashboard.png)
<img width="883" height="596" alt="Screenshot 2026-05-22 153748" src="https://github.com/user-attachments/assets/819d2845-0a61-4029-8a83-310c04272ed9" />
<img width="859" height="609" alt="Screenshot 2026-05-22 153759" src="https://github.com/user-attachments/assets/dea29dd6-13f7-43cb-bb2c-244f3b579259" />


###Working url link : https://pymultiguard-production.up.railway.app/
---

## 🎯 Quick Start

### Prerequisites
Ensure you have Python 3.13 installed along with the dependencies listed in `requirements.txt`.

### Launch the Graphical Interface
bash
# Launch the desktop UI application
python gui_app.py

# Or double-click the automated Windows batch script
launch_gui.bat

🛡️ Intelligence Features



This project goes beyond basic spam detection with 4 advanced intelligence modules:

🔍 Sender Intelligence - Real company lookup and legitimacy verification

📊 Data Collection Analysis - Shows what personal data they have about you

🎯 Email Source Tracking - Reveals HOW and WHERE spammers got your email

🔗 Link Safety Analysis - Detects phishing, malware, and credential harvesting

Additional Security Features



🔐 Encryption (AES-256) - Protects sensitive data at rest

🔒 PII Anonymization - Masks personal info before API calls

📋 Audit Logging - Complete trail of all operations

📊 Privacy Dashboard - Transparent data processing metrics

📊 Security Score: 100/100



✅ PII Anonymization: 30/30 points

✅ Audit Logging: 25/25 points

✅ Encryption: 25/25 points

✅ API Monitoring: 20/20 points

🚀 All Commands



Email Scanning



# Basic scan

python main.py scan --limit 10# Verbose mode with details

python main.py scan --limit 5 --verbose# Auto-move spam to spam folder

python main.py scan --limit 10 --auto-move-spam



Privacy & Security



# View privacy dashboard

python main.py privacy --days 7# Export audit log

python main.py audit --output audit.json --days 30# Run security demo

python quick_demo.py



Statistics



# View spam statistics

python main.py stats --days 7# Export to CSV

python main.py export csv --output report.csv --days 30# Export to JSON

python main.py export json --output report.json --days 30



Real-time Monitoring



# Monitor inbox every 5 minutes

python main.py monitor --interval 300# Monitor with auto-spam removal

python main.py monitor --interval 300 --auto-move-spam# Monitor with desktop notifications

python main.py monitor --interval 300 --notify



🏗️ Architecture



pymultiguard-1/

├── security/

│ ├── encryption.py # AES-256 encryption

│ ├── pii_anonymizer.py # PII detection & masking

│ ├── audit_logger.py # Comprehensive logging

│ └── __init__.py

├── privacy_dashboard.py # Visual security dashboard

├── groq_spam_classifier.py # AI spam detection

├── main.py # Main application

├── quick_demo.py # Security features demo

├── audit_log.db # Security audit database

└── spam_stats.db # Spam statistics



🔬 Technical Stack



Language: Python 3.13

Encryption: cryptography (Fernet/AES-256)

AI Model: Groq API (llama-3.1-8b-instant)

Database: SQLite

Email Protocol: IMAP (Gmail)

📈 What Makes This Special



Privacy Protection



PII Detection: Automatically finds emails, phones, names

Anonymization: Masks sensitive data BEFORE sending to AI

100% Protection Rate: All PII anonymized

Security Implementation



AES-256 Encryption: Industry-standard encryption

Audit Trails: Every operation logged with timestamps

API Monitoring: Track all external data sharing

Security Score: Measurable security metrics

Transparency



Privacy Dashboard: See exactly what data is processed

API Usage Stats: Token counts and cost estimates

Data Retention: Email content NOT stored permanently

Exportable Logs: Compliance-ready audit trails

🎓 Information Security Principles



✅ Confidentiality - Encryption protects data at rest

✅ Integrity - Audit logs ensure accountability

✅ Availability - Real-time monitoring keeps system running

✅ Privacy-by-Design - PII anonymized before external processing

✅ Transparency - Users see all data processing

✅ Compliance - GDPR-ready audit trails

📊 Live Demo Results



Security Score: 100/100

PII Detected: 6 items (emails, phones, names)

PII Anonymized: 100%

API Calls Logged: Yes

Audit Trail: Complete

Encryption: Active



🎯 Use Cases



Personal Email Protection - Scan your inbox safely

Privacy-Conscious AI - Use AI without exposing personal data

Compliance Demonstration - Show GDPR-ready implementation

Security Education - Learn production security practices

📝 Configuration



Edit .env file:

EMAIL_ADDRESS=your_email@gmail.comEMAIL_PASSWORD=your_app_passwordIMAP_HOST=imap.gmail.comIMAP_PORT=993OPENAI_API_KEY=your_groq_api_keyMODEL_NAME=llama-3.1-8b-instant



🔐 Security Best Practices Implemented



Never store email content - Processed in memory only

Anonymize before external calls - PII never leaves system

Encrypt sensitive credentials - AES-256 encryption

Log all operations - Complete audit trail

Measure security - Quantifiable security score

Transparent processing - Users see everything

🏆 Project Highlights



Production-Grade: Not a prototype, ready for real use

Privacy-First: PII protection built-in from day one

Measurable: 100/100 security score

Transparent: Complete visibility into data processing

Compliant: GDPR-ready audit trails

Educational: Demonstrates real-world security practices
