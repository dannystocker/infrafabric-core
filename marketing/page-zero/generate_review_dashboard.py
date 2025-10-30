#!/usr/bin/env python3
"""
InfraFabric Human Review Dashboard Generator
Creates an HTML dashboard for reviewing verification results
"""

import csv
import json
from pathlib import Path
from datetime import datetime

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InfraFabric Contact Verification Review Dashboard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #7f8c8d;
            margin-bottom: 30px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card.green {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        .stat-card.yellow {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .stat-card.red {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }
        .stat-value {
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .stat-label {
            font-size: 14px;
            opacity: 0.9;
        }
        .section {
            margin-bottom: 40px;
        }
        .section-title {
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }
        .contact-card {
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        .contact-card.quick-review {
            border-left-color: #f39c12;
        }
        .contact-card.manual-review {
            border-left-color: #e74c3c;
        }
        .contact-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .contact-name {
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
        }
        .confidence-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
        }
        .confidence-badge.high {
            background: #2ecc71;
            color: white;
        }
        .confidence-badge.medium {
            background: #f39c12;
            color: white;
        }
        .confidence-badge.low {
            background: #e74c3c;
            color: white;
        }
        .contact-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }
        .info-item {
            color: #555;
        }
        .info-label {
            font-weight: bold;
            color: #2c3e50;
            margin-right: 8px;
        }
        .source-link {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            margin-right: 10px;
            margin-top: 10px;
        }
        .source-link:hover {
            background: #2980b9;
        }
        .audit-link {
            display: inline-block;
            background: #95a5a6;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            margin-top: 10px;
        }
        .audit-link:hover {
            background: #7f8c8d;
        }
        .action-buttons {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            margin-right: 10px;
            border-radius: 4px;
            text-decoration: none;
            font-weight: bold;
            cursor: pointer;
        }
        .btn-approve {
            background: #2ecc71;
            color: white;
        }
        .btn-reject {
            background: #e74c3c;
            color: white;
        }
        .btn-research {
            background: #3498db;
            color: white;
        }
        .filter-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .filter-tab {
            padding: 10px 20px;
            background: #ecf0f1;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }
        .filter-tab.active {
            background: #3498db;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 InfraFabric Contact Verification Review</h1>
        <p class="subtitle">Generated: {generation_time} | Total Contacts: {total_contacts}</p>

        <div class="stats">
            <div class="stat-card green">
                <div class="stat-value">{auto_verified}</div>
                <div class="stat-label">Auto-Verified</div>
                <div class="stat-label" style="font-size: 12px; margin-top: 5px;">Score ≥ 80</div>
            </div>
            <div class="stat-card yellow">
                <div class="stat-value">{quick_review}</div>
                <div class="stat-label">Quick Review</div>
                <div class="stat-label" style="font-size: 12px; margin-top: 5px;">Score 50-79</div>
            </div>
            <div class="stat-card red">
                <div class="stat-value">{manual_review}</div>
                <div class="stat-label">Manual Review</div>
                <div class="stat-label" style="font-size: 12px; margin-top: 5px;">Score < 50</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{avg_confidence:.0f}%</div>
                <div class="stat-label">Avg Confidence</div>
            </div>
        </div>

        <!-- Auto-Verified Section -->
        <div class="section">
            <h2 class="section-title">✅ Auto-Verified Contacts ({auto_verified})</h2>
            <p style="color: #27ae60; margin-bottom: 20px;">These contacts have high confidence scores (≥80) and are ready to use.</p>
            {auto_verified_html}
        </div>

        <!-- Quick Review Section -->
        <div class="section">
            <h2 class="section-title">⚠️ Quick Review Needed ({quick_review})</h2>
            <p style="color: #f39c12; margin-bottom: 20px;">These contacts need a quick human verification (~1 min each). Click the source link to verify.</p>
            {quick_review_html}
        </div>

        <!-- Manual Review Section -->
        <div class="section">
            <h2 class="section-title">❌ Manual Review Required ({manual_review})</h2>
            <p style="color: #e74c3c; margin-bottom: 20px;">These contacts need deep manual research. Low confidence scores or missing data.</p>
            {manual_review_html}
        </div>
    </div>

    <script>
        // Add interaction for approve/reject buttons
        document.querySelectorAll('.btn-approve, .btn-reject').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const card = this.closest('.contact-card');
                const action = this.classList.contains('btn-approve') ? 'APPROVED' : 'REJECTED';
                if (confirm(`Mark this contact as ${action}?`)) {
                    card.style.opacity = '0.5';
                    card.innerHTML = card.innerHTML + `<div style="margin-top: 15px; padding: 10px; background: ${action === 'APPROVED' ? '#2ecc71' : '#e74c3c'}; color: white; border-radius: 4px; text-align: center;"><strong>${action}</strong> - Update CSV manually</div>`;
                }
            });
        });
    </script>
</body>
</html>
"""

def generate_contact_card(contact, audit_dir):
    """Generate HTML for a single contact card"""
    name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}"
    org = contact.get('organization', '')
    role = contact.get('role_title', '')
    confidence = float(contact.get('confidence_score', 0))
    status = contact.get('verified_status', 'unknown')
    review_type = contact.get('verified_by', 'unknown')
    source_url = contact.get('verified_source_url', '')
    signals = contact.get('signals_count', 0)

    # Confidence badge
    if confidence >= 80:
        badge_class = 'high'
    elif confidence >= 50:
        badge_class = 'medium'
    else:
        badge_class = 'low'

    # Card class
    if review_type == 'quick_review':
        card_class = 'quick-review'
    elif review_type == 'manual_review':
        card_class = 'manual-review'
    else:
        card_class = ''

    # Find audit log
    audit_file = None
    if audit_dir:
        audit_path = Path(audit_dir)
        # Try to find matching audit log
        for log_file in audit_path.glob('audit_*.json'):
            try:
                with open(log_file) as f:
                    log_data = json.load(f)
                    if (log_data['contact']['first_name'] == contact.get('first_name') and
                        log_data['contact']['last_name'] == contact.get('last_name')):
                        audit_file = log_file
                        break
            except:
                continue

    audit_link_html = ''
    if audit_file:
        audit_link_html = f'<a href="{audit_file}" class="audit-link" target="_blank">📋 View Audit Log</a>'

    # Action buttons (for review items)
    action_buttons = ''
    if review_type in ['quick_review', 'manual_review']:
        action_buttons = f'''
        <div class="action-buttons">
            <button class="btn btn-approve" onclick="return false;">✓ Approve</button>
            <button class="btn btn-reject" onclick="return false;">✗ Reject</button>
            <a href="https://www.linkedin.com/search/results/people/?keywords={name.replace(' ', '+')}" class="btn btn-research" target="_blank">🔍 Research</a>
        </div>
        '''

    html = f'''
    <div class="contact-card {card_class}">
        <div class="contact-header">
            <div class="contact-name">{name}</div>
            <span class="confidence-badge {badge_class}">{confidence:.0f}%</span>
        </div>
        <div class="contact-info">
            <div class="info-item">
                <span class="info-label">Organization:</span>
                {org}
            </div>
            <div class="info-item">
                <span class="info-label">Role:</span>
                {role}
            </div>
            <div class="info-item">
                <span class="info-label">Status:</span>
                {status}
            </div>
            <div class="info-item">
                <span class="info-label">Signals Found:</span>
                {signals}
            </div>
        </div>
        <div>
            {f'<a href="{source_url}" class="source-link" target="_blank">🔗 View Source</a>' if source_url else '<span style="color: #e74c3c;">⚠️ No source URL found</span>'}
            {audit_link_html}
        </div>
        {action_buttons}
    </div>
    '''
    return html

def generate_dashboard(csv_file, audit_dir, output_html):
    """Generate HTML dashboard from verification results"""

    # Read CSV
    contacts = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(row)

    # Categorize contacts
    auto_verified = []
    quick_review = []
    manual_review = []

    for contact in contacts:
        review_type = contact.get('verified_by', '')
        if review_type == 'auto':
            auto_verified.append(contact)
        elif review_type == 'quick_review':
            quick_review.append(contact)
        else:
            manual_review.append(contact)

    # Calculate stats
    total = len(contacts)
    avg_confidence = sum(float(c.get('confidence_score', 0)) for c in contacts) / total if total > 0 else 0

    # Generate HTML sections
    auto_verified_html = ''.join(generate_contact_card(c, audit_dir) for c in auto_verified)
    if not auto_verified_html:
        auto_verified_html = '<p style="color: #7f8c8d;">No auto-verified contacts yet.</p>'

    quick_review_html = ''.join(generate_contact_card(c, audit_dir) for c in quick_review)
    if not quick_review_html:
        quick_review_html = '<p style="color: #7f8c8d;">No contacts need quick review.</p>'

    manual_review_html = ''.join(generate_contact_card(c, audit_dir) for c in manual_review)
    if not manual_review_html:
        manual_review_html = '<p style="color: #7f8c8d;">No contacts need manual review.</p>'

    # Fill template
    html = HTML_TEMPLATE.format(
        generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_contacts=total,
        auto_verified=len(auto_verified),
        quick_review=len(quick_review),
        manual_review=len(manual_review),
        avg_confidence=avg_confidence,
        auto_verified_html=auto_verified_html,
        quick_review_html=quick_review_html,
        manual_review_html=manual_review_html
    )

    # Write output
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Dashboard generated: {output_html}")
    print(f"   Total contacts: {total}")
    print(f"   Auto-verified: {len(auto_verified)}")
    print(f"   Quick review: {len(quick_review)}")
    print(f"   Manual review: {len(manual_review)}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Generate HTML review dashboard from verification results')
    parser.add_argument('--csv', required=True, help='Verified contacts CSV file')
    parser.add_argument('--audit-dir', default='./verification-audit-logs', help='Audit logs directory')
    parser.add_argument('--out', default='verification-dashboard.html', help='Output HTML file')

    args = parser.parse_args()

    generate_dashboard(args.csv, args.audit_dir, args.out)
