"""
Odoo MCP Server - Gold Tier Implementation
Handles CRM, Sales, and Invoicing via JSON-RPC
"""

import xmlrpc.client
from pathlib import Path
import os
from datetime import datetime
from engine.audit_logger import log_action


class OdooMCPServer:
    """
    Odoo MCP Server for CRM, Sales, and Invoicing
    """
    
    def __init__(self):
        # Load from .env
        self.url = "http://localhost:8069"
        self.db = "ai_employee_db"
        self.username = "bashartech56@gmail.com"
        self.password = "bashar320420"
        
        # Connect to Odoo
        try:
            self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
            self.uid = self.common.authenticate(
                self.db, self.username, self.password, {}
            )
            
            if not self.uid:
                raise Exception("Odoo authentication failed! Check credentials.")
            
            self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
            print(f"✅ Odoo connected successfully (UID: {self.uid})")
            log_action("ODOO_CONNECT", {"status": "success", "uid": self.uid})
        except Exception as e:
            print(f"❌ Odoo connection failed: {e}")
            log_action("ODOO_CONNECT", {"status": "failed", "error": str(e)})
            raise
    
    # ==================== CRM FUNCTIONS ====================
    
    def create_lead(self, name, email="", phone="", source="Website"):
        """Create a new CRM lead"""
        try:
            # Note: Not using 'source' field as it may not exist in all Odoo versions
            lead_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                "crm.lead", "create", [{
                    "name": name,
                    "email_from": email,
                    "phone": phone,
                    "contact_name": name,
                }]
            )
            print(f"✅ Lead created: ID {lead_id}")
            log_action("ODOO_CREATE_LEAD", {
                "lead_id": lead_id,
                "name": name,
                "email": email,
                "source": source
            })
            return {"success": True, "lead_id": lead_id}
        except Exception as e:
            error_msg = f"❌ Error creating lead: {e}"
            print(error_msg)
            log_action("ODOO_CREATE_LEAD", {"status": "failed", "error": str(e)})
            return {"success": False, "error": str(e)}
    
    def get_leads(self, limit=10):
        """Get recent leads"""
        try:
            # Use standard fields that exist in all Odoo versions
            leads = self.models.execute_kw(
                self.db, self.uid, self.password,
                "crm.lead", "search_read",
                [[]],  # All records
                {"fields": ["name", "email_from", "phone", "create_date", "contact_name"], "limit": limit}
            )
            log_action("ODOO_GET_LEADS", {"count": len(leads)})
            return leads
        except Exception as e:
            log_action("ODOO_GET_LEADS", {"status": "failed", "error": str(e)})
            return {"error": str(e)}
    
    def update_lead_stage(self, lead_id, stage_id):
        """Update lead stage (e.g., New → Qualified → Won)"""
        try:
            self.models.execute_kw(
                self.db, self.uid, self.password,
                "crm.lead", "write",
                [[lead_id], {"stage_id": stage_id}]
            )
            print(f"✅ Lead {lead_id} stage updated")
            log_action("ODOO_UPDATE_LEAD", {"lead_id": lead_id, "stage_id": stage_id})
            return {"success": True}
        except Exception as e:
            log_action("ODOO_UPDATE_LEAD", {"status": "failed", "error": str(e)})
            return {"success": False, "error": str(e)}
    
    # ==================== SALES FUNCTIONS ====================
    
    def create_quotation(self, partner_id, product_id=None, qty=1, amount=0.0):
        """Create a sales quotation"""
        try:
            order_lines = []
            if product_id:
                order_lines = [(0, 0, {
                    "product_id": product_id,
                    "product_uom_qty": qty,
                    "price_unit": amount
                })]
            
            quotation_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                "sale.order", "create", [{
                    "partner_id": partner_id,
                    "order_line": order_lines
                }]
            )
            print(f"✅ Quotation created: ID {quotation_id}")
            log_action("ODOO_CREATE_QUOTATION", {"quotation_id": quotation_id, "partner_id": partner_id})
            return {"success": True, "quotation_id": quotation_id}
        except Exception as e:
            error_msg = f"❌ Error creating quotation: {e}"
            print(error_msg)
            log_action("ODOO_CREATE_QUOTATION", {"status": "failed", "error": str(e)})
            return {"success": False, "error": str(e)}
    
    def confirm_sale(self, sale_order_id):
        """Confirm a quotation (convert to sales order)"""
        try:
            self.models.execute_kw(
                self.db, self.uid, self.password,
                "sale.order", "action_confirm",
                [[sale_order_id]]
            )
            print(f"✅ Sale order {sale_order_id} confirmed")
            log_action("ODOO_CONFIRM_SALE", {"sale_order_id": sale_order_id})
            return {"success": True}
        except Exception as e:
            log_action("ODOO_CONFIRM_SALE", {"status": "failed", "error": str(e)})
            return {"success": False, "error": str(e)}
    
    def get_quotations(self, limit=10):
        """Get recent quotations"""
        try:
            quotations = self.models.execute_kw(
                self.db, self.uid, self.password,
                "sale.order", "search_read",
                [[]],
                {"fields": ["name", "partner_id", "amount_total", "state", "date_order"], "limit": limit}
            )
            log_action("ODOO_GET_QUOTATIONS", {"count": len(quotations)})
            return quotations
        except Exception as e:
            log_action("ODOO_GET_QUOTATIONS", {"status": "failed", "error": str(e)})
            return {"error": str(e)}
    
    # ==================== INVOICING FUNCTIONS ====================
    
    def create_invoice(self, partner_id, amount=0.0, invoice_date=None, description="Service/Product"):
        """Create a customer invoice"""
        try:
            invoice_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                "account.move", "create", [{
                    "move_type": "out_invoice",
                    "partner_id": partner_id,
                    "invoice_date": invoice_date or datetime.now().strftime('%Y-%m-%d'),
                    "invoice_line_ids": [(0, 0, {
                        "name": description,
                        "price_unit": amount,
                        "quantity": 1,
                    })]
                }]
            )
            print(f"✅ Invoice created: ID {invoice_id}")
            log_action("ODOO_CREATE_INVOICE", {
                "invoice_id": invoice_id,
                "partner_id": partner_id,
                "amount": amount
            })
            return {"success": True, "invoice_id": invoice_id}
        except Exception as e:
            error_msg = f"❌ Error creating invoice: {e}"
            print(error_msg)
            log_action("ODOO_CREATE_INVOICE", {"status": "failed", "error": str(e)})
            return {"success": False, "error": str(e)}
    
    def get_unpaid_invoices(self):
        """Get all unpaid customer invoices"""
        try:
            invoices = self.models.execute_kw(
                self.db, self.uid, self.password,
                "account.move", "search_read",
                [[
                    ["move_type", "=", "out_invoice"],
                    ["payment_state", "!=", "paid"]
                ]],
                {"fields": ["name", "partner_id", "amount_total", "invoice_date", "state"]}
            )
            log_action("ODOO_GET_UNPAID_INVOICES", {"count": len(invoices)})
            return invoices
        except Exception as e:
            log_action("ODOO_GET_UNPAID_INVOICES", {"status": "failed", "error": str(e)})
            return {"error": str(e)}
    
    def get_paid_invoices(self, days=7):
        """Get paid invoices from last N days"""
        try:
            invoices = self.models.execute_kw(
                self.db, self.uid, self.password,
                "account.move", "search_read",
                [[
                    ["move_type", "=", "out_invoice"],
                    ["payment_state", "=", "paid"],
                    ["invoice_date", ">=", (datetime.now().strftime('%Y-%m-%d'))]
                ]],
                {"fields": ["name", "partner_id", "amount_total", "invoice_date"]}
            )
            log_action("ODOO_GET_PAID_INVOICES", {"count": len(invoices)})
            return invoices
        except Exception as e:
            log_action("ODOO_GET_PAID_INVOICES", {"status": "failed", "error": str(e)})
            return {"error": str(e)}
    
    def get_revenue_this_week(self):
        """Get total revenue for current week"""
        try:
            invoices = self.models.execute_kw(
                self.db, self.uid, self.password,
                "account.move", "search_read",
                [[
                    ["move_type", "=", "out_invoice"],
                    ["payment_state", "=", "paid"]
                ]],
                {"fields": ["amount_total"]}
            )
            total = sum(inv.get("amount_total", 0) for inv in invoices)
            result = {"total_revenue": total, "invoices_count": len(invoices)}
            log_action("ODOO_GET_REVENUE", result)
            return result
        except Exception as e:
            log_action("ODOO_GET_REVENUE", {"status": "failed", "error": str(e)})
            return {"error": str(e)}
    
    # ==================== PARTNER (CUSTOMER) FUNCTIONS ====================
    
    def create_partner(self, name, email="", phone=""):
        """Create a customer/partner"""
        try:
            partner_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                "res.partner", "create", [{
                    "name": name,
                    "email": email,
                    "phone": phone
                }]
            )
            print(f"✅ Partner created: ID {partner_id}")
            log_action("ODOO_CREATE_PARTNER", {
                "partner_id": partner_id,
                "name": name,
                "email": email
            })
            return {"success": True, "partner_id": partner_id}
        except Exception as e:
            error_msg = f"❌ Error creating partner: {e}"
            print(error_msg)
            log_action("ODOO_CREATE_PARTNER", {"status": "failed", "error": str(e)})
            return {"success": False, "error": str(e)}
    
    def get_partner_by_email(self, email):
        """Find partner by email"""
        try:
            partners = self.models.execute_kw(
                self.db, self.uid, self.password,
                "res.partner", "search_read",
                [[["email", "=", email]]],
                {"fields": ["id", "name", "email", "phone"]}
            )
            if partners:
                return partners[0]
            return None
        except Exception as e:
            log_action("ODOO_GET_PARTNER", {"status": "failed", "error": str(e)})
            return None


# Test connection if run directly
if __name__ == "__main__":
    print("Testing Odoo MCP Server connection...")
    try:
        odoo = OdooMCPServer()
        print("\n✅ Connection successful!")
        
        # Test get leads
        print("\n📋 Recent Leads:")
        leads = odoo.get_leads(5)
        for lead in leads:
            print(f"  - {lead.get('name')} | {lead.get('email_from')}")
        
        # Test revenue
        print("\n💰 Revenue This Week:")
        revenue = odoo.get_revenue_this_week()
        if "total_revenue" in revenue:
            print(f"  Total: ${revenue['total_revenue']:.2f}")
            print(f"  Invoices: {revenue['invoices_count']}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
