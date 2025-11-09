#!/usr/bin/env python3
"""
Scenario-Based Government Contract Monitoring
Detects unusual patterns in emergency contracting and competitive bidding
Pattern analysis tool for independent verification and oversight
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ScenarioAlert:
    scenario_type: str
    severity: str
    company: str
    amount: float
    agency: str
    pattern_detected: str
    evidence: List[str]
    risk_score: int

class ScenarioMonitor:
    """Monitor for unusual contracting patterns and anomalies"""
    
    def __init__(self, db_path: str = "government_monitor.db", custom_watchlist: List[str] = None):
        self.db_path = db_path
        
        # User-configurable watchlist (optional)
        # Users can provide their own list of companies to monitor
        self.custom_watchlist = custom_watchlist or []
        
        # Industry categories for pattern analysis (non-accusatory)
        self.tech_sector_companies = [
            'PALANTIR', 'CLEARVIEW', 'ANDURIL', 'FACEBOOK', 'META',
            'GOOGLE', 'ALPHABET', 'AMAZON', 'MICROSOFT', 'ORACLE'
        ]
        
        self.defense_sector_companies = [
            'BOEING', 'LOCKHEED MARTIN', 'RAYTHEON', 'NORTHROP GRUMMAN',
            'GENERAL DYNAMICS', 'BAE SYSTEMS', 'L3HARRIS'
        ]
        
        self.financial_sector_companies = [
            'JPMORGAN', 'GOLDMAN SACHS', 'BLACKROCK', 'VANGUARD',
            'FIDELITY', 'BANK OF AMERICA', 'WELLS FARGO'
        ]
        
        # Emergency/crisis keywords
        self.emergency_keywords = [
            'emergency', 'crisis', 'urgent', 'national security', 'homeland security',
            'border security', 'cybersecurity', 'food security', 'energy security',
            'infrastructure protection', 'critical infrastructure'
        ]
        
        # No-bid/sole-source indicators
        self.no_bid_patterns = [
            'sole source', 'no bid', 'not competed', 'emergency procurement',
            'urgent requirement', 'national emergency', 'executive order'
        ]
    
    def analyze_scenario_1_national_emergency(self) -> List[ScenarioAlert]:
        """Detect 'National Emergency' acceleration patterns"""
        alerts = []
        
        conn = sqlite3.connect(self.db_path)
        
        # Look for emergency contracts with specific patterns
        query = '''
            SELECT recipient_name, award_amount, awarding_agency, award_date,
                   competition_type, description, award_id
            FROM contracts 
            WHERE (
                LOWER(description) LIKE '%emergency%' OR
                LOWER(description) LIKE '%border%' OR
                LOWER(description) LIKE '%cybersecurity%' OR
                LOWER(description) LIKE '%food security%' OR
                LOWER(competition_type) LIKE '%sole%source%' OR
                LOWER(competition_type) LIKE '%no%bid%'
            )
            AND award_date >= date('now', '-180 days')
            ORDER BY award_amount DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        for _, row in df.iterrows():
            evidence = []
            risk_score = 0
            
            # Check for custom watchlist companies (if configured)
            company_upper = row['recipient_name'].upper()
            if self.custom_watchlist and any(watched in company_upper for watched in self.custom_watchlist):
                evidence.append("Company on custom watchlist")
                risk_score += 30
            
            # Check for emergency procurement
            desc_lower = str(row['description']).lower()
            comp_lower = str(row['competition_type']).lower()
            
            if any(keyword in desc_lower for keyword in self.emergency_keywords):
                evidence.append("Contract justified by emergency/crisis language")
                risk_score += 30
            
            if any(pattern in comp_lower for pattern in self.no_bid_patterns):
                evidence.append("No-bid or sole-source procurement")
                risk_score += 35
            
            # Large contract amount
            if row['award_amount'] > 100_000_000:  # >$100M
                evidence.append(f"Large contract amount: ${row['award_amount']:,.0f}")
                risk_score += 20
            
            # Create alert if risk score is high enough
            if risk_score >= 50 and evidence:
                alert = ScenarioAlert(
                    scenario_type="National Emergency Acceleration",
                    severity="HIGH" if risk_score >= 80 else "MEDIUM",
                    company=row['recipient_name'],
                    amount=row['award_amount'],
                    agency=row['awarding_agency'],
                    pattern_detected="Emergency procurement bypassing normal competition",
                    evidence=evidence,
                    risk_score=risk_score
                )
                alerts.append(alert)
        
        return alerts
    
    def analyze_scenario_2_economic_patriotism(self) -> List[ScenarioAlert]:
        """Detect 'Economic Patriotism' trap patterns"""
        alerts = []
        
        conn = sqlite3.connect(self.db_path)
        
        # Look for "Buy American" and infrastructure contracts
        query = '''
            SELECT recipient_name, award_amount, awarding_agency, award_date,
                   competition_type, description, award_id
            FROM contracts 
            WHERE (
                LOWER(description) LIKE '%buy american%' OR
                LOWER(description) LIKE '%infrastructure%' OR
                LOWER(description) LIKE '%energy independence%' OR
                LOWER(description) LIKE '%manufacturing%' OR
                LOWER(description) LIKE '%domestic%'
            )
            AND award_date >= date('now', '-180 days')
            ORDER BY award_amount DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        for _, row in df.iterrows():
            evidence = []
            risk_score = 0
            
            # Check for connected companies getting "patriotic" contracts
            company_upper = row['recipient_name'].upper()
            desc_lower = str(row['description']).lower()
            
            # Patriotic branding
            patriotic_keywords = ['american', 'patriot', 'freedom', 'independence', 'domestic']
            if any(keyword in desc_lower for keyword in patriotic_keywords):
                evidence.append("Contract uses patriotic/nationalist branding")
                risk_score += 25
            
            # Large infrastructure or manufacturing deals
            if row['award_amount'] > 50_000_000 and any(word in desc_lower for word in ['infrastructure', 'manufacturing', 'energy']):
                evidence.append("Large infrastructure/manufacturing contract")
                risk_score += 30
            
            # Check for monopolistic advantages
            if 'exclusive' in desc_lower or 'sole' in desc_lower:
                evidence.append("Contract grants exclusive or monopolistic rights")
                risk_score += 35
            
            if risk_score >= 40 and evidence:
                alert = ScenarioAlert(
                    scenario_type="Economic Patriotism Trap",
                    severity="MEDIUM" if risk_score >= 60 else "LOW",
                    company=row['recipient_name'],
                    amount=row['award_amount'],
                    agency=row['awarding_agency'],
                    pattern_detected="Patriotic branding masking preferential treatment",
                    evidence=evidence,
                    risk_score=risk_score
                )
                alerts.append(alert)
        
        return alerts
    
    def analyze_scenario_3_information_sovereignty(self) -> List[ScenarioAlert]:
        """Detect 'Information Sovereignty' gambit patterns"""
        alerts = []
        
        conn = sqlite3.connect(self.db_path)
        
        # Look for data/information/media contracts
        query = '''
            SELECT recipient_name, award_amount, awarding_agency, award_date,
                   competition_type, description, award_id
            FROM contracts 
            WHERE (
                LOWER(description) LIKE '%data%' OR
                LOWER(description) LIKE '%information%' OR
                LOWER(description) LIKE '%social media%' OR
                LOWER(description) LIKE '%platform%' OR
                LOWER(description) LIKE '%educational%' OR
                LOWER(description) LIKE '%media%' OR
                LOWER(description) LIKE '%communication%'
            )
            AND award_date >= date('now', '-180 days')
            ORDER BY award_amount DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        for _, row in df.iterrows():
            evidence = []
            risk_score = 0
            
            company_upper = row['recipient_name'].upper()
            desc_lower = str(row['description']).lower()
            
            # Check for tech sector companies
            if any(tech_co in company_upper for tech_co in self.tech_sector_companies):
                evidence.append("Contract with major tech sector company")
                risk_score += 35
            
            # Check for custom watchlist platforms (if configured)
            if self.custom_watchlist and any(watched_co in company_upper for watched_co in self.custom_watchlist):
                evidence.append("Contract with watchlist company")
                risk_score += 35
            
            # Data sovereignty language
            sovereignty_keywords = ['american data', 'data sovereignty', 'protect data', 'information security']
            if any(keyword in desc_lower for keyword in sovereignty_keywords):
                evidence.append("Uses data sovereignty/protection justification")
                risk_score += 30
            
            # Educational or media contracts
            if any(word in desc_lower for word in ['education', 'school', 'media', 'journalism']):
                evidence.append("Involves education or media sector")
                risk_score += 25
            
            if risk_score >= 45 and evidence:
                alert = ScenarioAlert(
                    scenario_type="Information Sovereignty Gambit",
                    severity="HIGH" if risk_score >= 70 else "MEDIUM",
                    company=row['recipient_name'],
                    amount=row['award_amount'],
                    agency=row['awarding_agency'],
                    pattern_detected="Data/platform consolidation under sovereignty pretext",
                    evidence=evidence,
                    risk_score=risk_score
                )
                alerts.append(alert)
        
        return alerts
    
    def analyze_scenario_4_financial_consolidation(self) -> List[ScenarioAlert]:
        """Detect 'Financial Security' consolidation patterns"""
        alerts = []
        
        conn = sqlite3.connect(self.db_path)
        
        # Look for financial services contracts
        query = '''
            SELECT recipient_name, award_amount, awarding_agency, award_date,
                   competition_type, description, award_id
            FROM contracts 
            WHERE (
                LOWER(description) LIKE '%financial%' OR
                LOWER(description) LIKE '%banking%' OR
                LOWER(description) LIKE '%payment%' OR
                LOWER(description) LIKE '%crypto%' OR
                LOWER(description) LIKE '%currency%' OR
                LOWER(awarding_agency) LIKE '%treasury%' OR
                LOWER(awarding_agency) LIKE '%federal reserve%'
            )
            AND award_date >= date('now', '-180 days')
            ORDER BY award_amount DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        for _, row in df.iterrows():
            evidence = []
            risk_score = 0
            
            company_upper = row['recipient_name'].upper()
            desc_lower = str(row['description']).lower()
            
            # Check for major financial institutions
            if any(fin_co in company_upper for fin_co in self.financial_sector_companies):
                evidence.append("Contract with major financial institution")
                risk_score += 35
            
            # Populist branding with financial consolidation
            populist_keywords = ['small town', 'community', 'local', 'main street', 'working families']
            if any(keyword in desc_lower for keyword in populist_keywords):
                evidence.append("Uses populist branding")
                risk_score += 25
            
            # Regulatory advantage language
            if any(word in desc_lower for word in ['regulation', 'compliance', 'oversight', 'exclusive']):
                evidence.append("Involves regulatory or compliance advantages")
                risk_score += 30
            
            # Cryptocurrency/digital currency
            if any(word in desc_lower for word in ['crypto', 'digital currency', 'blockchain']):
                evidence.append("Involves cryptocurrency or digital currency")
                risk_score += 25
            
            if risk_score >= 40 and evidence:
                alert = ScenarioAlert(
                    scenario_type="Financial Security Consolidation",
                    severity="MEDIUM" if risk_score >= 60 else "LOW",
                    company=row['recipient_name'],
                    amount=row['award_amount'],
                    agency=row['awarding_agency'],
                    pattern_detected="Financial consolidation under security/populist pretext",
                    evidence=evidence,
                    risk_score=risk_score
                )
                alerts.append(alert)
        
        return alerts
    
    def detect_rapid_connected_accumulation(self) -> List[ScenarioAlert]:
        """Detect rapid accumulation of contracts by connected networks"""
        alerts = []
        
        conn = sqlite3.connect(self.db_path)
        
        # Look for companies getting multiple contracts quickly
        query = '''
            SELECT recipient_name, 
                   COUNT(*) as contract_count,
                   SUM(award_amount) as total_amount,
                   MIN(award_date) as first_contract,
                   MAX(award_date) as last_contract
            FROM contracts 
            WHERE award_date >= date('now', '-90 days')
            GROUP BY recipient_name
            HAVING COUNT(*) >= 2
            ORDER BY total_amount DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        for _, row in df.iterrows():
            evidence = []
            risk_score = 0
            
            company_upper = row['recipient_name'].upper()
            
            # Check if company is in any monitored sector
            monitored_sectors = []
            if self.custom_watchlist and any(watched_co in company_upper for watched_co in self.custom_watchlist):
                monitored_sectors.append("Custom watchlist")
                risk_score += 40
            
            if any(tech_co in company_upper for tech_co in self.tech_sector_companies):
                monitored_sectors.append("Tech sector")
                risk_score += 30
            
            if any(def_co in company_upper for def_co in self.defense_sector_companies):
                monitored_sectors.append("Defense sector")
                risk_score += 25
            
            if any(fin_co in company_upper for fin_co in self.financial_sector_companies):
                monitored_sectors.append("Financial sector")
                risk_score += 30
            
            if connected_networks:
                evidence.append(f"Company in connected network: {', '.join(connected_networks)}")
                evidence.append(f"Received {row['contract_count']} contracts in 90 days")
                evidence.append(f"Total value: ${row['total_amount']:,.0f}")
                
                # High accumulation rate
                if row['contract_count'] >= 3:
                    risk_score += 25
                
                # Large total amount
                if row['total_amount'] > 10_000_000:
                    risk_score += 20
                
                if risk_score >= 60:
                    alert = ScenarioAlert(
                        scenario_type="Connected Network Accumulation",
                        severity="HIGH" if risk_score >= 80 else "MEDIUM",
                        company=row['recipient_name'],
                        amount=row['total_amount'],
                        agency="Multiple Agencies",
                        pattern_detected="Rapid contract accumulation by connected company",
                        evidence=evidence,
                        risk_score=risk_score
                    )
                    alerts.append(alert)
        
        return alerts
    
    def run_full_scenario_analysis(self) -> Dict[str, List[ScenarioAlert]]:
        """Run all scenario analyses"""
        logger.info("Running comprehensive scenario analysis...")
        
        results = {
            'national_emergency': self.analyze_scenario_1_national_emergency(),
            'economic_patriotism': self.analyze_scenario_2_economic_patriotism(),
            'information_sovereignty': self.analyze_scenario_3_information_sovereignty(),
            'financial_consolidation': self.analyze_scenario_4_financial_consolidation(),
            'connected_accumulation': self.detect_rapid_connected_accumulation()
        }
        
        total_alerts = sum(len(alerts) for alerts in results.values())
        logger.info(f"Scenario analysis complete: {total_alerts} alerts generated")
        
        return results
    
    def generate_scenario_report(self) -> str:
        """Generate comprehensive scenario monitoring report"""
        results = self.run_full_scenario_analysis()
        
        report = []
        report.append("🚨 GOVERNMENT CONTRACT SCENARIO MONITORING REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        for scenario_name, alerts in results.items():
            if alerts:
                report.append(f"📋 {scenario_name.replace('_', ' ').title()}: {len(alerts)} alerts")
                
                for alert in sorted(alerts, key=lambda x: x.risk_score, reverse=True)[:3]:
                    report.append(f"   🚨 {alert.severity}: {alert.company}")
                    report.append(f"      Amount: ${alert.amount:,.0f}")
                    report.append(f"      Pattern: {alert.pattern_detected}")
                    report.append(f"      Risk Score: {alert.risk_score}/100")
                    for evidence in alert.evidence[:2]:  # Top 2 evidence points
                        report.append(f"      • {evidence}")
                    report.append("")
            else:
                report.append(f"✅ {scenario_name.replace('_', ' ').title()}: No alerts")
        
        return "\n".join(report)

def main():
    """Test scenario monitoring"""
    monitor = ScenarioMonitor()
    
    print("🔍 Running Scenario-Based Contract Monitoring...")
    print("Watching for patterns of:")
    print("  • National Emergency acceleration")
    print("  • Economic Patriotism traps") 
    print("  • Information Sovereignty gambits")
    print("  • Financial Security consolidation")
    print("  • Connected network accumulation")
    print()
    
    report = monitor.generate_scenario_report()
    print(report)

if __name__ == "__main__":
    main()
