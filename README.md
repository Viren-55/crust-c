# Claude B2B Sales Agent

This project provides a B2B sales agent that uses the Claude API to generate personalized email outreach based on a user's LinkedIn profile and a product's vision/goal, and then sends the email via SendGrid.

## Setup

1. Clone this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory of the project and add your Claude API key, sender email address, and SendGrid API key:
   ```
   CLAUDE_API_KEY=your_claude_api_key_here
   SENDER_EMAIL=your_sender_email@example.com
   SENDGRID_API_KEY=your_sendgrid_api_key_here
   ```

## Usage

Run the `main.py` script and pipe a JSON object to its standard input. The JSON object should contain the following keys:

- `product_vision`: Your product vision or goal.
- `linkedin_profile`: A JSON string containing the detailed LinkedIn profile data. The script will attempt to extract the recipient's email address from this data and convert it into a readable text format for the Claude API.

Example:

```bash
echo '{"product_vision": "Our cutting-edge AI platform helps businesses automate customer support, reducing response times by 50% and increasing customer satisfaction.", "linkedin_profile": "[ { \"business_email\": [ \"john.doe@example.com\" ], \"current_employers\": [ { \"employer_name\": \"Tech Solutions Inc.\", \"employer_linkedin_id\": \"12345\", \"employer_company_website_domain\": [ \"techsolutions.com\" ], \"business_emails\": { \"john.doe@example.com\": { \"verification_status\": \"verified\", \"last_validated_at\": \"2025-05-18\" } } } ], \"past_employers\": [], \"enriched_realtime\": false, \"query_linkedin_profile_urn_or_slug\": [ \"john-doe-profile\" ] } ]"}' | python claude_agents/main.py
```

The agent will then generate a personalized email (including subject and HTML body) and attempt to send it to the extracted email address using SendGrid.
