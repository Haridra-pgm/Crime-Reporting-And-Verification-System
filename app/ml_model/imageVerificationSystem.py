from app.ml_model.openrouter import image_verification


def nvida_nemotron_nano(report, image_path):
    module="nvidia/nemotron-nano-12b-v2-vl:free"

    promt ='''
        SYSTEM:
        You are an image + text forensic assistant. Analyze the provided image and the reporter's textual report together. Extract visual observations, detect weapons/fire/vehicles, classify the scene, and check whether the image supports the report. Output ONLY valid JSON exactly in the schema provided. Never identify persons (no PII).

        REPORT:
        ''' + str(report) + ''' (json/text)

        TASK:
        1. check thee image is ai generated or manipulated in any way.
        2. If image is manipulated or ai generated, set `image_status` to "manipulated" and explain why.
        3. If image is unreadable or corrupted, set `image_status` to "unreadable" or "corrupted" and explain why.
        4. If image is ok, set `image_status` to "ok" and proceed.
        5. Describe the image briefly.

        1.  Inspect the image closely. List visual detections of interest (weapons, fire/smoke, vehicles, people, blood, suspicious packages, broken glass, signs of forced entry, flames, open flames, ignition sources). For each detection include: label, confidence (0.0-1.0), bounding_box [x,y,width,height] in image pixels (or normalized 0-1 if pixels unknown).

        2. Inspect the image and return visual detections:
        - label
        - confidence (0.0–1.0)
        - bbox [x,y,width,height]
        - id (d1, d2…)

        3. Perform OCR on visible text (license plates, signs, documents). Return OCR text and bounding boxes if any.
        
        4. Classify the scene into one of: ["normal", "suspicious_activity", "crime_scene_likely", "fire_hazard", "vehicle_incident", "unknown"] with a confidence score.

        4. Compare image vs report_text:
        - verdict: valid | partial | invalid
        - reasons
        - evidence (list detection IDs)
        6. If image is unreadable or obviously manipulated, set `image_validity` to "invalid" and explain why.
        7. Describe the image
        8. Return EXACT JSON ONLY.

        ADDITIONAL GUIDANCE:
        - Use detection confidence >= 0.30 to include an object in detections; provide confidence values precisely.
        - If multiple overlapping detections exist, return all and include notes; downstream stage will reconcile.
        - Do NOT infer identity (no names, no personal data). If image shows a face, report only "person" with bbox.
        - Keep messages short and JSON-only.

        REQUIRED OUTPUT SCHEMA:
        {{
        "report_id": string,
        "image_status": "ok" | "unreadable" | "corrupted" | "manipulated"|"ai_generated",
                "image_describe": string,
        "detections": [
            {{
            "id": string,
            "label": string,
            "confidence": float,
            "bbox": [x,y,width,height],
            "notes": string
            }}
        ],
        "ocr": [
            {{ "text": string, "confidence": float, "bbox": [x,y,width,height] }}
        ],
        "scene_classification": {{ "label": string, "confidence": float }},
        "match_with_report": {{
            "verdict": "valid" | "partial" | "invalid",
            "confidence": float,
            "reasons": [string],
            "evidence": [string]
        }},
        "recommended_next_step": "none" | "escalate" | "verify_more_images" | "notify_authorities" | "preserve_evidence",
        "metadata": {
            "model": "nvidia/nemotron-nano-12b-v2-vl:free",
            "model_stage": "verification"
        }
        }}

        Return ONLY JSON. No prose.
    '''
    api_keys = [1, 2, 3, 4, 5, 6]
    for api_key_no in api_keys:
        try:
            # Attempt verification with the current API key
            result = image_verification(promt, image_path, module, api_key=api_key_no)  # Pass api_key as a keyword argument
            if result is not None:
                return result  # If successful, return the result
            else:
                print(f"API key {api_key_no} returned None, trying next key...")

        except Exception as e:
            # Log the exception message
            print(f"Error with API key {api_key_no}: {str(e)}. Trying next key...")

    # If no valid result is found after all keys, return None
    return None

def google_Gemma(report, image_path, nvida_validation):
    module = "google/gemma-3-4b-it:free"

    promt = '''
        SYSTEM:
        You are a verification model. You receive the original report, the nvida_nemotron_nano first-pass output, and the same image. Your job: verify, validate, reconcile contradictions and produce a final verdict. Output ONLY JSON in the exact schema. No PII.

        USER:
        REPORT:
        ''' + str(report) + ''' (json/text)

        nvida_nemotron_nano_OUTPUT:
        ''' + str(nvida_validation) + ''' (JSON)

        TASK:
        1. chack nvida_nemotron_nano output for completeness and correctness:
        2. check wather the image is 
        3. Validate every detection from nvida_nemotron_nano:
        - validated: true/false
        - adjusted_confidence
        - notes
        4. Inspect the image again for any missed detections:
        - label
        - confidence (0.0–1.0)
        - bbox [x,y,width,height]

        5. Add/remove detections if needed.
        6. Break report_text into claims and validate each:
        - confirmed | contradicted | insufficient_evidence
        7. Produce final_verdict:
        valid | partial | invalid
        8. Recommend actions: ["no_action","request_more_media","notify_local_authorities","preserve_chain_of_evidence","human_review"]
        9. Produce a short 3-4 sentence summary.
        10. Return EXACT JSON ONLY.

        ADDITIONAL GUIDANCE:
        - When aggregating confidence, weigh visual evidence higher than single-word OCR unless OCR is critical (e.g., license plate linked to vehicle ID).
        - If manipulations are suspected (inconsistent lighting, duplicated regions), set `final_verdict` to "partial" or "invalid" and recommend "human_review".
        - For borderline cases (final_confidence between 0.45-0.65), recommend "human_review" and "request_more_media".
        - Avoid PII. If a detection is a person, label only "person".
        - Return JSON only.

        REQUIRED OUTPUT SCHEMA:
        {{
        "report_id": string,
        "image_status": "ok" | "unreadable" | "corrupted" | "manipulated" | "ai_generated",
        "image_describe": string,
        "NVIDA_detections_review": "ok"|"adjusted"|"rejected",
        "final_detections": [
            {{
            "id": string,
            "label": string,
            "validated": boolean,
            "adjusted_confidence": float,
            "bbox": [x,y,width,height],
            "notes": string
            }}
        ],
        "claim_checks": [
            {{
            "claim": string,
            "verdict": "confirmed" | "contradicted" | "insufficient_evidence",
            "evidence_ids": [string],
            "explanation": string
            }}
        ],
        "final_verdict": "valid" | "partial" | "invalid",
        "final_confidence": float,
        "recommended_actions": [
            {{ "action": string, 
            "priority": "low"|"medium"|"high", 
            "reason": string }}
        ],
        "summary": string ,
        "metadata": {
            "model": "google/gemma-3-4b-it:free",
            "model_stage": "verification"
        }
        }

        ONLY JSON. No extra text.
    '''
    api_keys = [1, 2, 3, 4, 5, 6]
    for api_key_no in api_keys:
        try:
            # Attempt verification with the current API key
            result = image_verification(promt, image_path, module, api_key=api_key_no)  # Pass api_key as a keyword argument
            if result is not None:
                return result  # If successful, return the result
            else:
                print(f"API key {api_key_no} returned None, trying next key...")

        except Exception as e:
            # Log the exception message
            print(f"Error with API key {api_key_no}: {str(e)}. Trying next key...")

    # If no valid result is found after all keys, return None
    return None

def verify_image_report(report, image_path):
    nvida_result = nvida_nemotron_nano(report, image_path)
    final_result = google_Gemma(report, image_path, nvida_result)
    return final_result

