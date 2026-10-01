"""
Akhi Real Estate Intelligence — Email Notification System
Sends lead alerts to the admin and confirmation emails to buyers.
Uses stdlib smtplib only (no external service required).
"""
from __future__ import annotations

import smtplib
import ssl
import textwrap
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

try:
    from config.settings import (
        SMTP_HOST,
        SMTP_PORT,
        SMTP_USER,
        SMTP_PASSWORD,
        SMTP_FROM_NAME,
        NOTIFY_EMAIL,
        PLATFORM_NAME,
        smtp_is_configured,
    )
except ImportError:
    import os
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Akhi Real Estate Intelligence")
    NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", SMTP_USER)
    PLATFORM_NAME = "Akhi Real Estate Intelligence"

    def smtp_is_configured() -> bool:
        return bool(SMTP_USER and SMTP_PASSWORD and "placeholder" not in (SMTP_PASSWORD or "").lower())


def _send_email(to_email: str, subject: str, html_body: str, text_body: str = "") -> tuple[bool, str]:
    """
    Core SMTP sender. Returns (success, message).
    Uses STARTTLS on port 587 (Gmail / Zoho / Outlook compatible).
    """
    if not smtp_is_configured():
        return False, "SMTP not configured — set SMTP_USER and SMTP_PASSWORD in .env"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_USER}>"
        msg["To"] = to_email

        if text_body:
            msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())

        return True, f"Email sent to {to_email}"
    except smtplib.SMTPAuthenticationError:
        return False, "SMTP authentication failed — check SMTP_USER / SMTP_PASSWORD in .env"
    except smtplib.SMTPException as exc:
        return False, f"SMTP error: {exc}"
    except Exception as exc:
        return False, f"Email failed: {exc}"


# ── Admin Lead Alert ──────────────────────────────────────────────────────────

def send_new_lead_alert(lead: dict[str, Any]) -> tuple[bool, str]:
    """
    Sends a formatted lead alert to the admin inbox.
    Called immediately after a new inquiry/lead is saved.
    """
    budget_cr = float(lead.get("budget", 0) or 0)
    budget_label = f"₹{budget_cr:.2f} Cr" if budget_cr >= 1 else f"₹{budget_cr * 100:.0f} L"

    subject = f"🔥 New Lead: {lead.get('name', 'Unknown')} — {budget_label} | {PLATFORM_NAME}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px;
                      box-shadow: 0 4px 20px rgba(0,0,0,0.08); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #0f172a 0%, #0ea5e9 100%);
                   color: white; padding: 24px 28px; }}
        .header h1 {{ margin: 0; font-size: 22px; font-weight: 800; }}
        .header p {{ margin: 6px 0 0; font-size: 14px; opacity: 0.85; }}
        .body {{ padding: 28px; }}
        .row {{ display: flex; justify-content: space-between; padding: 10px 0;
                border-bottom: 1px solid #f1f5f9; }}
        .label {{ color: #64748b; font-size: 13px; font-weight: 600; text-transform: uppercase;
                  letter-spacing: 0.05em; }}
        .value {{ color: #0f172a; font-size: 14px; font-weight: 700; text-align: right;
                  max-width: 60%; }}
        .budget-highlight {{ background: #f0f9ff; border: 2px solid #0ea5e9; border-radius: 12px;
                             padding: 16px; margin: 20px 0; text-align: center; }}
        .budget-highlight .amount {{ font-size: 28px; font-weight: 900; color: #0ea5e9; }}
        .cta {{ display: inline-block; background: #25d366; color: white; text-decoration: none;
                padding: 12px 24px; border-radius: 8px; font-weight: 700; margin-top: 16px; }}
        .footer {{ background: #f8fafc; padding: 16px 28px; font-size: 12px; color: #94a3b8; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>🔥 New Investment Lead</h1>
          <p>{PLATFORM_NAME} — Lead Intelligence Dashboard</p>
        </div>
        <div class="body">
          <div class="budget-highlight">
            <div style="font-size:13px;color:#64748b;font-weight:600;margin-bottom:4px;">INVESTMENT BUDGET</div>
            <div class="amount">{budget_label}</div>
          </div>

          <div class="row">
            <span class="label">Name</span>
            <span class="value">{lead.get('name', 'N/A')}</span>
          </div>
          <div class="row">
            <span class="label">Phone</span>
            <span class="value">{lead.get('phone', 'N/A')}</span>
          </div>
          <div class="row">
            <span class="label">Email</span>
            <span class="value">{lead.get('email', 'N/A')}</span>
          </div>
          <div class="row">
            <span class="label">Interest</span>
            <span class="value">{lead.get('interest', 'N/A')}</span>
          </div>
          <div class="row">
            <span class="label">Property</span>
            <span class="value">{lead.get('property', 'N/A')}</span>
          </div>
          <div class="row">
            <span class="label">Service</span>
            <span class="value">{lead.get('service', 'N/A')}</span>
          </div>
          <div class="row">
            <span class="label">Message</span>
            <span class="value">{lead.get('message', 'No message')}</span>
          </div>
          <div class="row">
            <span class="label">Timestamp</span>
            <span class="value">{lead.get('timestamp', 'N/A')}</span>
          </div>

          <a href="https://wa.me/91{lead.get('phone','').replace(' ','')}" class="cta">
            💬 WhatsApp Now
          </a>
        </div>
        <div class="footer">
          This alert was automatically generated by {PLATFORM_NAME}. Log in to your admin panel to manage this lead.
        </div>
      </div>
    </body>
    </html>
    """

    text_body = textwrap.dedent(f"""
        New Lead Alert — {PLATFORM_NAME}
        ================================
        Name    : {lead.get('name', 'N/A')}
        Phone   : {lead.get('phone', 'N/A')}
        Email   : {lead.get('email', 'N/A')}
        Budget  : {budget_label}
        Interest: {lead.get('interest', 'N/A')}
        Property: {lead.get('property', 'N/A')}
        Service : {lead.get('service', 'N/A')}
        Message : {lead.get('message', 'No message')}
        Time    : {lead.get('timestamp', 'N/A')}
    """).strip()

    return _send_email(NOTIFY_EMAIL, subject, html_body, text_body)


# ── Buyer Confirmation Email ──────────────────────────────────────────────────

def send_buyer_confirmation(lead: dict[str, Any]) -> tuple[bool, str]:
    """
    Sends a confirmation email to the buyer/inquirer after they submit a form.
    """
    buyer_email = lead.get("email", "")
    if not buyer_email or "@" not in buyer_email:
        return False, "No valid buyer email"

    subject = f"✅ Your Inquiry is Received — {PLATFORM_NAME}"
    budget_cr = float(lead.get("budget", 0) or 0)
    budget_label = f"₹{budget_cr:.2f} Cr" if budget_cr >= 1 else f"₹{budget_cr * 100:.0f} L"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px;
                      box-shadow: 0 4px 20px rgba(0,0,0,0.08); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #0f172a 0%, #0ea5e9 100%);
                   color: white; padding: 24px 28px; }}
        .header h1 {{ margin: 0; font-size: 22px; font-weight: 800; }}
        .body {{ padding: 28px; }}
        .check {{ font-size: 60px; text-align: center; padding: 16px 0; }}
        .message {{ font-size: 15px; color: #334155; line-height: 1.6; }}
        .highlight {{ background: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 12px 16px;
                      border-radius: 0 8px 8px 0; margin: 16px 0; color: #0f172a; font-weight: 600; }}
        .footer {{ background: #f8fafc; padding: 16px 28px; font-size: 12px; color: #94a3b8; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>🏛️ {PLATFORM_NAME}</h1>
        </div>
        <div class="body">
          <div class="check">✅</div>
          <p class="message">
            Dear <strong>{lead.get('name', 'Investor')}</strong>,<br><br>
            Thank you for your inquiry! We have received your details and our senior advisor
            will connect with you within <strong>2–4 business hours</strong>.
          </p>
          <div class="highlight">
            📋 Inquiry Summary:<br>
            • Budget: <strong>{budget_label}</strong><br>
            • Interest: <strong>{lead.get('interest', 'N/A')}</strong><br>
            • Property: <strong>{lead.get('property', 'N/A')}</strong>
          </div>
          <p class="message">
            Meanwhile, feel free to explore our property intelligence dashboard for
            real-time market insights, AVM valuations, and G-REPI™ rankings.
          </p>
        </div>
        <div class="footer">
          © {datetime.now().year} {PLATFORM_NAME}. This is an automated confirmation email.
        </div>
      </div>
    </body>
    </html>
    """

    return _send_email(buyer_email, subject, html_body)


# ── Welcome Email on Registration ─────────────────────────────────────────────

def send_welcome_email(name: str, email: str) -> tuple[bool, str]:
    """Sends a welcome email to a newly registered user."""
    subject = f"🏛️ Welcome to {PLATFORM_NAME}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px;
                      box-shadow: 0 4px 20px rgba(0,0,0,0.08); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #0f172a 0%, #0ea5e9 100%);
                   color: white; padding: 32px 28px; text-align: center; }}
        .header h1 {{ margin: 0 0 8px; font-size: 26px; font-weight: 900; }}
        .header p {{ margin: 0; opacity: 0.85; font-size: 14px; }}
        .body {{ padding: 28px; }}
        .feature {{ display: flex; align-items: flex-start; margin-bottom: 16px; }}
        .icon {{ font-size: 24px; margin-right: 12px; flex-shrink: 0; }}
        .feat-text {{ font-size: 14px; color: #334155; line-height: 1.5; }}
        .feat-text strong {{ color: #0f172a; }}
        .cta-wrap {{ text-align: center; margin: 24px 0; }}
        .cta {{ display: inline-block; background: linear-gradient(135deg, #0ea5e9, #06b6d4);
                color: white; text-decoration: none; padding: 14px 32px;
                border-radius: 10px; font-weight: 700; font-size: 15px; }}
        .footer {{ background: #f8fafc; padding: 16px 28px; font-size: 12px; color: #94a3b8; text-align: center; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>🏛️ Welcome to AREI™</h1>
          <p>Akhi Real Estate Intelligence Platform</p>
        </div>
        <div class="body">
          <p style="font-size:16px;color:#0f172a;font-weight:600;">
            Hello {name}, welcome aboard! 🎉
          </p>
          <p style="color:#475569;font-size:14px;line-height:1.6;">
            You now have access to India's most advanced property intelligence platform.
            Here's what you can explore:
          </p>

          <div class="feature">
            <div class="icon">📊</div>
            <div class="feat-text"><strong>G-REPI™ Index</strong> — Institutional micro-market performance rankings across Gurugram corridors</div>
          </div>
          <div class="feature">
            <div class="icon">🏷️</div>
            <div class="feat-text"><strong>FairValue AVM™</strong> — 3-tier automated valuation (P15 liquidation, P50 FMV, P85 premium)</div>
          </div>
          <div class="feature">
            <div class="icon">📈</div>
            <div class="feat-text"><strong>IRR Projection Engine</strong> — 5–10 year DCF & cash flow modelling with real appreciation data</div>
          </div>
          <div class="feature">
            <div class="icon">🗺️</div>
            <div class="feat-text"><strong>Corridor Quadrant™</strong> — Investment quadrant classification across 6 Gurugram corridors</div>
          </div>

          <div class="cta-wrap">
            <a href="https://akhiproperties.com" class="cta">Explore Platform →</a>
          </div>
        </div>
        <div class="footer">
          © {datetime.now().year} {PLATFORM_NAME}. You are receiving this because you registered on our platform.
        </div>
      </div>
    </body>
    </html>
    """

    return _send_email(email, subject, html_body)
