"""
POC-wide settings. Values here are read from environment variables where
sensible, with safe local defaults so the POC runs out of the box on SQLite
with no external services configured.
"""

import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./admissions_poc.db")

# Comma-separated list of allowed frontend origins for CORS, e.g.
# "https://your-frontend.onrender.com,http://localhost:5500". Defaults to
# "*" (allow all) for local POC convenience — set this explicitly once the
# frontend has a real deployed URL.
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]

# --- Email ---
# Three modes, checked in this priority order:
#   1. SendGrid  — if SENDGRID_API_KEY is set
#   2. SMTP      — if SMTP_USERNAME and SMTP_PASSWORD are set (works with
#                  Gmail + an app password, or any other SMTP provider)
#   3. Console   — fallback if neither is configured; logs the email instead
#                  of sending it, so the POC runs with zero setup.
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

NOTIFICATION_FROM_EMAIL = os.getenv("NOTIFICATION_FROM_EMAIL", SMTP_USERNAME or "admissions@example.com")

# --- LLM (Anthropic) for generating personalized recommendation explanations ---
# If ANTHROPIC_API_KEY is not set, the explanation service falls back to a
# deterministic template built from the score breakdown — so the POC still
# runs end-to-end with zero LLM cost/setup. Set the key to get natural,
# personalized explanations in the recommendation email.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
# claude-haiku-4-5-20251001 is a good default for this — short, templated
# personalization doesn't need a larger model. Swap to claude-sonnet-5 if
# you want more nuanced writing.
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")

# Number of top recommendations to generate per student
TOP_N_RECOMMENDATIONS = 3

# Approximate CGPA (0-10 scale) -> percentage conversion multiplier.
# This is a common approximation (used e.g. by many Indian universities);
# review/replace with your institution's actual conversion table before
# relying on it for real decisions.
CGPA_TO_PERCENTAGE_MULTIPLIER = 9.5
