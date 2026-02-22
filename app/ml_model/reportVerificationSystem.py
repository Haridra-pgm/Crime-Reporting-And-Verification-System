from app.ml_model.openrouter import report_verification 

def mistralai(report, imageReportSystem):
    module="mistralai/mistral-7b-instruct-v0.1:free"

    promt ='''
        SYSTEM:
        You are a text forensic assistant . Analyze the provided reporter's textual report and the image verification system's output together. Compare visual observations, detections, scene classification, and validity assessment from the image with the reporter's claims. Output ONLY valid JSON exactly in the schema provided.

        REPORT:
        ''' + str(report) + ''' (json/text)

        IMAGE_VERIFICATION_OUTPUT:
        ''' + str(imageReportSystem) + ''' (JSON)

        TASK:
        Using both inputs, evaluate the crime report and generate:
        1) crime_category (Theft, Robbery, Assault, Kidnapping, Vandalism, Cybercrime, Fraud, Accident, Harassment, Other).
        2) urgency (HIGH, MEDIUM, LOW).
        3) report_validity:
        - "valid" (text matches image findings)
        - "partial" (some match, some conflict)
        - "invalid" (not supported by image)
        4) severity_score (0–10) based on:
        - threat_level
        - presence_of_weapon
        - public_risk
        - harm_potential
        - violence_indicator
        - property_damage
        5) credibility_score (0–100) = text consistency + clarity + coherence.
        6) supporting_evidence_score (0–100) = alignment with image_verification.
        7) key_entities: location, victim, suspect, weapon, object.
        8) summary (<=40 words).

        OUTPUT (JSON ONLY):
        {{
        "crime_category":"",
        "urgency":"",
        "report_validity":"valid|partial|invalid",
        "severity_score": 0,
        "credibility_score": 0,
        "supporting_evidence_score": 0,
        "key_entities":{"location":"","victim":"","suspect":"","weapon":"","object":""},
        "summary":""
        }}
        Provide ONLY JSON. No extra text.
    '''
    api_keys = [1, 2, 3, 4, 5, 6]
    for api_key_no in api_keys:
        try:
            # Attempt verification with the current API key
            result = report_verification(promt,module, api_key=api_key_no)  # Pass api_key as a keyword argument
            if result is not None:
                return result  # If successful, return the result
            else:
                print(f"API key {api_key_no} returned None, trying next key...")

        except Exception as e:
            # Log the exception message
            print(f"Error with API key {api_key_no}: {str(e)}. Trying next key...")

    # If no valid result is found after all keys, return None
    return None


def meta_llama(report, imageReportSystem, mistralai_result):
    module="meta-llama/llama-3.2-3b-instruct:free"

    promt =f'''
        SYSTEM:
        You are a text forensic assistant . Analyze the provided reporter's textual report, the image verification system's output, and the mistralai model's output together. Compare visual observations, detections, scene classification, and validity assessment from the image with the reporter's claims. Output ONLY valid JSON exactly in the schema provided.

        REPORT:
        ''' + str(report) + '''    (json/text)

        IMAGE_VERIFICATION_OUTPUT:
        ''' + str(imageReportSystem) + ''' (JSON)

        mistralai_output :
        ''' + str(mistralai_result) + ''' (JSON)

        TASK:
        Refine and finalize:
        1) final_crime_category
        2) Validate every detection from mistralai_output:
        - validated: true/false
        - adjusted_confidence
        - notes
        3) final_urgency
        4) final_report_validity:
        - valid
        - partial
        - invalid
        5) final_severity_score (0–10) using combined factors:
        - threat_level
        - weapon_presence
        - violence_indicator
        - harm_potential
        - public_safety_risk
        - property_damage
        - emotional_distress_indicator
        - consistency_with_evidence
        6) final_credibility_score (0–100)
        7) final_supporting_evidence_score (0–100)
        8) extracted_details: location, victim, suspect, weapon, motive
        9) consistency ("consistent","partial","inconsistent") using cross-check:
        - original_report
        - mixtral_output
        - image_verification
        10) final_summary (<=50 words)

        OUTPUT (JSON ONLY):
        {{
        "report id" "",
        "final_crime_category":"",
        "mistralai_detections_review":"",
        "final_urgency":"",
        "final_report_validity":"valid|partial|invalid",
        "final_severity_score":0,
        "final_credibility_score":0,
        "final_supporting_evidence_score":0,
        "extracted_details":{{"location":"","victim":"","suspect":"","weapon":"","motive":""}},
        "consistency":"consistent|partial|inconsistent",
        "final_summary":""
        }}       
        
        Provide ONLY JSON. No extra text.
    '''
    api_keys = [1, 2, 3, 4, 5, 6]
    for api_key_no in api_keys:
        try:
            # Attempt verification with the current API key
            result = report_verification(promt,module, api_key=api_key_no)  # Pass api_key as a keyword argument
            if result is not None:
                return result  # If successful, return the result
            else:
                print(f"API key {api_key_no} returned None, trying next key...")

        except Exception as e:
            # Log the exception message
            print(f"Error with API key {api_key_no}: {str(e)}. Trying next key...")

    # If no valid result is found after all keys, return None
    return None

def run_report_verification(report, imageReportSystem):
    mistralai_result = mistralai(report, imageReportSystem)
    final_result = meta_llama(report, imageReportSystem, mistralai_result)
    return final_result




    



