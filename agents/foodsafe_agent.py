import os
import json
import io
from PIL import Image, ImageOps
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

load_dotenv()

MIN_IMAGE_DIMENSION = int(os.getenv("MIN_IMAGE_DIMENSION", "400"))

# Clients
def get_foundry_client():
    return AIProjectClient(
        endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        credential=DefaultAzureCredential()
    )

def get_vision_client():
    return ComputerVisionClient(
        os.getenv("VISION_ENDPOINT"),
        CognitiveServicesCredentials(os.getenv("VISION_KEY"))
    )

def get_search_client():
    return SearchClient(
        endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        index_name=os.getenv("AZURE_SEARCH_INDEX"),
        credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
    )

def safe_json_parse(response_content):
    try:
        return json.loads(response_content)
    except json.JSONDecodeError:
        return {"error": "Failed to parse AI response. Retrying recommended."}


def preprocess_image_bytes(image_bytes: bytes, max_size: int = 1600) -> dict:
    """Normalize image orientation and size before analysis."""
    with Image.open(io.BytesIO(image_bytes)) as image:
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")
        original_width, original_height = image.size

        if max(original_width, original_height) > max_size:
            image.thumbnail((max_size, max_size))

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=92, optimize=True)
        return {
            "image_bytes": buffer.getvalue(),
            "width": image.width,
            "height": image.height,
            "original_width": original_width,
            "original_height": original_height,
        }

# REASONING STEP 1: Visual Analysis
def analyze_image(image_bytes: bytes, food_type: str) -> dict:
    try:
        processed = preprocess_image_bytes(image_bytes)
        image_quality_issue = min(processed["width"], processed["height"]) < MIN_IMAGE_DIMENSION
        vision_client = get_vision_client()
        analysis = vision_client.analyze_image_in_stream(
            image=io.BytesIO(processed["image_bytes"]),
            visual_features=[
                VisualFeatureTypes.color,
                VisualFeatureTypes.tags,
                VisualFeatureTypes.description,
                VisualFeatureTypes.objects,
            ]
        )
        
        dominant_color = analysis.color.dominant_color_foreground if analysis.color else "unknown"
        tags = [
            {"name": tag.name, "confidence": round(tag.confidence, 3)}
            for tag in analysis.tags
            if tag.confidence > 0.5
        ] if analysis.tags else []
        captions = [
            {"text": caption.text, "confidence": round(caption.confidence, 3)}
            for caption in (analysis.description.captions if analysis.description else [])
            if caption.confidence > 0.4
        ]
        objects = [
            {
                "name": getattr(obj, "object_property", getattr(obj, "name", "unknown")),
                "confidence": round(obj.confidence, 3),
            }
            for obj in (analysis.objects if hasattr(analysis, "objects") and analysis.objects else [])
        ]

        evidence_summary = {
            "food_type": food_type,
            "image_quality": {
                "width": processed["width"],
                "height": processed["height"],
                "original_width": processed["original_width"],
                "original_height": processed["original_height"],
            },
            "dominant_color": dominant_color,
            "tags": tags,
            "captions": captions,
            "objects": objects,
        }
        
        project_client = get_foundry_client()
        openai_client = project_client.get_openai_client()
        
        anomaly_check = openai_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You are a Nigerian food safety expert. Use only visible evidence. Return JSON: {\"anomalies\": [...], \"concern_level\": \"low/medium/high/uncertain\", \"confidence\": 0-1, \"key_visual_flags\": \"...\", \"evidence_used\": [...], \"needs_better_photo\": true/false, \"uncertainty_reason\": \"image_quality/evidence_uncertain/none\"}. Set needs_better_photo true only when the image itself is genuinely too blurry, dark, cropped, or too small to inspect. If the image is clear but the adulteration evidence is weak, keep needs_better_photo false and mark uncertainty_reason as evidence_uncertain."},
                {"role": "user", "content": f"Analyze this food image. Evidence: {evidence_summary}. Focus on adulteration cues relevant to {food_type}. If the image is clear but the evidence is still inconclusive, do not ask for a retake; instead mark the result as uncertain and explain the missing evidence."}
            ],
            response_format={"type": "json_object"}
        )
        result = safe_json_parse(anomaly_check.choices[0].message.content)
        if "confidence" not in result:
            result["confidence"] = 0.5
        result["confidence"] = max(0.0, min(1.0, float(result.get("confidence", 0.5))))
        result["needs_better_photo"] = bool(result.get("needs_better_photo", False)) and image_quality_issue
        if image_quality_issue:
            result["needs_better_photo"] = True
            result["uncertainty_reason"] = "image_quality"
        elif result.get("concern_level") == "uncertain" and not result.get("uncertainty_reason"):
            result["uncertainty_reason"] = "evidence_uncertain"
        result["image_quality_issue"] = image_quality_issue
        result["evidence_summary"] = evidence_summary
        return result
    except Exception as e:
        return {
            "anomalies": [f"Vision API Error: {str(e)}"],
            "concern_level": "unknown",
            "confidence": 0.0,
            "key_visual_flags": "Error",
            "needs_better_photo": True,
            "uncertainty_reason": "image_quality",
        }

# REASONING STEP 2: Knowledge Base Match
def search_knowledge_base(food_type: str, anomaly_description: str) -> list:
    try:
        search_client = get_search_client()
        query = f"{food_type} {anomaly_description}".strip()
        results = search_client.search(search_text=query, top=3)
        return [
            {
                "authority": r.get("authority"),
                "food_item": r.get("food_item"),
                "adulterant": r.get("adulterant"),
                "visual_signs": r.get("visual_signs"),
                "health_risks": r.get("health_risks"),
                "nafdac_action": r.get("nafdac_action"),
                "source": r.get("source"),
                "reference_url": r.get("reference_url"),
            }
            for r in results
        ]
    except Exception:
        return []

# REASONING STEP 3: Risk Assessment
def generate_risk_assessment(food_type: str, visual_result: dict, kb_matches: list) -> dict:
    try:
        openai_client = get_foundry_client().get_openai_client()
        if visual_result.get("needs_better_photo"):
            return {
                "risk_score": 0,
                "risk_level": "Uncertain",
                "likely_adulterants": [],
                "health_explanation": "The image quality is too weak for a reliable risk judgment. Ask for a clearer, closer, well-lit photo.",
            }
        risk_response = openai_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You are a public health expert. Base the risk score only on visible evidence and KB matches. Return JSON: {\"risk_score\": 1-10, \"risk_level\": \"Safe/Low Risk/Moderate Risk/High Risk/DANGER\", \"likely_adulterants\": [\"...\"], \"health_explanation\": \"...\", \"confidence\": 0-1}. If evidence is weak, choose Uncertain."},
                {"role": "user", "content": f"Food: {food_type}. Visual evidence: {visual_result}. DB Matches: {kb_matches}. Generate a conservative risk assessment."}
            ],
            response_format={"type": "json_object"}
        )
        return safe_json_parse(risk_response.choices[0].message.content)
    except Exception as e:
        return {"risk_score": 0, "risk_level": "Error", "health_explanation": str(e), "confidence": 0.0}

# REASONING STEP 4: Action Plan
def generate_action_plan(food_type: str, risk_assessment: dict, kb_matches: list) -> dict:
    try:
        openai_client = get_foundry_client().get_openai_client()
        if risk_assessment.get("risk_level") == "Uncertain":
            if any(match.get("authority") and match.get("authority") != "NAFDAC" for match in kb_matches):
                return {
                    "immediate_action": "The image is usable, but the evidence is inconclusive. Compare the result against the listed knowledge-base sources and buy only from trusted sellers.",
                    "nafdac_hotline": "0800-162-3322",
                    "should_file_community_report": False,
                }
            return {
                "immediate_action": "Retake the photo in bright light, closer to the product, and with the full item in frame.",
                "nafdac_hotline": "0800-162-3322",
                "should_file_community_report": False,
            }
        action_response = openai_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "You are a Nigerian safety advisor. Return JSON: {\"immediate_action\": \"...\", \"nafdac_hotline\": \"0800-162-3322\", \"should_file_community_report\": true}. Be conservative if the evidence is weak. Reference the knowledge-base authorities and source titles when they are available."},
                {"role": "user", "content": f"Food: {food_type}. Risk: {risk_assessment}. KB matches: {kb_matches}. What should the consumer do?"}
            ],
            response_format={"type": "json_object"}
        )
        return safe_json_parse(action_response.choices[0].message.content)
    except Exception:
        return {"immediate_action": "Discard product and consult NAFDAC.", "nafdac_hotline": "0800-162-3322"}

# ORCHESTRATOR
def run_foodsafe_agent(image_bytes: bytes, food_type: str, user_lga: str = "Lagos") -> dict:
    visual_result = analyze_image(image_bytes, food_type)
    kb_matches = search_knowledge_base(
        food_type,
        f"{visual_result.get('key_visual_flags', '')} {visual_result.get('anomalies', [])}"
    )
    risk_assessment = generate_risk_assessment(food_type, visual_result, kb_matches)
    action_plan = generate_action_plan(food_type, risk_assessment, kb_matches)
    
    return {
        "step1_visual": visual_result,
        "step2_kb_matches": kb_matches,
        "step3_risk": risk_assessment,
        "step4_action": action_plan
    }