# AI Revenue Recovery Orchestrator

**Track 03:** AI Revenue Recovery  
**Razorpay Buildathon Demo**

---

## 1. Executive Summary & Problem Overview

For an Indian digital business, a failed payment is rarely a lost customer. Instead, revenue slips away across three main failure vectors:

* **Payment Gateway & Issuer Failures:** Bank outages, network timeouts, and OTP delivery delays.
* **Checkout & Cart Drop-offs:** Authentication interruptions, payment-method confusion, and customer hesitation.
* **Subscription Churn & Overdue Receivables:** Expired cards, insufficient funds, revoked mandates, and unpaid B2B invoices.

### The Operational Challenge

Generic retries and aggressive messaging fail in production:
* **Transient Bank Outages** need a delayed retry cool-off, not an immediate retry storm.
* **Expired Cards or Revoked Mandates** should never receive auto-retries; they require payment-method updates.
* **High-Value B2B Overdue Invoices** need human review or structured promise-to-pay workflows.
* **Excessive Outreach** frustrates customers; interventions must enforce strict communication limits.
* **Successful Payments** must trigger an immediate halt to all ongoing recovery workflows.

---

## 2. End-to-End Pipeline & Failure Taxonomy

The orchestrator turns failed transactions into bounded, explainable recovery cases following a strict 8-stage sequence:

$$\text{Detect} \longrightarrow \text{Diagnose} \longrightarrow \text{Score} \longrightarrow \text{Apply Guardrails} \longrightarrow \text{Intervene} \longrightarrow \text{Measure} \longrightarrow \text{Stop} \longrightarrow \text{Audit}$$

```mermaid
graph TD
    %% Styling Definitions
    classDef category fill:#0f172a,stroke:#3b82f6,stroke-width:2px,color:#f8fafc;
    classDef signal fill:#1e293b,stroke:#64748b,stroke-width:1px,color:#cbd5e1;
    classDef impact fill:#450a0a,stroke:#ef4444,stroke-width:2px,color:#fca5a5;
    classDef recovery fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#a7f3d0;

    %% PROBLEM CATEGORIES & SIGNALS
    subgraph PROBLEMS ["PROBLEM: REVENUE LOSS EVENTS"]
        direction TB

        subgraph CAT_A ["1. Payment Gateway & Issuer Failures"]
            A_SIG["<b>Signals:</b><br>• issuer_unavailable<br>• bank_down / bank_timeout<br>• OTP delivery delay<br>• Network / Routing failure"]:::signal
        end

        subgraph CAT_B ["2. Checkout & Cart Drop-offs"]
            B_SIG["<b>Signals:</b><br>• checkout_dropped<br>• auth_failed / OTP drop<br>• Payment-method confusion<br>• Customer hesitation"]:::signal
        end

        subgraph CAT_C ["3. Subscription Churn & Receivables"]
            C_SIG["<b>Signals:</b><br>• insufficient_funds<br>• card_expired / mandate_revoked<br>• invoice_overdue / invoice_unpaid_30d"]:::signal
        end
    end

    %% BUSINESS IMPACT OF UNCHECKED FAILURE
    subgraph IMPACT ["BUSINESS IMPACT OF POOR RECOVERY"]
        I1["<b>Operational & Financial Loss:</b><br>• Revenue lost from temporary payment glitches<br>• Checkout conversion drops due to payment friction<br>• Involuntary subscription churn<br>• High manual workload for support & collections<br>• Customer fatigue & loss from blind retries<br>• Zero auditability for recovery attempts"]:::impact
    end

    %% CORRECT BOUNDED RECOVERY BEHAVIOR
    subgraph RECOVERY ["CORRECT AGENTIC RECOVERY BEHAVIOR"]
        R1["<b>Gateway Strategy:</b><br>• Diagnose transience<br>• Cool-off delay (prevent retry storms)<br>• Hard stop at retry limit"]:::recovery

        R2["<b>Checkout Strategy:</b><br>• Low-friction 1-click UPI / Payment link<br>• Preferred channel outreach<br>• Immediate halt upon payment or decline"]:::recovery

        R3["<b>Subscription Strategy:</b><br>• Align soft declines to salary pay cycles<br>• Request payment-method update on hard declines<br>• Human escalation for high-value B2B"]:::recovery
    end

    %% Relationships
    CAT_A --> A_SIG
    CAT_B --> B_SIG
    CAT_C --> C_SIG

    A_SIG --> I1
    B_SIG --> I1
    C_SIG --> I1

3. Orchestration Explained (backend/services/razorpay_service.py)
The RazorpayService module serves as the execution adapter. It connects the orchestrator's decisions to live Razorpay endpoints or fallback local simulations.

graph TD
    %% Styling Definitions
    classDef adapter fill:#0f172a,stroke:#3b82f6,stroke-width:2px,color:#f8fafc;
    classDef live fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#a7f3d0;
    classDef mock fill:#451a03,stroke:#f59e0b,stroke-width:2px,color:#fef3c7;
    classDef action fill:#1e293b,stroke:#64748b,stroke-width:1px,color:#cbd5e1;
    classDef webhook fill:#4c1d95,stroke:#8b5cf6,stroke-width:2px,color:#ede9fe;

    %% INITIATION & ADAPTER DUAL-MODE LOGIC
    subgraph INIT ["1. DUAL-MODE INITIALIZATION LAYER"]
        Start["<b>RazorpayService.__init__()</b><br>Check Environment Settings"]:::adapter
        CheckKeys{"Keys Present?<br>(KEY_ID & KEY_SECRET)"}:::adapter
        
        LiveClient["<b>LIVE MODE ACTIVATED</b><br>Initializes official razorpay.Client<br>Executes real API requests"]:::live
        MockClient["<b>SIMULATION MODE ACTIVATED</b><br>Sets client = None<br>Prevents crashes & returns mock payloads"]:::mock

        Start --> CheckKeys
        CheckKeys -- "Yes" --> LiveClient
        CheckKeys -- "No / Missing" --> MockClient
    end

    %% INTERVENTION EXECUTIONS
    subgraph ACTIONS ["2. INTERVENTION ORCHESTRATION LAYER"]
        direction TB

        subgraph ACT_1 ["retry_payment(transaction_id)"]
            A1["<b>Goal:</b> Gateway & Issuer Failures<br><b>Flow:</b> Fetches payment status via client<br><b>Output:</b> Schedules background retry window"]:::action
        end

        subgraph ACT_2 ["send_payment_link(transaction_id, amount)"]
            A2["<b>Goal:</b> Checkout & Cart Drop-offs<br><b>Flow:</b> Converts INR to paise (amount * 100) & calls payment_link.create()<br><b>Output:</b> Returns 1-click payment link URL"]:::action
        end

        subgraph ACT_3 ["send_reminder(transaction_id)"]
            A3["<b>Goal:</b> Soft Decline Nudges<br><b>Flow:</b> Triggers SMS / WhatsApp nudge<br><b>Output:</b> Dispatches reminder status"]:::action
        end

        subgraph ACT_4 ["escalate_human(transaction_id)"]
            A4["<b>Goal:</b> Policy Guardrails / High Value<br><b>Flow:</b> Flags case for human review<br><b>Output:</b> Bypasses automation to FinOps"]:::action
        end
    end

    %% WEBHOOK FEEDBACK LOOP
    subgraph WEBHOOK ["3. ASYNCHRONOUS FEEDBACK LAYER"]
        W1["<b>verify_webhook(payload, signature)</b><br>• Uses HMAC SHA-256 (hmac.compare_digest)<br>• Authenticates incoming events (e.g., payment.captured)<br>• Triggers immediate termination of active recovery cases"]:::webhook
    end

    %% Mappings
    LiveClient --> ACTIONS
    MockClient --> ACTIONS

    ACT_1 --> WEBHOOK
    ACT_2 --> WEBHOOK
    ACT_3 --> WEBHOOK
    ACT_4 --> WEBHOOK

4. Key Execution Components
Dual-Mode SDK Resilience: Initializes razorpay.Client if keys are detected. If keys are missing, it defaults to a mock execution adapter to allow local testing and demo simulations without throwing errors.

Action Dispatching:

retry_payment(): Verifies state and schedules background retries to prevent gateway retry storms.

send_payment_link(): Handles currency unit conversion (rupees to paise) and interacts with Razorpay's Payment Link API.

send_reminder(): Triggers customer nudges across SMS and messaging channels.

escalate_human(): Hands off complex or high-value cases to manual FinOps review.

Cryptographic Webhook Verification: Employs HMAC SHA-256 (hmac.compare_digest) signature validation for asynchronous event ingestion, ensuring recovery loops cease as soon as payment capture is confirmed.
    A_SIG ==> R1
    B_SIG ==> R2
    C_SIG ==> R3
