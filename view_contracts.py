#!/usr/bin/env python3
"""
Simple Contract Viewer
Shows detailed contract information from your database
"""

import sqlite3
import sys

def view_recent_contracts(limit=20):
    """Show most recent contracts"""
    conn = sqlite3.connect('government_monitor.db')
    cursor = conn.cursor()
    
    query = """
        SELECT 
            recipient_name,
            printf('$%,.2f', award_amount) as amount,
            awarding_agency,
            award_date,
            competition_type,
            substr(description, 1, 80) as description
        FROM contracts 
        ORDER BY award_date DESC 
        LIMIT ?
    """
    
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    
    print("\n" + "="*120)
    print("📋 MOST RECENT CONTRACTS")
    print("="*120 + "\n")
    
    for i, row in enumerate(results, 1):
        print(f"Contract #{i}")
        print(f"  Company:     {row[0]}")
        print(f"  Amount:      {row[1]}")
        print(f"  Agency:      {row[2]}")
        print(f"  Date:        {row[3]}")
        print(f"  Competition: {row[4]}")
        print(f"  Description: {row[5]}")
        print()
    
    conn.close()

def view_by_company(company_name):
    """Show all contracts for a specific company"""
    conn = sqlite3.connect('government_monitor.db')
    cursor = conn.cursor()
    
    query = """
        SELECT 
            recipient_name,
            printf('$%,.2f', award_amount) as amount,
            awarding_agency,
            award_date,
            competition_type,
            description
        FROM contracts 
        WHERE recipient_name LIKE ?
        ORDER BY award_date DESC
    """
    
    cursor.execute(query, (f'%{company_name}%',))
    results = cursor.fetchall()
    
    if not results:
        print(f"\n❌ No contracts found for company matching: {company_name}")
        conn.close()
        return
    
    print("\n" + "="*120)
    print(f"📋 CONTRACTS FOR: {results[0][0]}")
    print("="*120 + "\n")
    
    total = 0
    for i, row in enumerate(results, 1):
        amount_str = row[1]
        amount_num = float(amount_str.replace('$', '').replace(',', ''))
        total += amount_num
        
        print(f"Contract #{i}")
        print(f"  Amount:      {row[1]}")
        print(f"  Agency:      {row[2]}")
        print(f"  Date:        {row[3]}")
        print(f"  Competition: {row[4]}")
        print(f"  Description: {row[5][:100]}")
        print()
    
    print(f"Total Contracts: {len(results)}")
    print(f"Total Value: ${total:,.2f}\n")
    
    conn.close()

def view_large_contracts(min_amount=1000000):
    """Show contracts above a certain dollar amount"""
    conn = sqlite3.connect('government_monitor.db')
    cursor = conn.cursor()
    
    query = """
        SELECT 
            recipient_name,
            printf('$%,.2f', award_amount) as amount,
            awarding_agency,
            award_date,
            competition_type
        FROM contracts 
        WHERE award_amount >= ?
        ORDER BY award_amount DESC
    """
    
    cursor.execute(query, (min_amount,))
    results = cursor.fetchall()
    
    print("\n" + "="*120)
    print(f"📋 LARGE CONTRACTS (${min_amount:,}+)")
    print("="*120 + "\n")
    
    for i, row in enumerate(results, 1):
        print(f"{i}. {row[0]:<50} {row[1]:>15} {row[2]:<30} {row[3]}")
    
    print(f"\nTotal: {len(results)} contracts\n")
    conn.close()

def main():
    """Main menu"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "recent":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            view_recent_contracts(limit)
        
        elif command == "company":
            if len(sys.argv) < 3:
                print("Usage: python3 view_contracts.py company <company_name>")
                return
            company = ' '.join(sys.argv[2:])
            view_by_company(company)
        
        elif command == "large":
            min_amount = int(sys.argv[2]) if len(sys.argv) > 2 else 1000000
            view_large_contracts(min_amount)
        
        else:
            print(f"Unknown command: {command}")
            print("\nAvailable commands:")
            print("  recent [limit]           - Show most recent contracts")
            print("  company <name>           - Show all contracts for a company")
            print("  large [min_amount]       - Show contracts above dollar amount")
    
    else:
        # Default: show recent contracts
        view_recent_contracts(20)

if __name__ == "__main__":
    main()

