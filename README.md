# 🔍 Government Contract Cronyism Monitor

A comprehensive monitoring system designed to detect corruption patterns, cronyism, and preferential treatment in federal government contracting.

## ⚠️ IMPORTANT: Before You Start

### 🔐 Security Requirements
1. **Never commit `token.txt`** - Your API token must stay private
2. **Get a SAM.gov API key** - Required (free): https://sam.gov/
3. **Review [SECURITY.md](SECURITY.md)** - Important security guidelines

### 📋 First-Time Setup
```bash
# 1. Clone this repository
git clone https://github.com/brcinque/government-contract-monitor.git
cd government-contract-monitor

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Set up your API token
cp token.txt.example token.txt
# Edit token.txt and add your SAM.gov API token

# 4. Verify setup
python3 monitor.py  # Choose option 4 for Quick Status
```

### ⚖️ Responsible Use
This tool provides **independent verification** capabilities. It detects patterns that may warrant investigation:
- ✅ Verify findings through multiple sources
- ✅ Understand that pattern detection requires context
- ✅ Use as one tool among many for oversight
- ✅ Document and archive suspicious patterns
- ⚠️ Patterns indicate areas for scrutiny, not proof of wrongdoing

---

## 🚀 Quick Start

### Main Interface (Recommended)
```bash
python3 monitor.py
```
**Interactive menu with options:**
1. **Full Cronyism Detection** - Complete analysis with pattern detection
2. **Data Collection Only** - Update database without analysis  
3. **Dashboard Only** - Launch web interface
4. **Quick Status** - Show system status

### Enhanced Dashboard
```bash
python3 enhanced_dashboard.py
```
Advanced cronyism-focused dashboard at: http://127.0.0.1:8080

### Original Dashboard
```bash
python3 scripts/run_dashboard.py
```
Classic interface at: http://127.0.0.1:8080

## 📊 What It Detects

### 🚨 Cronyism Patterns
- **Emergency Procurement** - Contracts bypassing competition under "crisis" pretexts
- **Rapid Accumulation** - Companies quickly receiving multiple contracts
- **Watchlist Companies** - Trump network, Big Tech, connected entities
- **No-Bid Contracts** - Sole-source awards without competition
- **Large Contract Alerts** - High-value deals requiring scrutiny

### 🎯 Specific Scenarios Monitored
1. **"National Emergency" Acceleration** - Crisis-justified contract acceleration
2. **"Economic Patriotism" Traps** - Patriotic branding masking preferential treatment
3. **"Information Sovereignty" Gambits** - Data/platform consolidation under security pretexts
4. **"Financial Security" Consolidation** - Banking/finance deals with regulatory advantages

## 🗂️ File Structure

```
GSA/
├── monitor.py                 # 🎯 MAIN INTERFACE (use this)
├── enhanced_dashboard.py      # 🔍 ADVANCED CRONYISM DASHBOARD  
├── dashboard_webapp.py        # 📊 Original dashboard
├── government_monitor.db      # 💾 Database (auto-created)
├── README.md                  # 📖 This documentation
├── core/                      # Core system files
│   ├── government_monitor_system.py
│   ├── comprehensive_collector.py
│   └── scenario_monitoring.py
├── scripts/                   # Execution scripts
│   ├── run_cronyism_detection.py
│   ├── run_ultimate_collection.py
│   ├── run_enhanced_collection.py
│   ├── run_daily_collection.py
│   └── run_dashboard.py
└── archive/                   # Development files
```

## 💾 System Status
- **Multi-source data collection** from 7+ government sources
- **Real-time pattern detection** for corruption scenarios
- **Historical analysis** with 20+ years of data capability
- **Interactive dashboards** with advanced visualizations

## 🎯 Key Features

### Data Collection
- **USASpending.gov** - Enhanced queries with multiple strategies
- **Federal Register** - Legal contract notices
- **Agency Press Releases** - Real-time announcements (NASA, GSA, VA, DoD, DHS, DoE)
- **Small Business Contracts** - SBA awards and programs
- **Automatic deduplication** across sources
- **Rate limiting** and respectful scraping

### Pattern Detection
- **Watchlist Monitoring** - Tracks specific companies and networks
- **Emergency Pattern Detection** - Flags crisis-justified procurement
- **Competition Analysis** - Identifies no-bid/sole-source patterns
- **Timeline Analysis** - Detects unusual contract timing
- **Risk Scoring** - Quantifies corruption likelihood

### Dashboard Features
- **Cronyism Summary Cards** - Key corruption metrics
- **Watchlist Company Table** - Tracked entities and their contracts
- **Emergency Contract List** - No-bid and crisis-justified deals
- **Agency Risk Analysis** - Risk scoring by government agency
- **Timeline Charts** - Pattern development over time
- **Interactive Visualizations** - Plotly-powered charts

## 🔧 Technical Requirements

### Installation
```bash
# Recommended: Use virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip3 install -r requirements.txt
```

### System Requirements
- **Python**: 3.10+ (tested with 3.10 and 3.12)
- **Memory**: 8GB+ RAM recommended
- **Storage**: ~1GB for years of data
- **Network**: Internet access for government APIs
- **API Key**: Free SAM.gov account required

### API Token Setup (Required)
1. Create account at https://sam.gov/ (free)
2. Navigate to Account Settings → API Access
3. Generate API key
4. Create `token.txt` file:
```bash
cp token.txt.example token.txt
# Edit token.txt and paste your API key
```
5. **NEVER commit token.txt to git** (automatically ignored)

## 🔄 Daily Operation

### Recommended Daily Workflow
```bash
python3 monitor.py
# Choose option 1: Full Cronyism Detection
```

### Automated Monitoring
Set up daily cron job:
```bash
0 9 * * * cd /path/to/GSA && python3 monitor.py >> collection.log 2>&1
```

### Manual Collection
```bash
python3 -c "
import sys; sys.path.insert(0, 'core')
from comprehensive_collector import UltimateGovernmentMonitor
monitor = UltimateGovernmentMonitor()
results = monitor.run_ultimate_collection()
print(f'Collected {results.get(\"new_contracts_saved\", 0)} contracts')
"
```

## 🚨 Alert System

### Alert Types
- **HIGH**: Immediate investigation recommended
- **MEDIUM**: Monitor for pattern development  
- **LOW**: Background tracking

### Pattern Detection
- **Rapid Accumulation**: 3+ contracts in 30 days
- **Large No-Bid**: Non-competitive contracts over $10M
- **Emergency Procurement**: Crisis-justified bypassing of competition
- **Connected Networks**: Contracts to watchlist companies

## 📊 Database Schema

### Contracts Table
- award_id, recipient_name, award_amount
- awarding_agency, award_date, competition_type
- description, collected_date

### Alerts Table
- alert_type, message, data, created_date
- resolved, severity, risk_score

## 🔧 Configuration

### Email Alerts (Optional)
Edit `core/government_monitor_system.py`:
```python
email_config = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'your-email@gmail.com',
    'password': 'your-app-password',
    'from_email': 'your-email@gmail.com',
    'to_email': 'your-email@gmail.com'
}
monitor = GovernmentMonitor(email_config)
```

## 📝 Usage Examples

### Company Research
```python
import sys; sys.path.insert(0, 'core')
from government_monitor_system import GovernmentMonitor
monitor = GovernmentMonitor()
report = monitor.get_company_report("Palantir")
print(f"Total contracts: {report['summary']['total_contracts']}")
```

### Custom Analysis
```python
import sqlite3
conn = sqlite3.connect('government_monitor.db')
cursor = conn.cursor()
cursor.execute("""
    SELECT recipient_name, SUM(award_amount) 
    FROM contracts 
    WHERE awarding_agency LIKE '%Defense%'
    GROUP BY recipient_name 
    ORDER BY SUM(award_amount) DESC 
    LIMIT 10
""")
results = cursor.fetchall()
```

## 🛠️ Troubleshooting

### Dashboard Won't Start
```bash
# Check if port 8080 is in use
lsof -i :8080

# Kill existing process if needed
kill -9 <PID>
```

### No Data Collected
```bash
# Test API connection
python3 -c "
import requests
response = requests.get('https://api.usaspending.gov/api/v2/')
print(f'API Status: {response.status_code}')
"
```

### Database Issues
```bash
# Check database
sqlite3 government_monitor.db ".tables"
sqlite3 government_monitor.db "SELECT COUNT(*) FROM contracts;"
```

## 🎯 Success Metrics

### Detection Capability
- **Multi-source monitoring** - 7+ government data sources
- **Real-time pattern detection** - Immediate alerts on concerning developments
- **Historical analysis** - 20+ years of data capability
- **Scenario-specific detection** - Tailored for outlined corruption patterns

### System Performance
- **Clean file structure** - Organized and maintainable
- **Single main interface** - Streamlined user experience
- **Advanced dashboards** - Professional visualizations
- **Production ready** - Reliable and tested

## 🔒 Privacy & Security

- **Local Storage**: All data stored locally in SQLite
- **No External Dependencies**: Runs entirely on your machine
- **API Rate Limits**: Respects government API limits
- **Personal Use**: Designed for individual research/monitoring

## 🎯 Bottom Line

This system transforms your ability to detect corruption by:
1. **Monitoring 7+ government data sources** simultaneously
2. **Pattern detection** specifically designed for your scenarios
3. **Real-time alerting** on concerning developments
4. **Historical analysis** to understand trend development
5. **Evidence collection** for investigative follow-up

**Perfect for detecting emergency acceleration, patriotic branding, information sovereignty, and financial consolidation schemes.**

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🔒 Security

- See [SECURITY.md](SECURITY.md) for security guidelines
- Never commit sensitive data (tokens, credentials)
- Keep your monitoring data local and secure

## 📚 Documentation

- 📖 [USAGE_GUIDE.md](USAGE_GUIDE.md) - Detailed usage instructions
- 🏗️ [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) - Technical architecture
- 📋 [CHANGELOG.md](CHANGELOG.md) - Version history and updates
- 🔐 [SECURITY.md](SECURITY.md) - Security best practices

## 🐛 Issues & Improvements

Found a bug or have a suggestion? Open an issue on GitHub. This tool is designed for independent watchdog use - improvements that enhance monitoring capabilities are welcome.

## ⚖️ Disclaimer

**This tool enables independent monitoring and verification.**

- ✅ Provides pattern detection for individual oversight
- ✅ All data collected is already public government information
- ✅ Designed for personal watchdog and verification purposes
- ⚠️ Pattern detection identifies areas for scrutiny, not proof
- ⚠️ Users responsible for their own analysis and conclusions
- ⚠️ Verify all findings through multiple independent sources

**Data accuracy depends on government reporting. This tool is one mechanism for checks at the individual level.**

## 🌟 Data Sources

This monitoring tool collects from:
- USASpending.gov
- SAM.gov (System for Award Management)
- Federal Register
- Department of Defense
- NASA, GSA, VA, DHS, DOE, and other federal agencies

Built with Python, Flask, Plotly, and open source libraries.

**Independent monitoring is a form of distributed accountability.** 🔦