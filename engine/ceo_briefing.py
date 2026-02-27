"""
CEO Weekly Briefing Generator - Gold Tier
Generates Monday Morning CEO Audit from Odoo data
"""

import sys
import os
from pathlib import Path

# Fix emoji encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')  # Set UTF-8 code page
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_servers.odoo_server import OdooMCPServer
from datetime import datetime, timedelta

VAULT = Path(__file__).parent.parent


def generate_ceo_briefing():
    """Generate weekly CEO briefing from Odoo data"""
    try:
        odoo = OdooMCPServer()
        
        # Get financial data
        revenue = odoo.get_revenue_this_week()
        unpaid = odoo.get_unpaid_invoices()
        leads = odoo.get_leads(limit=10)
        quotations = odoo.get_quotations(limit=10)
        
        # Handle errors gracefully
        if isinstance(revenue, dict) and "error" in revenue:
            revenue = {"total_revenue": 0, "invoices_count": 0, "error": revenue["error"]}
        
        briefing = f"""# Monday Morning CEO Briefing

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Period:** {datetime.now().strftime('%B %Y')}

---

## Executive Summary

Welcome to your weekly business audit. Here's what happened in your business:

---

## Revenue Summary

"""
        
        if "error" not in revenue:
            briefing += f"""| Metric | Value |
|--------|-------|
| **Total Revenue This Week** | ${revenue.get('total_revenue', 0):.2f} |
| **Invoices Paid** | {revenue.get('invoices_count', 0)} |
"""
        else:
            briefing += f"""Revenue data unavailable: {revenue.get('error')}

"""
        
        briefing += f"""
---

## Unpaid Invoices (Follow Up Required)

"""
        
        if unpaid and isinstance(unpaid, list) and len(unpaid) > 0:
            briefing += """| Invoice | Customer | Amount | Date | Status |
|---------|----------|--------|------|--------|
"""
            for inv in unpaid[:10]:  # Show top 10
                partner = inv.get('partner_id', ['Unknown'])[1] if isinstance(inv.get('partner_id'), list) else 'Unknown'
                briefing += f"| {inv.get('name', 'N/A')} | {partner} | ${inv.get('amount_total', 0):.2f} | {inv.get('invoice_date', 'N/A')} | {inv.get('state', 'N/A')} |\n"
            
            briefing += f"\n**Total Unpaid:** {len(unpaid)} invoices\n"
        elif unpaid and isinstance(unpaid, dict) and "error" in unpaid:
            briefing += f"\nUnable to fetch unpaid invoices: {unpaid.get('error')}\n"
        else:
            briefing += "\nNo unpaid invoices! All payments received.\n"
        
        briefing += f"""
---

## Recent CRM Leads

"""
        
        if leads and isinstance(leads, list) and len(leads) > 0:
            briefing += """| Lead | Email | Phone | Source | Date |
|------|-------|-------|--------|------|
"""
            for lead in leads[:10]:  # Show top 10
                briefing += f"| {lead.get('name', 'N/A')} | {lead.get('email_from', 'N/A')} | {lead.get('phone', 'N/A')} | {lead.get('source', 'N/A')} | {lead.get('create_date', 'N/A')} |\n"
        elif leads and isinstance(leads, dict) and "error" in leads:
            briefing += f"\nUnable to fetch leads: {leads.get('error')}\n"
        else:
            briefing += "\nNo new leads this period.\n"
        
        briefing += f"""
---

## Sales Quotations

"""
        
        if quotations and isinstance(quotations, list) and len(quotations) > 0:
            briefing += """| Quotation | Customer | Amount | Status | Date |
|-----------|----------|--------|--------|------|
"""
            for quote in quotations[:10]:
                partner = quote.get('partner_id', ['Unknown'])[1] if isinstance(quote.get('partner_id'), list) else 'Unknown'
                briefing += f"| {quote.get('name', 'N/A')} | {partner} | ${quote.get('amount_total', 0):.2f} | {quote.get('state', 'N/A')} | {quote.get('date_order', 'N/A')} |\n"
        elif quotations and isinstance(quotations, dict) and "error" in quotations:
            briefing += f"\nUnable to fetch quotations: {quotations.get('error')}\n"
        else:
            briefing += "\nNo quotations this period.\n"
        
        briefing += f"""
---

## Action Items

### High Priority
- [ ] Follow up on unpaid invoices above
- [ ] Contact new leads from this week
- [ ] Review pending quotations

### This Week's Focus
- [ ] Convert qualified leads to opportunities
- [ ] Send quotations to pending customers
- [ ] Review revenue targets vs actual

---

## Quick Stats

| Category | Count |
|----------|-------|
| Unpaid Invoices | {len(unpaid) if isinstance(unpaid, list) else 0} |
| Recent Leads | {len(leads) if isinstance(leads, list) else 0} |
| Active Quotations | {len(quotations) if isinstance(quotations, list) else 0} |

---

## Quick Links

- [Open Odoo CRM](http://localhost:8069/web#menu_id=69&action=107&model=crm.lead&view_type=list)
- [Open Odoo Invoices](http://localhost:8069/web#menu_id=194&action=103&model=account.move&view_type=list)
- [Open Odoo Quotations](http://localhost:8069/web#menu_id=196&action=109&model=sale.order&view_type=list)

---

*Briefing generated by AI Employee Vault - Gold Tier*
*Next briefing: {datetime.now() + timedelta(days=7):%Y-%m-%d}%
"""
        
        # Save to Odoo_Data/CEO_Briefings/
        briefing_folder = VAULT / "Odoo_Data" / "CEO_Briefings"
        briefing_folder.mkdir(exist_ok=True)
        
        filename = f"CEO_Briefing_{datetime.now().strftime('%Y-%m-%d')}.md"
        briefing_file = briefing_folder / filename
        briefing_file.write_text(briefing, encoding='utf-8')
        
        print(f"CEO Briefing generated: {filename}")
        print(f"Saved to: {briefing_file}")
        
        return briefing_file
        
    except Exception as e:
        print(f"Error generating CEO briefing: {e}")
        from engine.audit_logger import log_action
        log_action("GENERATE_CEO_BRIEFING", {"status": "failed", "error": str(e)})
        return None


# Test the briefing generator
if __name__ == "__main__":
    print("Generating CEO Briefing...")
    try:
        briefing_file = generate_ceo_briefing()
        if briefing_file:
            print(f"\nBriefing generated successfully!")
            print(f"Open: {briefing_file}")
    except Exception as e:
        print(f"\nFailed: {e}")
        print("\nMake sure Odoo is running and accessible at http://localhost:8069")
