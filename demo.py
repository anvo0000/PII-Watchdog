import json
import boto3

class PiiDetection:
    """
    A class to detect PII, using Bedrock and Claude 3.5 Sonnet.
    Flexible detection styles: detail or quick check
    """
    # Class-level configuration for Bedrock
    BEDROCK_SERVICE = "bedrock-runtime"
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
