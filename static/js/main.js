// PyMultiGuard Frontend JavaScript

const analyzeBtn = document.getElementById('analyzeBtn');
const btnText = document.getElementById('btnText');
const btnLoader = document.getElementById('btnLoader');
const statusText = document.getElementById('statusText');
const resultsContainer = document.getElementById('resultsContainer');

// Analyze button click handler
analyzeBtn.addEventListener('click', async () => {
    // Disable button and show loader
    analyzeBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-block';
    statusText.textContent = 'Fetching emails from Gmail...';

    // Clear previous results
    resultsContainer.innerHTML = '<div class="loading"><div class="loading-spinner"></div><p>Analyzing emails... This may take 30-60 seconds</p></div>';

    try {
        // Call API
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ limit: 5 })
        });

        const data = await response.json();

        if (data.success) {
            statusText.textContent = `Analysis complete! Found ${data.total_emails} emails`;
            displayResults(data.results);
        } else {
            statusText.textContent = 'Error occurred';
            showError(data.error);
        }
    } catch (error) {
        statusText.textContent = 'Connection error';
        showError('Failed to connect to server: ' + error.message);
    } finally {
        // Re-enable button
        analyzeBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
});

// Display results
function displayResults(results) {
    resultsContainer.innerHTML = '';

    results.forEach((email, index) => {
        const emailCard = createEmailCard(email, index + 1);
        resultsContainer.appendChild(emailCard);
    });
}

// Create email card
function createEmailCard(email, number) {
    const card = document.createElement('div');
    card.className = 'email-card';

    // Email header
    const header = `
        <div class="email-header">
            <div class="email-number">📧 Email #${number}</div>
            <div class="email-info"><strong>From:</strong> ${escapeHtml(email.from)}</div>
            <div class="email-info"><strong>Subject:</strong> ${escapeHtml(email.subject)}</div>
            <div class="email-info"><strong>Category:</strong> ${email.category}</div>
        </div>
    `;

    // Spam classification
    const classification = email.classification;
    const isSpam = classification.is_spam;
    const classType = isSpam ? 'spam' : 'safe';
    const classLabel = isSpam ? '⚠️ SPAM' : '✓ SAFE';

    const classificationHtml = `
        <div class="classification ${classType}">
            ${classLabel} - Confidence: ${classification.confidence}%
        </div>
        <p style="color: #8b949e; margin: 10px 0;">${escapeHtml(classification.reason)}</p>
    `;

    // Sender Intelligence
    const sender = email.sender_intelligence;
    const senderHtml = `
        <div class="section">
            <div class="section-title">🔍 Sender Intelligence</div>
            <div class="section-content">
                <p><strong>Company:</strong> ${escapeHtml(sender.company_name)}</p>
                <p><strong>Industry:</strong> ${escapeHtml(sender.industry)}</p>
                <p><strong>Legitimacy:</strong> ${escapeHtml(sender.legitimacy.toUpperCase())}</p>
                <p><strong>Description:</strong> ${escapeHtml(sender.description)}</p>
            </div>
        </div>
    `;

    // Data Collection Analysis
    const dataCol = email.data_collection;
    const riskLevel = dataCol.risk_assessment.level;
    const riskClass = `risk-${riskLevel}`;

    const dataColHtml = `
        <div class="section">
            <div class="section-title">📊 Data Collection Analysis</div>
            <div class="section-content">
                <p><strong>Data Points Collected:</strong> ${dataCol.data_count}</p>
                <p><strong>Personalization Level:</strong> ${dataCol.personalization_level.toUpperCase()}</p>
                <p><strong>Tracking Detected:</strong> ${dataCol.is_tracking ? 'YES' : 'NO'}</p>
                <p><strong>Privacy Risk:</strong> <span class="${riskClass}">${riskLevel.toUpperCase()}</span></p>
                <p>${escapeHtml(dataCol.risk_assessment.message)}</p>
            </div>
        </div>
    `;

    // Email Source Tracking
    const source = email.email_source;
    const sourceRiskClass = `risk-${source.risk_level}`;

    const sourceHtml = `
        <div class="section">
            <div class="section-title">🎯 Email Source Tracking</div>
            <div class="section-content">
                <p><strong>Source:</strong> ${escapeHtml(source.source)}</p>
                <p><strong>Method:</strong> ${escapeHtml(source.method)}</p>
                <p><strong>Confidence:</strong> ${source.confidence}%</p>
                <p><strong>Risk Level:</strong> <span class="${sourceRiskClass}">${source.risk_level.toUpperCase()}</span></p>
                <p><strong>Explanation:</strong> ${escapeHtml(source.explanation)}</p>
            </div>
        </div>
    `;

    // Link Safety Analysis
    const links = email.link_safety;
    let linksHtml = `
        <div class="section">
            <div class="section-title">🔗 Link Safety Analysis</div>
            <div class="section-content">
                <p><strong>Total Links:</strong> ${links.total_links}</p>
    `;

    if (links.dangerous_links > 0) {
        linksHtml += `<p><strong>Dangerous Links:</strong> <span class="risk-high">${links.dangerous_links}</span></p>`;
    }
    if (links.suspicious_links > 0) {
        linksHtml += `<p><strong>Suspicious Links:</strong> <span class="risk-medium">${links.suspicious_links}</span></p>`;
    }
    if (links.safe_links > 0) {
        linksHtml += `<p><strong>Safe Links:</strong> <span class="risk-low">${links.safe_links}</span></p>`;
    }

    // Show first 3 links
    if (links.analysis && links.analysis.length > 0) {
        linksHtml += '<div style="margin-top: 15px;">';
        links.analysis.slice(0, 3).forEach(link => {
            const safetyClass = link.safety_level;
            linksHtml += `
                <div class="link-item ${safetyClass}">
                    <div class="link-url">${escapeHtml(link.url.substring(0, 80))}${link.url.length > 80 ? '...' : ''}</div>
                    <div class="link-safety">Safety: ${link.safety_level.toUpperCase()}</div>
                    <div style="color: #8b949e; font-size: 0.9em;">
                        <p><strong>What Happens:</strong> ${escapeHtml(link.what_happens)}</p>
                        <p><strong>Recommendation:</strong> ${escapeHtml(link.recommendation)}</p>
                    </div>
                </div>
            `;
        });
        linksHtml += '</div>';
    }

    linksHtml += '</div></div>';

    // Combine all sections
    card.innerHTML = header + classificationHtml + senderHtml + dataColHtml + sourceHtml + linksHtml;

    return card;
}

// Show error message
function showError(message) {
    resultsContainer.innerHTML = `
        <div class="error-message">
            <h3>❌ Error</h3>
            <p>${escapeHtml(message)}</p>
            <p style="margin-top: 10px; font-size: 0.9em;">Please check your configuration and try again.</p>
        </div>
    `;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
