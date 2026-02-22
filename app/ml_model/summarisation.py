from app.ml_model.openrouter import summarize

def openai(image_verification,report_verification_result ,risk_assessment):
    module="openai/gpt-oss-20b:free"
    promt ='''
        SYSTEM:
        You are an expert summary generator. Your job is to receive 3 different structured inputs:
        1. image_verification  
        2. report_verification  
        3. risk_assessment  

        Your output MUST be:
        - plain text only  
        - no JSON  
        - no quotes  
        - no markdown formatting except bullet points and section titles  
        - Each bullet <= 20 words  
        - Each sentence <= 25 words  
        - Factual only; do not invent missing details  
        - If any data is empty or unclear, write: “insufficient evidence”  
        - Keep tone professional, neutral, and concise

        Never write long paragraphs. Always use compact, information-dense bullets. 

        USER

        IMAGE_VERIFICATION: ''' + str(image_verification) + ''' (JSON)
        REPORT_VERIFICATION: ''' + str(report_verification_result) + ''' (JSON)
        RISK_ASSESSMENT: ''' + str(risk_assessment) + ''' (JSON)

        TASK:
        Create a clean 4-part summary with the following sections and bullets exactly as defined:

        🔍 Image Verification Summary
        • Image authenticity result
        • 1–2 validated detections (label + confidence)
        • Claim support result (supports / contradicts / unclear)
        • Final image verdict + confidence

        📝 Report Verification Summary
        • Incident category
        • Report validity status
        • Urgency level
        • Key confirmed details (location, persons, objects)

        ⚠️ Risk Assessment Summary
        • Severity score (0–10)
        • Threat probability (%)
        • Final risk score (0–100)
        • Top contributing factors

        📌 Overall Recommendation
        • Combined conclusion (image + report + risk)
        • Recommended action (immediate_dispatch / human_review / monitoring)
        • Any warnings (e.g., insufficient evidence, missing data)

        Give plain text output only. No JSON.
   
    '''
    api_keys = [1, 2, 3, 4, 5, 6]
    for api_key_no in api_keys:
        try:
            # Attempt verification with the current API key
            result = summarize(promt,module, api_key=api_key_no)  # Pass api_key as a keyword argument
            if result is not None:
                return result  # If successful, return the result
            else:
                print(f"API key {api_key_no} returned None, trying next key...")

        except Exception as e:
            # Log the exception message
            print(f"Error with API key {api_key_no}: {str(e)}. Trying next key...")

    # If no valid result is found after all keys, return None
    return None    

def summary_generator(image_verification, report_verification_result, risk_assessment):
    return openai(image_verification, report_verification_result, risk_assessment)
