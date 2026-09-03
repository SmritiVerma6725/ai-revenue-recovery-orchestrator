from fastapi import FastAPI, Header, Request
from fastapi.responses import HTMLResponse

from backend.demo import (
    build_agent_decision,
    build_audit_trail,
    build_demo_dashboard,
    build_recovery_cases,
    build_recovery_timeline,
    build_revenue_trend,
    simulate_recovery,
)
from backend.services.webhook_service import WebhookService
from backend.services.razorpay_service import RazorpayService

app = FastAPI(title="AI Revenue Recovery Orchestrator", version="0.1.0")
webhook_service = WebhookService()
razorpay_service = RazorpayService()


def render_dashboard_page() -> HTMLResponse:
    summary = build_demo_dashboard()
    cards = [
        ("Revenue at Risk", f"₹{summary['revenue_at_risk']:,}"),
        ("Recoverable Amount", f"₹{summary['recoverable_amount']:,}"),
        ("Recovered Amount", f"₹{summary['recovered_amount']:,}"),
        ("Recovery Rate", f"{summary['recovery_rate']}%"),
    ]
    cards_html = "".join(
        f"<div class='card'><span>{label}</span><strong>{value}</strong></div>" for label, value in cards
    )
    trend = build_revenue_trend()
    chart_width = 900
    chart_height = 260
    max_daily = max(item["recovered_amount"] for item in trend)
    max_cumulative = max(item["cumulative_recovered"] for item in trend)
    bar_width = chart_width / len(trend)
    bars_html = "".join(
        f"<rect x='{index * bar_width + 3:.1f}' y='{chart_height - (item['recovered_amount'] / max_daily) * 180:.1f}' width='{max(4, bar_width - 6):.1f}' height='{(item['recovered_amount'] / max_daily) * 180:.1f}' class='revenue-bar'><title>Day {item['day']}: ₹{item['recovered_amount']:,}</title></rect>"
        for index, item in enumerate(trend)
    )
    points = " ".join(
        f"{index * bar_width + bar_width / 2:.1f},{chart_height - (item['cumulative_recovered'] / max_cumulative) * 220:.1f}"
        for index, item in enumerate(trend)
    )
    labels_html = "".join(
        f"<span style='left:{index * 100 / (len(trend) - 1):.1f}%'>{item['day']}</span>"
        for index, item in enumerate(trend)
        if item["day"] in {1, 5, 10, 15, 20, 25, 30}
    )
    return HTMLResponse(
        f"""
        <html>
            <head>
                <title>AI Revenue Recovery</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; background: #f4f7fb; color: #1d2736; }}
                    .container {{ max-width: 1200px; margin: 40px auto; padding: 24px; }}
                    .topbar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }}
                    .brand {{ font-size: 28px; font-weight: 700; }}
                    .nav {{ display: flex; gap: 16px; }}
                    .nav a {{ text-decoration: none; color: #2144d5; font-weight: 600; }}
                    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }}
                    .card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.05); }}
                    .card span {{ display: block; color: #68778d; margin-bottom: 12px; }}
                    .card strong {{ font-size: 28px; }}
                    .panel {{ background: white; border-radius: 12px; padding: 20px; margin-top: 24px; box-shadow: 0 8px 24px rgba(0,0,0,0.05); }}
                    h2 {{ margin-top: 0; }}
                    .badge {{ display: inline-block; background: #eaf6ef; color: #0d7f45; padding: 6px 10px; border-radius: 999px; font-weight: 700; }}
                    .demo-action {{ margin-top: 16px; padding: 12px 16px; border: 0; border-radius: 8px; background: #2144d5; color: white; font-weight: 700; cursor: pointer; }}
                    #demo-status {{ margin-left: 12px; color: #0d7f45; font-weight: 600; }}
                    .chart-header {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; }}
                    .legend {{ color: #68778d; font-size: 13px; }}
                    .chart {{ position: relative; overflow-x: auto; padding-bottom: 24px; }}
                    .chart svg {{ display: block; min-width: 720px; width: 100%; height: 260px; background: linear-gradient(to bottom, #f8fbff, #ffffff); border-bottom: 1px solid #dce5f0; }}
                    .revenue-bar {{ fill: #8db7ff; opacity: .8; }}
                    .cumulative-line {{ fill: none; stroke: #e35d6a; stroke-width: 4; stroke-linecap: round; stroke-linejoin: round; }}
                    .chart-labels {{ position: absolute; left: 0; right: 0; bottom: 0; height: 20px; min-width: 720px; }}
                    .chart-labels span {{ position: absolute; transform: translateX(-50%); color: #68778d; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class='container'>
                    <div class='topbar'>
                        <div class='brand'>AI Revenue Recovery</div>
                        <div class='nav'>
                            <a href='/'>Overview</a>
                            <a href='/dashboard'>Dashboard</a>
                            <a href='/api/recovery-cases'>Recovery Cases</a>
                        </div>
                    </div>
                    <div class='grid'>{cards_html}</div>
                    <div class='panel'>
                        <div class='chart-header'>
                            <h2>Monthly recovery performance</h2>
                            <span class='legend'>Blue: daily recovered revenue · Red: cumulative recovery</span>
                        </div>
                        <div class='chart'>
                            <svg viewBox='0 0 {chart_width} {chart_height}' role='img' aria-label='Revenue recovered by day during the month'>
                                {bars_html}
                                <polyline points='{points}' class='cumulative-line'></polyline>
                            </svg>
                            <div class='chart-labels'>{labels_html}</div>
                        </div>
                    </div>
                    <div class='panel'>
                        <h2>Executive overview</h2>
                        <p>Recovered revenue is growing faster than the baseline, with the most efficient actions focused on customers with repeat-payment history and strong lifetime value.</p>
                        <p><span class='badge'>Demo mode</span> 2,840 high-probability cases identified and monitored.</p>
                        <button class='demo-action' onclick='simulateRecovery()'>Simulate recovered payment</button>
                        <span id='demo-status'></span>
                    </div>
                </div>
                <script>
                    async function simulateRecovery() {{
                        const response = await fetch('/api/demo/simulate-recovery', {{ method: 'POST' }});
                        const data = await response.json();
                        document.getElementById('demo-status').textContent = 'Recovered amount updated to ₹' + data.recovered_amount.toLocaleString('en-IN');
                        window.setTimeout(() => window.location.reload(), 700);
                    }}
                </script>
            </body>
        </html>
        """
    )


@app.get("/")
def index_page() -> HTMLResponse:
    return render_dashboard_page()


@app.get("/dashboard")
def dashboard_page() -> HTMLResponse:
    return render_dashboard_page()


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "ai-revenue-recovery"}


@app.get("/api/dashboard")
def dashboard() -> dict:
    return build_demo_dashboard()


@app.post("/api/demo/simulate-recovery")
def demo_simulate_recovery() -> dict:
    return simulate_recovery()


@app.get("/api/recovery-cases")
def recovery_cases() -> list[dict]:
    return build_recovery_cases()


@app.get("/api/agent/decision")
def agent_decision() -> dict:
    return build_agent_decision()


@app.get("/api/audit-trail")
def audit_trail() -> list[dict]:
    return build_audit_trail()


@app.get("/api/recovery-timeline")
def recovery_timeline() -> list[dict]:
    return build_recovery_timeline()


@app.post("/api/webhooks/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None),
) -> dict:
    payload = await request.json()
    if not razorpay_service.verify_webhook(payload, x_razorpay_signature):
        return {"status": "rejected", "message": "Webhook signature verification failed."}
    return webhook_service.process_event(payload)
