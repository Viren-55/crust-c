import json
import re
import anthropic
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

class ClaudeAPI:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    def generate_email_content(self, linkedin_profile_text, product_goal):
        prompt = f"""You are a B2B sales agent. Your goal is to write a personalized email to a potential client based on their LinkedIn profile and our product's vision/goal.

Here is the LinkedIn profile information:
{linkedin_profile_text}

Here is our product vision/goal:
{product_goal}

Generate a concise and compelling email. The email should be in HTML format. The response MUST be a JSON object with two keys: 'subject' for the email subject line, and 'body_html' for the HTML content of the email body. Ensure the HTML is well-formed and suitable for direct use. All newlines and special characters within the 'body_html' string MUST be properly escaped for JSON.

Example JSON output:
{{"subject": "Your personalized subject line", "body_html": "<p>Your email body in HTML format.\nThis is a new line.</p>"}}

Your JSON response:"""

        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",  # Or another suitable Claude model
                max_tokens=1000, # Increased max_tokens for HTML content
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            claude_output = response.content[0].text
            
            # Find the start and end of the JSON object
            json_start = claude_output.find('{')
            json_end = claude_output.rfind('}')

            if json_start != -1 and json_end != -1 and json_end > json_start:
                json_string = claude_output[json_start : json_end + 1]
                parsed_response = json.loads(json_string)
                return parsed_response.get('subject'), parsed_response.get('body_html')
            else:
                print(f"Error: Could not find a valid JSON object in Claude's response: {claude_output}")
                return None, None
        except json.JSONDecodeError as e:
            print(f"Error parsing Claude's JSON response: {e}\nRaw response: {claude_output}")
            return None, None
        except Exception as e:
            print(f"Error generating email content with Claude API: {e}")
            return None, None

def extract_email_from_profile_json(profile_json_str):
    try:
        profile_data = json.loads(profile_json_str)
        if isinstance(profile_data, list) and len(profile_data) > 0:
            # Assuming the first item in the list contains the primary data
            first_profile = profile_data[0]
            if "business_email" in first_profile and first_profile["business_email"]:
                # Assuming the first business email is the one to use
                return first_profile["business_email"][0]
            elif "current_employers" in first_profile and first_profile["current_employers"]:
                for employer in first_profile["current_employers"]:
                    if "business_emails" in employer and employer["business_emails"]:
                        for email, details in employer["business_emails"].items():
                            if details.get("verification_status") == "verified":
                                return email
            elif "past_employers" in first_profile and first_profile["past_employers"]:
                for employer in first_profile["past_employers"]:
                    if "business_emails" in employer and employer["business_emails"]:
                        for email, details in employer["business_emails"].items():
                            if details.get("verification_status") == "verified":
                                return email
    except json.JSONDecodeError:
        print("Warning: linkedin_profile is not a valid JSON string. Attempting regex extraction.")
        return extract_email_from_text(profile_json_str) # Fallback to regex if not valid JSON
    return None

def extract_email_from_text(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    if match:
        return match.group(0)
    return None

def convert_profile_json_to_readable_text(profile_json_str):
    try:
        profile_data = json.loads(profile_json_str)
        if isinstance(profile_data, list) and len(profile_data) > 0:
            first_profile = profile_data[0]
            text_output = "LinkedIn Profile Summary:\n"
            if "business_email" in first_profile and first_profile["business_email"]:
                text_output += f"  Business Email: {first_profile['business_email'][0]}\n"
            if "current_employers" in first_profile and first_profile["current_employers"]:
                text_output += "  Current Employment:\n"
                for employer in first_profile["current_employers"]:
                    text_output += f"    - {employer.get('employer_name', 'N/A')}\n"
                    if "employer_company_website_domain" in employer and employer["employer_company_website_domain"]:
                        text_output += f"      Website: {employer['employer_company_website_domain'][0]}\n"
            if "past_employers" in first_profile and first_profile["past_employers"]:
                text_output += "  Past Employment:\n"
                for employer in first_profile["past_employers"]:
                    text_output += f"    - {employer.get('employer_name', 'N/A')}\n"
            # Add more fields as needed to make it comprehensive for Claude
            return text_output
    except json.JSONDecodeError:
        return profile_json_str # Return original string if not valid JSON
    return ""

def send_email_sendgrid(to_email, subject, body):
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=body)
    try:
        sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)
        response = sendgrid_client.send(message)
        print(f"Email successfully sent to {to_email} via SendGrid.")
        print(f"SendGrid Status Code: {response.status_code}")
        print(f"SendGrid Body: {response.body}")
        print(f"SendGrid Headers: {response.headers}")
    except Exception as e:
        print(f"Error sending email to {to_email} via SendGrid: {e}")

def main():
    # Read JSON input from stdin
    try:
        input_data = json.load(open(0)) # open(0) refers to stdin
        product_vision = input_data['product_vision']
        linkedin_profile_raw = input_data['linkedin_profile'] # This is now the raw JSON string
        # custom_subject is now optional and will be overridden by Claude's subject
    except json.JSONDecodeError:
        print("Error: Invalid JSON input.")
        return
    except KeyError as e:
        print(f"Error: Missing key in JSON input: {e}")
        return

    # Extract email from the structured LinkedIn profile JSON
    receiver_email = extract_email_from_profile_json(linkedin_profile_raw)

    if not receiver_email:
        print("Error: Could not find an email address in the provided LinkedIn profile data.")
        return

    # Convert the structured LinkedIn profile JSON to a readable text for Claude
    linkedin_profile_text_for_claude = convert_profile_json_to_readable_text(linkedin_profile_raw)
    if not linkedin_profile_text_for_claude:
        print("Error: Could not convert LinkedIn profile data to readable text for Claude.")
        return

    claude_api = ClaudeAPI()
    subject, email_body_html = claude_api.generate_email_content(linkedin_profile_text_for_claude, product_vision)

    if subject and email_body_html:
        print("\n--- Generated Personalized Email Preview ---")
        print(f"To: {receiver_email}")
        print(f"From: {SENDER_EMAIL}")
        print(f"Subject: {subject}")
        print("\nHTML Body:\n")
        print(email_body_html)
        print("--------------------------------------------")

        send_email_sendgrid(receiver_email, subject, email_body_html)
    else:
        print("Failed to generate personalized email.")

if __name__ == "__main__":
    main()
