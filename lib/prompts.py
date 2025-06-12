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

RECOMMEND_INCIDENT_RESOLUTION_OLLAMA_ZERO_SHOT_PROMPT = """
You are an IT support engineer. Your task is to help resolve system issues using the provided incident logs and documentation.

Given:
1. A current incident description
2. Relevant past incidents and documentation from the knowledge base

Context from knowledge base:
{context}

Current incident to resolve:
{input}

Instructions:
1. Look for similar past incidents or documentation in the provided context
2. If you find relevant information, use it to suggest steps to resolve the current incident
3. If you find matching documentation, include its URL in your response

Your response should be:
1. A numbered list of steps to investigate and resolve the issue
2. If you found relevant documentation, add a "References" section with the exact URL

Keep your response focused on practical steps. Do not include explanations or reasoning.
"""