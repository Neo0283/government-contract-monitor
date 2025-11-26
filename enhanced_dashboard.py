#!/usr/bin/env python3
"""
Enhanced Government Contract Dashboard
Specifically designed for cronyism detection and pattern analysis
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from flask import Flask, render_template_string, jsonify, request
import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

app = Flask(__name__)

class CronyismDashboard:
    def __init__(self, db_path: str = "government_monitor.db"):
        self.db_path = db_path
    
    def get_cronyism_summary(self):
        """Get cronyism-focused summary statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Basic stats
        cursor.execute('SELECT COUNT(*), SUM(award_amount), COUNT(DISTINCT recipient_name) FROM contracts')
        total_contracts, total_spending, unique_companies = cursor.fetchone()
        
        # Emergency/No-bid contracts
        cursor.execute('''
            SELECT COUNT(*) FROM contracts 
            WHERE LOWER(competition_type) LIKE '%sole%source%' 
               OR LOWER(competition_type) LIKE '%no%bid%'
               OR LOWER(description) LIKE '%emergency%'
        ''')
        emergency_contracts = cursor.fetchone()[0]
        
        # Recent high-value contracts
        cursor.execute('''
            SELECT COUNT(*) FROM contracts 
            WHERE award_amount > 50000000 
            AND award_date >= date('now', '-180 days')
        ''')
        recent_large = cursor.fetchone()[0]
        
        # Rapid accumulation companies
        cursor.execute('''
            SELECT COUNT(DISTINCT recipient_name) FROM (
                SELECT recipient_name, COUNT(*) as contract_count
                FROM contracts 
                WHERE award_date >= date('now', '-90 days')
                GROUP BY recipient_name
                HAVING COUNT(*) >= 3
            )
        ''')
        rapid_accum = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_contracts': total_contracts or 0,
            'total_spending': total_spending or 0,
            'unique_companies': unique_companies or 0,
            'emergency_contracts': emergency_contracts or 0,
            'recent_large_contracts': recent_large or 0,
            'rapid_accumulation_companies': rapid_accum or 0,
            'emergency_percentage': round((emergency_contracts / max(total_contracts, 1)) * 100, 1)
        }
    
    def get_watchlist_companies(self):
        """Get contracts for companies on cronyism watchlists"""
        watchlist_patterns = [
            'TRUMP', 'KUSHNER', 'TRUTH SOCIAL', 'DJT',
            'PALANTIR', 'CLEARVIEW', 'ANDURIL',
            'SPACEX', 'TESLA', 'NEURALINK'
        ]
        
        conn = sqlite3.connect(self.db_path)
        results = []
        
        for pattern in watchlist_patterns:
            df = pd.read_sql_query('''
                SELECT recipient_name, COUNT(*) as contract_count, 
                       SUM(award_amount) as total_amount,
                       MAX(award_date) as latest_contract
                FROM contracts 
                WHERE UPPER(recipient_name) LIKE ?
                GROUP BY recipient_name
                ORDER BY total_amount DESC
            ''', conn, params=[f'%{pattern}%'])
            
            for _, row in df.iterrows():
                results.append({
                    'company': row['recipient_name'],
                    'contract_count': row['contract_count'],
                    'total_amount': row['total_amount'],
                    'latest_contract': row['latest_contract'],
                    'watchlist_category': pattern
                })
        
        conn.close()
        return results
    
    def get_emergency_contracts(self):
        """Get emergency/no-bid contracts for analysis (last 12 months)"""
        conn = sqlite3.connect(self.db_path)
        
        df = pd.read_sql_query('''
            SELECT recipient_name, award_amount, awarding_agency, 
                   award_date, competition_type, description
            FROM contracts 
            WHERE (LOWER(competition_type) LIKE '%sole%source%' 
                   OR LOWER(competition_type) LIKE '%no%bid%'
                   OR LOWER(description) LIKE '%emergency%'
                   OR LOWER(description) LIKE '%urgent%')
            AND award_date >= date('now', '-12 months')
            ORDER BY award_amount DESC
            LIMIT 20
        ''', conn)
        
        conn.close()
        return df.to_dict('records')
    
    def get_recent_contracts_table(self):
        """Get table of recent contracts"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                recipient_name,
                award_amount,
                awarding_agency,
                award_date,
                competition_type,
                substr(description, 1, 100) as description
            FROM contracts 
            WHERE award_date >= date('now', '-30 days')
            ORDER BY award_date DESC
            LIMIT 50
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return "<p>No contracts in the last 30 days</p>"
        
        # Format amounts
        df['award_amount'] = df['award_amount'].apply(lambda x: f"${x:,.0f}")
        
        # Rename columns for display
        df.columns = ['Company', 'Amount', 'Agency', 'Date', 'Competition', 'Description']
        
        return df.to_html(classes='table', index=False, escape=False)
    
    def get_agency_risk_analysis(self):
        """Analyze agencies by risk factors (last 12 months)"""
        conn = sqlite3.connect(self.db_path)
        
        df = pd.read_sql_query('''
            SELECT 
                awarding_agency,
                COUNT(*) as total_contracts,
                SUM(award_amount) as total_amount,
                COUNT(CASE WHEN LOWER(competition_type) LIKE '%sole%source%' 
                           OR LOWER(competition_type) LIKE '%no%bid%' 
                           THEN 1 END) as no_bid_contracts,
                AVG(award_amount) as avg_amount
            FROM contracts 
            WHERE award_date >= date('now', '-12 months')
            GROUP BY awarding_agency
            HAVING COUNT(*) >= 5
            ORDER BY total_amount DESC
            LIMIT 15
        ''', conn)
        
        # Calculate risk scores
        results = []
        for _, row in df.iterrows():
            no_bid_rate = (row['no_bid_contracts'] / row['total_contracts']) * 100
            risk_score = min(100, no_bid_rate * 2 + (row['avg_amount'] / 10000000))  # Simplified risk scoring
            
            results.append({
                'agency': row['awarding_agency'],
                'total_contracts': row['total_contracts'],
                'total_amount': row['total_amount'],
                'no_bid_rate': round(no_bid_rate, 1),
                'avg_amount': row['avg_amount'],
                'risk_score': round(risk_score, 1)
            })
        
        conn.close()
        return sorted(results, key=lambda x: x['risk_score'], reverse=True)
    
    def get_timeline_analysis(self):
        """Get timeline of concerning contract patterns"""
        conn = sqlite3.connect(self.db_path)
        
        df = pd.read_sql_query('''
            SELECT 
                DATE(award_date, 'start of month') as month,
                COUNT(*) as total_contracts,
                SUM(award_amount) as total_amount,
                COUNT(CASE WHEN LOWER(competition_type) LIKE '%sole%source%' 
                           OR LOWER(competition_type) LIKE '%no%bid%' 
                           THEN 1 END) as no_bid_contracts,
                COUNT(CASE WHEN award_amount > 50000000 THEN 1 END) as large_contracts
            FROM contracts 
            WHERE award_date >= date('now', '-24 months')
            GROUP BY month
            ORDER BY month
        ''', conn)
        
        conn.close()
        return df.to_dict('records')

dashboard_data = CronyismDashboard()

# Enhanced HTML Template with cronyism focus
CRONYISM_DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Government Contract Cronyism Monitor</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #333;
            min-height: 100vh;
        }
        .header {
            background: rgba(255,255,255,0.95);
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            margin-bottom: 20px;
        }
        .header h1 { 
            margin: 0; 
            color: #1e3c72; 
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p { 
            margin: 10px 0 0 0; 
            color: #666; 
            font-size: 1.1em;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 0 20px;
        }
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .stat-card { 
            background: white; 
            padding: 25px; 
            border-radius: 12px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-left: 5px solid #1e3c72;
            transition: transform 0.2s;
        }
        .stat-card:hover { transform: translateY(-2px); }
        .stat-card.alert { border-left-color: #e74c3c; }
        .stat-card.warning { border-left-color: #f39c12; }
        .stat-number { 
            font-size: 2.2em; 
            font-weight: bold; 
            color: #1e3c72; 
            margin-bottom: 5px;
        }
        .stat-number.alert { color: #e74c3c; }
        .stat-number.warning { color: #f39c12; }
        .stat-label { 
            color: #666; 
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .stat-card.clickable {
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .stat-card.clickable:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        .click-hint {
            font-size: 0.8em;
            color: #888;
            margin-top: 5px;
            font-style: italic;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 12px;
            width: 80%;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 2px solid #eee;
            padding-bottom: 15px;
        }
        .modal-title {
            color: #1e3c72;
            font-size: 1.5em;
            font-weight: 500;
            margin: 0;
        }
        .close {
            color: #aaa;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            line-height: 1;
        }
        .close:hover {
            color: #e74c3c;
        }
        .contract-item {
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #3498db;
            background: #f8f9fa;
        }
        .contract-item.high-value {
            border-left-color: #e74c3c;
            background: #fdf2f2;
        }
        .contract-company {
            font-weight: bold;
            font-size: 1.1em;
            color: #1e3c72;
        }
        .contract-amount {
            font-size: 1.2em;
            font-weight: bold;
            color: #e74c3c;
        }
        .contract-details {
            margin-top: 8px;
            color: #666;
            font-size: 0.9em;
        }
        .chart-container { 
            background: white; 
            padding: 30px; 
            margin-bottom: 25px; 
            border-radius: 12px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .chart-container h3 { 
            margin: 0 0 20px 0; 
            color: #1e3c72;
            font-size: 1.4em;
            font-weight: 500;
        }
        .alerts-section { 
            background: white; 
            padding: 30px; 
            border-radius: 12px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin-bottom: 25px;
        }
        .alert-item { 
            padding: 15px; 
            margin: 12px 0; 
            border-radius: 8px;
            border-left: 4px solid #e74c3c;
            background: #fdf2f2;
        }
        .alert-item.warning { 
            border-left-color: #f39c12; 
            background: #fef9e7;
        }
        .alert-item.info { 
            border-left-color: #3498db; 
            background: #f0f8ff;
        }
        .watchlist-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        .watchlist-table th, .watchlist-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        .watchlist-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #1e3c72;
        }
        .refresh-btn { 
            background: linear-gradient(135deg, #1e3c72, #2a5298); 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 1em;
            transition: all 0.2s;
        }
        .refresh-btn:hover { 
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        .refresh-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .last-updated {
            margin-left: 20px;
            color: #666;
            font-size: 0.9em;
            font-style: italic;
        }
        .risk-high { color: #e74c3c; font-weight: bold; }
        .risk-medium { color: #f39c12; font-weight: bold; }
        .risk-low { color: #27ae60; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Government Contract Cronyism Monitor</h1>
        <p>Advanced pattern detection for corruption and preferential treatment</p>
        <button class="refresh-btn" onclick="refreshAnalysis()" id="refreshBtn">🔄 Refresh Analysis</button>
        <span class="last-updated" id="lastUpdated">Last updated: {{ current_time }}</span>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_contracts }}</div>
                <div class="stat-label">Total Contracts Monitored</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${{ "%.1f"|format(stats.total_spending/1000000000) }}B</div>
                <div class="stat-label">Total Contract Value</div>
            </div>
            <div class="stat-card alert">
                <div class="stat-number alert">{{ stats.emergency_contracts }}</div>
                <div class="stat-label">Emergency/No-Bid Contracts</div>
            </div>
            <div class="stat-card warning clickable" onclick="showRapidAccumulation()">
                <div class="stat-number warning">{{ stats.rapid_accumulation_companies }}</div>
                <div class="stat-label">Rapid Accumulation Companies</div>
                <div class="click-hint">Click to view details</div>
            </div>
            <div class="stat-card alert clickable" onclick="showLargeContracts()">
                <div class="stat-number alert">{{ stats.recent_large_contracts }}</div>
                <div class="stat-label">Large Contracts (6mo, >$50M)</div>
                <div class="click-hint">Click to view details</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.emergency_percentage }}%</div>
                <div class="stat-label">Emergency Contract Rate</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>📊 Contract Timeline Analysis</h3>
            <div id="timeline-chart"></div>
        </div>
        
        <div class="chart-container">
            <h3>🏛️ Agency Risk Analysis</h3>
            <div id="agency-risk-chart"></div>
        </div>
        
        <div class="alerts-section">
            <h3>📋 Recent Contracts (Last 30 Days)</h3>
            <div id="recent-contracts-container">
                <p>Loading recent contracts...</p>
            </div>
        </div>
        
        <div class="alerts-section">
            <h3>📋 Recent Contracts (Last 30 Days)</h3>
            <div id="recent-contracts-container">
                <p>Loading recent contracts...</p>
            </div>
        </div>
        
        <div class="alerts-section">
            <h3>👁️ Watchlist Companies</h3>
            <table class="watchlist-table">
                <thead>
                    <tr>
                        <th>Company</th>
                        <th>Contracts</th>
                        <th>Total Value</th>
                        <th>Latest Contract</th>
                        <th>Category</th>
                    </tr>
                </thead>
                <tbody>
                    {% for company in watchlist_companies %}
                    <tr>
                        <td><strong>{{ company.company }}</strong></td>
                        <td>{{ company.contract_count }}</td>
                        <td>${{ "%.1f"|format(company.total_amount/1000000) }}M</td>
                        <td>{{ company.latest_contract }}</td>
                        <td><span class="risk-high">{{ company.watchlist_category }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="alerts-section">
            <h3>🚨 Emergency/No-Bid Contracts (Last 12 Months)</h3>
            {% for contract in emergency_contracts[:10] %}
            <div class="alert-item">
                <strong>{{ contract.recipient_name }}</strong> - ${{ "%.1f"|format(contract.award_amount/1000000) }}M
                <br><small>{{ contract.awarding_agency }} | {{ contract.award_date }} | {{ contract.competition_type }}</small>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <!-- Modal for Rapid Accumulation Companies -->
    <div id="rapidAccumulationModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title">🚨 Rapid Accumulation Companies</h2>
                <span class="close" onclick="closeModal('rapidAccumulationModal')">&times;</span>
            </div>
            <div id="rapidAccumulationContent">
                <p>Loading rapid accumulation data...</p>
            </div>
        </div>
    </div>
    
    <!-- Modal for Large Contracts -->
    <div id="largeContractsModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title">💰 Large Contracts (>$50M)</h2>
                <span class="close" onclick="closeModal('largeContractsModal')">&times;</span>
            </div>
            <div id="largeContractsContent">
                <p>Loading large contracts data...</p>
            </div>
        </div>
    </div>
    
    <script>
        // Timeline chart
        var timelineData = {{ timeline_data | safe }};
        
        var contractsTrace = {
            x: timelineData.map(d => d.month),
            y: timelineData.map(d => d.total_contracts),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Total Contracts',
            line: {color: '#3498db', width: 3}
        };
        
        var noBidTrace = {
            x: timelineData.map(d => d.month),
            y: timelineData.map(d => d.no_bid_contracts),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'No-Bid Contracts',
            line: {color: '#e74c3c', width: 3}
        };
        
        var timelineLayout = {
            title: '',
            xaxis: {title: 'Month'},
            yaxis: {title: 'Number of Contracts'},
            showlegend: true,
            legend: {x: 0, y: 1}
        };
        
        Plotly.newPlot('timeline-chart', [contractsTrace, noBidTrace], timelineLayout);
        
        // Agency risk chart
        var agencyData = {{ agency_risk_data | safe }};
        
        var agencyTrace = {
            x: agencyData.map(d => d.risk_score),
            y: agencyData.map(d => d.agency.substring(0, 30)),
            type: 'bar',
            orientation: 'h',
            marker: {
                color: agencyData.map(d => d.risk_score > 50 ? '#e74c3c' : d.risk_score > 25 ? '#f39c12' : '#27ae60')
            }
        };
        
        var agencyLayout = {
            title: '',
            xaxis: {title: 'Risk Score'},
            yaxis: {title: ''},
            margin: {l: 250}
        };
        
        Plotly.newPlot('agency-risk-chart', [agencyTrace], agencyLayout);
        
        // Modal functions
        function showRapidAccumulation() {
            document.getElementById('rapidAccumulationModal').style.display = 'block';
            fetch('/api/rapid-accumulation')
                .then(response => response.json())
                .then(data => {
                    let content = '<div>';
                    if (data.length === 0) {
                        content += '<p>No rapid accumulation patterns detected in the last 90 days.</p>';
                    } else {
                        data.forEach(company => {
                            content += `
                                <div class="contract-item">
                                    <div class="contract-company">${company.company}</div>
                                    <div class="contract-amount">${company.contract_count} contracts - $${(company.total_amount/1000000).toFixed(1)}M</div>
                                    <div class="contract-details">
                                        Latest: ${company.latest_contract} | 
                                        Avg Amount: $${(company.avg_amount/1000000).toFixed(1)}M |
                                        Pattern: ${company.contract_count} contracts in ${company.days_span} days
                                    </div>
                                </div>
                            `;
                        });
                    }
                    content += '</div>';
                    document.getElementById('rapidAccumulationContent').innerHTML = content;
                })
                .catch(error => {
                    document.getElementById('rapidAccumulationContent').innerHTML = 
                        '<p>Error loading rapid accumulation data: ' + error + '</p>';
                });
        }
        
        function showLargeContracts() {
            document.getElementById('largeContractsModal').style.display = 'block';
            fetch('/api/large-contracts')
                .then(response => response.json())
                .then(data => {
                    let content = '<div>';
                    if (data.length === 0) {
                        content += '<p>No large contracts (>$50M) found in the last 6 months.</p>';
                    } else {
                        data.forEach(contract => {
                            content += `
                                <div class="contract-item high-value">
                                    <div class="contract-company">${contract.recipient_name}</div>
                                    <div class="contract-amount">$${(contract.award_amount/1000000).toFixed(1)}M</div>
                                    <div class="contract-details">
                                        Agency: ${contract.awarding_agency} | 
                                        Date: ${contract.award_date} | 
                                        Competition: ${contract.competition_type || 'Not specified'}
                                    </div>
                                    <div class="contract-details">
                                        Description: ${contract.description ? contract.description.substring(0, 200) + '...' : 'No description available'}
                                    </div>
                                </div>
                            `;
                        });
                    }
                    content += '</div>';
                    document.getElementById('largeContractsContent').innerHTML = content;
                })
                .catch(error => {
                    document.getElementById('largeContractsContent').innerHTML = 
                        '<p>Error loading large contracts data: ' + error + '</p>';
                });
        }
        
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
            }
        }
        
        // Refresh analysis function
        function refreshAnalysis() {
            const refreshBtn = document.getElementById('refreshBtn');
            const lastUpdated = document.getElementById('lastUpdated');
            
            // Show loading state
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '⏳ Refreshing...';
            
            // Refresh all data by reloading the page (ensures fresh database queries)
            setTimeout(() => {
                location.reload();
            }, 500);
        }
        
        // Load recent contracts
        function loadRecentContracts() {
            fetch('/api/recent-contracts')
                .then(response => response.json())
                .then(data => {
                    let html = '<table class="watchlist-table"><thead><tr>';
                    html += '<th>Company</th><th>Amount</th><th>Agency</th><th>Date</th><th>Competition</th><th>Description</th>';
                    html += '</tr></thead><tbody>';
                    
                    if (data.length === 0) {
                        html += '<tr><td colspan="6" style="text-align:center; padding:20px;">No contracts in the last 30 days. Run data collection to update.</td></tr>';
                    } else {
                        data.forEach(contract => {
                            html += '<tr>';
                            html += `<td><strong>${contract.recipient_name}</strong></td>`;
                            html += `<td>$${(contract.award_amount/1000000).toFixed(2)}M</td>`;
                            html += `<td style="font-size:0.85em;">${contract.awarding_agency}</td>`;
                            html += `<td>${contract.award_date}</td>`;
                            html += `<td style="font-size:0.85em;"><span class="risk-medium">${contract.competition_type || 'N/A'}</span></td>`;
                            html += `<td style="font-size:0.8em;">${contract.description ? contract.description.substring(0, 70) + '...' : 'No description'}</td>`;
                            html += '</tr>';
                        });
                    }
                    
                    html += '</tbody></table>';
                    document.getElementById('recent-contracts-container').innerHTML = html;
                })
                .catch(error => {
                    document.getElementById('recent-contracts-container').innerHTML = 
                        '<p style="color:red;">Error loading recent contracts: ' + error + '</p>';
                });
        }
        
        // Load recent contracts on page load
        window.addEventListener('DOMContentLoaded', loadRecentContracts);
        
        // Auto-refresh every 5 minutes
        setInterval(() => {
            const lastUpdated = document.getElementById('lastUpdated');
            lastUpdated.innerHTML = 'Auto-refreshing...';
            setTimeout(() => {
                location.reload();
            }, 1000);
        }, 300000); // 5 minutes
    </script>
</body>
</html>
"""

@app.route('/')
def cronyism_dashboard():
    from datetime import datetime
    
    stats = dashboard_data.get_cronyism_summary()
    watchlist_companies = dashboard_data.get_watchlist_companies()
    emergency_contracts = dashboard_data.get_emergency_contracts()
    agency_risk_data = dashboard_data.get_agency_risk_analysis()
    timeline_data = dashboard_data.get_timeline_analysis()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template_string(
        CRONYISM_DASHBOARD_HTML,
        stats=stats,
        watchlist_companies=watchlist_companies,
        emergency_contracts=emergency_contracts,
        agency_risk_data=json.dumps(agency_risk_data),
        timeline_data=json.dumps(timeline_data),
        current_time=current_time
    )

@app.route('/api/cronyism-summary')
def cronyism_summary_api():
    return jsonify(dashboard_data.get_cronyism_summary())

@app.route('/api/watchlist')
def watchlist_api():
    return jsonify(dashboard_data.get_watchlist_companies())

@app.route('/api/emergency-contracts')
def emergency_contracts_api():
    return jsonify(dashboard_data.get_emergency_contracts())

@app.route('/api/rapid-accumulation')
def rapid_accumulation_api():
    """Get companies with rapid contract accumulation"""
    conn = sqlite3.connect(dashboard_data.db_path)
    
    df = pd.read_sql_query('''
        SELECT 
            recipient_name,
            COUNT(*) as contract_count,
            SUM(award_amount) as total_amount,
            AVG(award_amount) as avg_amount,
            MIN(award_date) as first_contract,
            MAX(award_date) as latest_contract,
            JULIANDAY(MAX(award_date)) - JULIANDAY(MIN(award_date)) as days_span
        FROM contracts 
        WHERE award_date >= date('now', '-90 days')
        GROUP BY recipient_name
        HAVING COUNT(*) >= 2
        ORDER BY contract_count DESC, total_amount DESC
        LIMIT 20
    ''', conn)
    
    conn.close()
    
    results = []
    for _, row in df.iterrows():
        results.append({
            'company': row['recipient_name'],
            'contract_count': int(row['contract_count']),
            'total_amount': float(row['total_amount']),
            'avg_amount': float(row['avg_amount']),
            'first_contract': row['first_contract'],
            'latest_contract': row['latest_contract'],
            'days_span': int(row['days_span']) if row['days_span'] else 0
        })
    
    return jsonify(results)

@app.route('/api/large-contracts')
def large_contracts_api():
    """Get large contracts (>$50M) from last 6 months"""
    conn = sqlite3.connect(dashboard_data.db_path)
    
    df = pd.read_sql_query('''
        SELECT 
            recipient_name,
            award_amount,
            awarding_agency,
            award_date,
            competition_type,
            description
        FROM contracts 
        WHERE award_amount > 50000000
        AND award_date >= date('now', '-6 months')
        ORDER BY award_amount DESC
        LIMIT 50
    ''', conn)
    
    conn.close()
    return jsonify(df.to_dict('records'))

if __name__ == '__main__':
    print("🔍 Enhanced Cronyism Dashboard")
    print("=" * 40)
    print("Dashboard URL: http://127.0.0.1:8080")
    print("Press Ctrl+C to stop the server")
    print()
    app.run(debug=False, host='127.0.0.1', port=8080)
