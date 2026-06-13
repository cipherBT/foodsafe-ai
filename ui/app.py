import streamlit as st
import sys
import os
from PIL import Image, ImageOps
import io
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agents.foodsafe_agent import run_foodsafe_agent

st.set_page_config(page_title="FoodSafe", page_icon="🛡️", layout="wide")

st.markdown("""
<div style='background-color:#006400; padding:20px; border-radius:8px; margin-bottom:20px'>
    <h1 style='color:white; margin:0'>🛡️ FoodSafe Nigeria</h1>
    <p style='color:#90EE90; margin:5px 0 0 0'>AI-Powered Food Adulteration Detection Agent</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    food_type = st.selectbox("Select food type:", ["Palm Oil", "Fresh Fruits", "Ground Pepper", "Frozen Fish"])
    user_lga = st.text_input("Your Location (LGA):", value="Lagos")
    uploaded_file = st.file_uploader("Upload a photo of the food", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        image = ImageOps.exif_transpose(image).convert("RGB")
        width, height = image.size
        if max(width, height) > 1600:
            image.thumbnail((1600, 1600))
        if min(width, height) < 400:
            st.warning("This photo is quite small. A closer, sharper image will usually classify better.")
        st.image(image, use_container_width=True)
        analyze_btn = st.button("🔍 Analyze for Adulteration", type="primary", use_container_width=True)

with col2:
    if uploaded_file and 'analyze_btn' in locals() and analyze_btn:
        with st.spinner("🤖 Agent running 4-step reasoning analysis..."):
            result = run_foodsafe_agent(uploaded_file.getvalue(), food_type, user_lga)
            
            st.subheader("🔬 Step 1: Visual Analysis")
            st.json(result["step1_visual"])

            visual = result["step1_visual"]
            confidence = visual.get("confidence", 0.0)
            if visual.get("needs_better_photo"):
                st.warning("The image quality is too low for a reliable visual read. Retake the photo in brighter light and closer to the food.")
            elif visual.get("concern_level") == "uncertain":
                st.info("The image is usable, but the evidence is still inconclusive. Review the knowledge-base matches and risk summary below.")
            else:
                st.info(f"Visual confidence: {confidence:.2f}")
            
            st.subheader("📚 Step 2: Knowledge Base Matches")
            if result["step2_kb_matches"]:
                authorities = sorted({match.get("authority") or match.get("source") or "Unknown source" for match in result["step2_kb_matches"]})
                st.success(f"Found {len(result['step2_kb_matches'])} knowledge-base matches from {', '.join(authorities)}.")
            else:
                st.info("No direct matches found.")
                
            st.subheader("⚠️ Step 3: Health Risk Assessment")
            risk = result["step3_risk"]
            if risk.get("risk_level") == "Uncertain":
                st.warning(f"**{risk.get('risk_level', 'Unknown')}** (Score: {risk.get('risk_score', 0)}/10)\n\n{risk.get('health_explanation', '')}")
            else:
                st.error(f"**{risk.get('risk_level', 'Unknown')}** (Score: {risk.get('risk_score', 0)}/10)\n\n{risk.get('health_explanation', '')}")
            
            st.subheader("✅ Step 4: Action Plan")
            st.warning(f"**Action:** {result['step4_action'].get('immediate_action', '')}\n\n**NAFDAC Hotline:** {result['step4_action'].get('nafdac_hotline', '')}")