# One place for every prompt, so they're easy to tune. (Phase 3 moves these to LangChain templates.)

SUMMARIZE = """Summarize this email in 3 short bullet points.
Start each bullet with "• " and a bold category in markdown, like **Action Required:**, **Key Info:** or **FYI:**.

Subject: {subject}
From: {sender}

{body}"""

REPLY = """Write a {tone} reply to this email. Keep it under 120 words.
Only output the reply text, with no subject line and no explanation.

Subject: {subject}
From: {sender}

{body}"""

TASKS = """List every task, request or deadline in this email.
Format each line as: ☐ <task> (due: <date or "no deadline">)
If there are none, reply exactly: No tasks or deadlines found.

Subject: {subject}

{body}"""

CLASSIFY = """Classify this email into exactly one category:
Urgent, Opportunity, Meeting, Promotional, Normal.
Reply with only the category name.

Subject: {subject}
From: {sender}

{body}"""
