import json
import boto3

class PiiDetection:
    """
    A class to detect PII, using Bedrock and Claude 3.5 Sonnet.
    Flexible detection styles: detail or quick check
    """
    # Class-level configuration for Bedrock
    BEDROCK_SERVICE = "bedrock-runtime"
    BEDROCK_REGION = "us-west-2"
    DEFAULT_MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"

    def __init__(self,
                 user_text: str = "N/A",
                 model_id: str = DEFAULT_MODEL_ID,
                 is_detail: bool = False
                 ):
        self.user_text = user_text
        self.model_id = model_id
        self.is_detail = is_detail

    def _create_prompt(self) -> str:
        simple_prompt = f"""Does the following email contain personal information 
                          (such as names, emails, phone numbers, addresses, financial information, etc.)?
                          Respond with 'Yes' or 'No' and list the detected PII if applicable: {self.user_text}"""

        mega_prompt = f"""COMPREHENSIVE PII DETECTION ANALYSIS
                OBJECTIVE:
                Conduct an exhaustive scan of the provided text to identify and categorize all Personally Identifiable Information (PII).

                DETECTION GUIDELINES:
                1. Identify ALL forms of PII, including but not limited to:
                   - Full names
                   - Email addresses
                   - Phone numbers
                   - Physical addresses
                   - Social security numbers
                   - Financial information
                   - Professional contact details

                2. CRITICAL CLASSIFICATION RULES:
                   - Confirm existence of PII with absolute certainty
                   - Provide specific type and category of each PII element
                   - Highlight potential privacy risks
                   - Use structured, clear output format

                EXPECTED OUTPUT FORMAT:
                ```
                PII DETECTION RESULT:
                - Total PII Elements Found: [X]
                - Specific PII Breakdown:
                  1. Name PII: (Details) (If NO then eliminate this line)
                  2. Email PII: (Details) (If NO then eliminate this line)
                  3. Contact PII: (Details) (If NO then eliminate this line)
                  4. Professional PII: (Details) (If NO then eliminate this line)

                PRIVACY RISK ASSESSMENT:
                - Risk Level: [Low/Medium/High]
                - Recommended Action: Use one of these keywords: [Anonymize/Redact/Review]
                
                Don't need to check the email closing and email signature.
                ```
                TEXT TO ANALYZE:
                {self.user_text}
                PERFORM EXHAUSTIVE PII SCAN NOW."""
        return mega_prompt if self.is_detail else simple_prompt

    def detect_pii(self) -> str:
        prompt = self._create_prompt()
        print(self.is_detail)
        print(self.user_text)

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.9,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        try:
            bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-west-2")
            response = bedrock.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=body
            )
            # Parse the response
            response_body = json.loads(response['body'].read().decode('utf-8'))
            return response_body['content'][0]['text']
        except Exception as error_msg:
            raise error_msg




# Check
# user_text1 = """Craft messaging that resonates by blending content and technology
#     Build trust through transparency to power smarter personalization
#     Leverage AI as your copilot to create lasting customer connections - and Speaker lineup
#     Jarrett Wong - jarrett.wong@braze.com, address WA9826 """

# user_text1="This is excellent course for beginners to kick-start with GenAI journey in AWS. The compilation of sections are perfect and Alex Dan has good teaching skills to explain the concepts from the scratch."
# agent = PiiDetection(user_text1, is_detail=True)
# result = agent.detect_pii()
# print(result)

# Quick Check
# Yes
# Personal Information found:
# - Name: Jarrett Wong
# - Email: jarrett.wong@braze.com
# - Address code/number: WA9826


###Detail check and Recommendation
# PII DETECTION RESULT:
# - Total PII Elements Found: 3
#
# - Specific PII Breakdown:
#   1. Name PII: YES (Details: "Jarrett Wong")
#   2. Email PII: YES (Details: "jarrett.wong@braze.com")
#   3. Contact PII: YES (Details: Address reference "WA9826")
#   4. Professional PII: YES (Association with business email domain "braze.com")
#
# PRIVACY RISK ASSESSMENT:
# - Risk Level: HIGH
# - Recommended Action: REDACT
#
# Detailed Findings:
# 1. Full name and professional identity exposed
# 2. Direct business email contact information revealed
# 3. Partial address/identifier present
# 4. Professional affiliation can be determined through email domain
#
# Recommendations:
# 1. Redact or anonymize the email address
# 2. Remove or obscure the full name
# 3. Remove address reference
# 4. Consider using generic role descriptions instead of specific identifiers
#
# Note: The combination of multiple PII elements (name + email + address) creates a higher risk profile as these can be used together for identity verification or potential misuse.