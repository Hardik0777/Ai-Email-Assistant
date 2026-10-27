"""All prompts as LangChain PromptTemplates: the single source of truth for what the AI is asked."""
from langchain_core.prompts import PromptTemplate

SUMMARIZE = PromptTemplate.from_template(
    """Summarize this email in 3 short bullet points.
Start each bullet with "• " and a bold category in markdown, like **Action Required:**, **Key Info:** or **FYI:**.

Subject: {subject}
From: {sender}

{body}"""
)

REPLY = PromptTemplate.from_template(
    """Write a {tone} reply to this email. Keep it under 120 words.
Only output the reply text, with no subject line and no explanation.

Subject: {subject}
From: {sender}

{body}"""
)

TASKS = PromptTemplate.from_template(
    """List every task, request or deadline in this email.
Format each line as: ☐ <task> (due: <date or "no deadline">)
If there are none, reply exactly: No tasks or deadlines found.

Subject: {subject}

{body}"""
)

CLASSIFY = PromptTemplate.from_template(
    """Classify this email into exactly one category:
Urgent, Opportunity, Meeting, Promotional, Normal.
Reply with only the category name.

Subject: {subject}
From: {sender}

{body}"""
)
