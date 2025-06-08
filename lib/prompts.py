
GENERATE_SYNTHETIC_INCIDENTS_OLLAMA_PROMPT = """
    Generate {count} a synthetic IT support ticket as a valid JSON array.
    Each ticket should represent an issue in a Merchant Onboarding Application used by Sales Agents or Merchants.

    Common issues include: login failures, validation errors, PDF problems, UI bugs, or timeouts.
    These are only examples. **Do not limit the generated incidents to these issues**. 
    Include a variety of scenarios, including **uncommon, edge-case, or unexpected technical problems** that could occur in a real Merchant Onboarding system.

    Ensure each incident has a unique root cause or behavior. Mix both frequent and rare issues across the generated data to improve variety.

    For each ticket:
    - Do not assign incident_number.
    - Vary:
        • Who encountered the issue (Sales Agent or Merchant)
        • Whether it's a common or rare issue
        • urgency: 1 = Critical, 2 = High, 3 = Moderate
        • impact: 1 = High, 2 = Medium, 3 = Low
        • category: Network, Software, Hardware, or Access
        • assignment_group: IT Support or Network Ops
        • short_description and description (concise, realistic)
        • resolution: one or two short, realistic past-tense sentence

    Return only a compact and valid JSON array of objects with the following fields:
    short_description, description, urgency, impact, category, assignment_group, resolution.
"""

GENERATE_SYNTHETIC_DOCS_OLLAMA_PROMPT = """
    You are an expert IT documentation writer. Based on the following incident details,
    write an internal Confluence-style documentation detailing steps to resolve the issue or similar issue.
    The incidents that will be given are from Service Now.

    Context:
    Incident Title: {short_desc}
    Description: {description}
    Resolution: {resolution}

    Generate a synthetic documentation as a JSON object with the following fields:
    - url - randomly generated URL/link for this documentation.
    - title - should not match exactly the incident title. Be creative here and make a title that mimics real-world documentations.
    - overview - overview of what the documentation is for.
    - tools - list tools to use to investigate issue (e.g. Splunk, Jira, etc.)
    - investigation_steps - list of steps to investigate the issue

    Return ONLY the raw JSON object.
"""

GENERATE_SYNTHETIC_DOCS_OPENAI_PROMPT = """
    You are an expert IT documentation writer.

    Given incident details from ServiceNow, generate **internal Confluence-style documentation** that explains how to resolve this or similar issues.
    Structure it in a realistic format used in enterprise knowledge bases.

    ### Incident Context
    - **Incident Title**: {short_desc}
    - **Description**: {description}
    - **Resolution Summary**: {resolution}

    ### Output Instructions
    Return a **valid JSON object** with the following fields:

    - `url`: A realistic, randomly generated internal Confluence-style URL.
    - `title`: A clear and professional title that **does not copy the incident title exactly**. It should sound like a real-world knowledge base article.
    - `overview`: A concise overview describing what the documentation covers.
    - `tools`: A list of tools that could help investigate or resolve this issue (e.g., Splunk, Jira, internal monitoring tools).
    - `investigation_steps`: A step-by-step list of investigation and resolution actions IT staff should take.

    ### Constraints
    - Keep language natural and realistic.
    - Assume the audience is internal IT support or DevOps staff.
    - Do **not** return anything except the raw JSON object.
"""

GENERATE_SYNTHETIC_INCIDENTS_OPENAI_PROMPT = """
    Generate {count} synthetic IT support tickets as a valid, compact JSON array.

    Each ticket should describe a realistic issue encountered in a **Merchant Onboarding Application** used by **Sales Agents** and **Merchants**.

    ### Application Context:
    This is a CRUD application where Sales Agents:
    - Input merchant details
    - Select payment service equipment (e.g., POS terminals)
    - Define applicable fees and optional services

    Merchants use a separate Customer UI to:
    - Log in
    - Review and e-sign a Merchant Agreement (PDF)

    Once signed, onboarding moves to the PROCESSING stage.

    ---

    ### Guidelines:
    - Include both **common** and **rare/edge-case** issues.
    - Ensure a **diverse set of scenarios** across the {count} tickets.
    - Avoid repetitive tickets. Each one should reflect a unique problem or root cause.

    #### Examples of common issues:
    - Sales Agents: login failures, validation errors, fee/rate logic bugs
    - Merchants: agreement not loading, e-sign failures, download issues

    You are NOT limited to these. Invent realistic, plausible technical problems.

    ---

    ### For each ticket, randomly generate the following fields:
    - `user_role`: "Sales Agent" or "Merchant"
    - `issue_type`: "common" or "rare"
    - `urgency`: 1 (Critical), 2 (High), or 3 (Moderate)
    - `impact`: 1 (High), 2 (Medium), or 3 (Low)
    - `category`: "Network", "Software", "Hardware", or "Access"
    - `assignment_group`: "IT Support" or "Network Ops"
    - `short_description`: A concise 1-line summary of the issue
    - `description`: 2-3 sentence context of what happened and who was affected
    - `resolution`: 1-2 short past-tense sentences describing realistic remediation actions

    ---

    ### Output:
    Return **only** a valid JSON array of `{count}` objects with the following keys:
    - `short_description`
    - `description`
    - `urgency`
    - `impact`
    - `category`
    - `assignment_group`
    - `resolution`

    Do not include any markdown, code blocks, or commentary—only return the raw JSON array.
"""

RECOMMEND_INCIDENT_RESOLUTION_OLLAMA_PROMPT = """
You are a senior IT support engineer with expertise in diagnosing system issues using only provided incident logs and documentation.

You will be given:
- A current incident description.
- A set of relevant past incidents and documentation.

These are the only materials available. **Do not make assumptions beyond the given information.**

---

## Context
The following documents and/or past incidents are retrieved from a knowledge base:
{context}

---

## Current Incident
{input}

---

## Internal Guidance (for reasoning only — do NOT include these in your final response)

Think step-by-step:
1. Analyze the incident details.
2. Search the provided context for similar incidents (metadata.source = "ServiceNow").
3. If a match is found, infer the likely root cause and what worked previously.
4. Also look for relevant documentation (metadata.source = "Confluence").
5. Only if you find a **clear match in the context**, list the document title and URL under "References".
6. If no matches are found, state that no similar incidents or documentation were provided.

---

## Final Output

Respond **only** with:
- A **numbered list** of realistic steps to investigate and resolve the issue based on past incidents or documentation.
- A **References** section (if applicable), using exact `url` fields from the context. **Do not make up URLs.**

**Do NOT include your reasoning or the step-by-step process above in the response.**

Example:

**References:**
- [Handling Merchant Login Errors](https://confluence.company.net/docs/merchant-login-errors)

"""