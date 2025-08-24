import anthropic
import json
import re
from config import CLAUDE_API_KEY

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