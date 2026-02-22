from app.ml_model.openrouter import risk_assessment_system

def xAI_Grok(report, imageReportSystemreport , reportVerificationSystem):
    module="x-ai/grok-4.1-fast:free"
    promt ='''
        SYSTEM:
        You are a deterministic numeric prediction assistant. Produce ONLY the exact JSON specified below and nothing else. Follow the calculation rules precisely, include a short calculation_breakdown, and keep explanation fields concise. Do not produce prose outside the JSON.

        USER:
        INPUT:
        report = ''' + str(report) + '''  (json/text)         
        image_verification = ''' + str(imageReportSystemreport) + ''' (JSON)
        report_verification = ''' + str(reportVerificationSystem) + ''' (JSON)

        OVERVIEW:
        Compute a severity / risk baseline using structured factors. Use deterministic math and return an explainable breakdown.

        FACTOR SCORES (scale):
        - weapon_presence: 0–10 (based on detections + report)
        - violence_indicator: 0–10 (language cues + image)
        - public_risk: 0–10 (crowd, location type)
        - property_damage: 0–10
        - manipulation_score: 0–100 (higher = likely manipulated) — from image_verification if present
        - image_quality_score: 0–100 (higher = good)
        - temporal_proximity_days: integer days since incident (0 if now)
        - witnesses_count: integer (0 if none mentioned)
        - prior_incidents_score: 0–10 (known risk at location)

        NORMALIZATIONS:
        - Convert credibility/supporting_evidence from 0–100 into 0–10 by dividing by 10 when used in factor math.

        SEVERITY FORMULA (apply exactly, round to 1 decimal):
        severity_raw = 0.22*weapon_presence + 0.20*violence_indicator + 0.15*public_risk + 0.10*property_damage + 0.08*(supporting_evidence_score/10) + 0.08*(credibility_score/10) + 0.07*(prior_incidents_score) + 0.05*min(10, max(0, (5 - temporal_proximity_days))) - 0.07*(manipulation_score/10)*(image_quality_score<40 ? 1 : 0.5)
        Then:
        severity_score = clamp(round(severity_raw,1), 0.0, 10.0)

        RISK / THREAT / CONFIDENCE:
        - risk_score = round(severity_score * 10) // 0–100
        - threat_probability = integer estimate 0–100 based on severity_score and violence_indicator
        - severity_confidence (0–100) = round( 0.5*(image_quality_score) * 0.01*100 + 0.5*(supporting_evidence_score) ) normalized and clipped; if manipulation_score>60 reduce confidence by 30 points (min 0).

        UNCERTAINTY: compute a simple interval by:
        - interval_half_width = max(0.5, 1.5 * (1 - severity_confidence/100) * severity_score/2) // then round to 1 decimal
        - severity_interval = [max(0.0, severity_score - interval_half_width), min(10.0, severity_score + interval_half_width)]

        RECOMMENDED_ACTION RULES (apply strictly):
        - "immediate_dispatch" if severity_score >= 7.0 or threat_probability >= 65
        - "human_review" if 4.0 <= severity_score < 7.0 or 40 <= threat_probability < 65 or manipulation_score > 50 or severity_interval_span > 2.0
        - "monitor_and_collect" if 2.0 <= severity_score < 4.0
        - "no_action" if severity_score < 2.0 and supporting_evidence_score < 25

        OUTPUT JSON (EXACT KEYS; JSON ONLY):
        {{
        "report_id": "",

        "severity_score": 0.0,                     // 0.0 - 10.0 (one decimal)
        "severity_interval": [0.0, 0.0],          // 1-decimal

        "severity_confidence": 0,                 // 0 - 100
        "threat_probability": 0,                  // 0 - 100 integer
        "risk_score": 0,                          // 0 -100 integer

        "factors": {{
            "weapon_presence": 0.0,
            "violence_indicator": 0.0,
            "public_risk": 0.0,
            "property_damage": 0.0,
            "supporting_evidence_score": 0,         // 0-100
            "credibility_score": 0,                 // 0-100
            "manipulation_score": 0,                // 0-100
            "image_quality_score": 0,               // 0-100
            "temporal_proximity_days": 0,
            "witnesses_count": 0,
            "prior_incidents_score": 0.0
        }},

        "calculation_breakdown": "",              // <= 30 words: main factors affecting severity
        "recommended_action": "",                 // one of immediate_dispatch|human_review|monitor_and_collect|no_action
        "explanation": "",                        // <= 30 words

        "metadata": {{"model":"x-ai/grok-4.1-fast","processing_time_ms":0}}
        }}

        ADDITIONAL INSTRUCTIONS:
        - Copy report_id from input when available.
        - Round numeric values as specified.
        - Keep calculation_breakdown and explanation short.
        - Return JSON only.

        '''
    api_keys = [1, 2, 3, 4, 5, 6]
    for api_key_no in api_keys:
        try:
            # Attempt verification with the current API key
            result = risk_assessment_system(promt,module, api_key=api_key_no)  # Pass api_key as a keyword argument
            if result is not None:
                return result  # If successful, return the result
            else:
                print(f"API key {api_key_no} returned None, trying next key...")

        except Exception as e:
            # Log the exception message
            print(f"Error with API key {api_key_no}: {str(e)}. Trying next key...")

    # If no valid result is found after all keys, return None
    return None    

def Qwen3(report, imageReportSystemreport , reportVerificationSystem, xAI_Grok_result):
    module="qwen/qwen3-4b:free"
    promt ='''
        SYSTEM:
        You are a numeric calibrator and uncertainty estimator. Use the prior (grok_output) and the raw inputs to produce a calibrated posterior severity with 90% credible interval, refined probabilities, and final action. Return ONLY the exact JSON below and nothing else.

        USER:
        INPUT:
        original_report = ''' + str(report) + '''  (json/text)                    
        grok_output = ''' + str(xAI_Grok_result) + ''' (JSON)   
        image_verification = ''' + str(imageReportSystemreport) + ''' (JSON)
        report_verification = ''' + str(reportVerificationSystem) + ''' (JSON)

        GUIDANCE / MATH NOTES:
        - Treat grok_output.severity_score as prior mean μ0 and derive a prior std σ0 = max(0.8, 0.12 * μ0 + 0.8) (use this formula).
        - Build an evidence_strength factor E in [0.1,2.0]:
        E = 1.0 + 0.01*(grok_output.factors.supporting_evidence_score - 50)/50 + 0.01*(grok_output.factors.credibility_score - 50)/50 - 0.01*(grok_output.factors.manipulation_score - 30)/70
        then clamp E to [0.1,2.0].
        - Compute an evidence-based observed severity s_obs by re-evaluating factors (weighted average like grok but allow +/-10% adjustment if image_verification suggests so).
        - Use simple precision-weighted update:
        prior_precision = 1/(σ0^2)
        evidence_std = max(0.8, 0.15 * s_obs + 0.5)/E
        evidence_precision = 1/(evidence_std^2)
        posterior_mean = (prior_precision*μ0 + evidence_precision*s_obs) / (prior_precision + evidence_precision)
        posterior_std = sqrt(1/(prior_precision + evidence_precision))
        - final_severity_score = clamp(round(posterior_mean,1),0.0,10.0)
        - severity_interval (90%): [posterior_mean - 1.645*posterior_std, posterior_mean + 1.645*posterior_std] rounded to 1 decimal, clamped to [0,10].

        REFINED METRICS:
        - calibrated_threat_probability: integer 0–100 computed from final_severity_score, violence_indicator, weapon_presence, and image verification match (increase if image supports).
        - final_risk_score = round(final_severity_score * 10)
        - final_supporting_evidence_score and final_credibility_score: re-weighted (0–100), show numbers used.
        - If manipulation_score > 60, reduce evidence weight significantly and note in calibration_note.

        RECOMMENDATION MAPPING:
        - immediate_dispatch if final_severity_score >= 7.0 or calibrated_threat_probability >= 65
        - human_review if 4.0 <= final_severity_score < 7.0 or 40 <= calibrated_threat_probability < 65 or posterior_std*10 > 1.2
        - monitor_and_collect otherwise (unless final_supporting_evidence_score < 20 then no_action)

        OUTPUT JSON (EXACT KEYS; JSON ONLY):
        {{
        "report_id": "",
        "prior_severity_mean": 0.0,
        "prior_severity_std": 0.0,
        "evidence_severity": 0.0,
        "evidence_strength": 0.0,
        "final_severity_score": 0.0,
        "severity_interval": [0.0,0.0],
        "posterior_std": 0.0,
        "calibrated_threat_probability": 0,
        "threat_interval": [0,0],
        "final_risk_score": 0,
        "final_supporting_evidence_score": 0,
        "final_credibility_score": 0,
        "adjusted_factors": {{
            "weapon_presence": 0.0,
            "violence_indicator": 0.0,
            "public_risk": 0.0,
            "property_damage": 0.0
        }},
        "calibration_note": "",                 // <= 30 words
        "final_recommendation": "",             // immediate_dispatch|human_review|monitor_and_collect|no_action
        "metadata": {{"model":"qwen/qwen3-235b-a22b","processing_time_ms":0}}
        }}

        ADDITIONAL INSTRUCTIONS:
        - Copy report_id when available.
        - Provide numeric rounding as specified.
        - If grok_output missing, compute baseline from inputs and proceed.
        - Keep calibration_note concise and factual.
        - Return JSON only.
                '''
    api_keys = [1, 2, 3, 4, 5, 6]
    for api_key_no in api_keys:
        try:
            # Attempt verification with the current API key
            result = risk_assessment_system(promt,module, api_key=api_key_no)  # Pass api_key as a keyword argument
            if result is not None:
                return result  # If successful, return the result
            else:
                print(f"API key {api_key_no} returned None, trying next key...")

        except Exception as e:
            # Log the exception message
            print(f"Error with API key {api_key_no}: {str(e)}. Trying next key...")

    # If no valid result is found after all keys, return None
    return None    

def run_risk_assessment(report, imageReportSystemreport , reportVerificationSystem):
    grok_result = xAI_Grok(report, imageReportSystemreport , reportVerificationSystem)
    final_result = Qwen3(report, imageReportSystemreport , reportVerificationSystem, grok_result)
    return final_result


