# FoodSafe Nigeria 🛡️

An **AI-powered food adulteration detection system** designed to help Nigerian consumers identify potentially unsafe or adulterated food products through visual analysis, machine learning, and cross-referenced regulatory knowledge bases.

## Overview

Food adulteration is a significant public health challenge in Nigeria. FoodSafe empowers consumers to visually inspect food products and receive evidence-based risk assessments backed by regulatory guidance from NAFDAC, WHO, FDA, and international food safety standards.

**Key Features:**
- 🔍 **Visual Analysis**: Computer vision-powered detection of visual anomalies in food products
- 📚 **Multi-Source Knowledge Base**: Cross-referenced safety data from NAFDAC, WHO, FDA, and Codex Alimentarius
- 🤖 **AI-Powered Reasoning**: 4-step LLM pipeline for evidence synthesis and risk scoring
- 📱 **User-Friendly Interface**: Streamlit-based web app for easy image upload and analysis
- 🎯 **Actionable Guidance**: Specific consumer actions tied to detected risks

---

## How It Works

FoodSafe uses a **4-step reasoning pipeline**:

### Step 1: Visual Analysis
- Upload a clear photo of the food product
- Azure Computer Vision API extracts:
  - Dominant colors
  - Objects and tags
  - Image descriptions
- Azure OpenAI analyzes evidence for adulteration cues
- **Output**: Detected anomalies, confidence score, image quality assessment

### Step 2: Knowledge Base Matching
- Searches Azure Search index against detected anomalies
- Matches product against known adulteration patterns
- Retrieves safety guidance from multiple authorities
- **Output**: Matching records with visual signs, health risks, and source citations

### Step 3: Health Risk Assessment
- Synthesizes visual evidence + KB matches
- Generates risk score (1–10)
- Classifies risk level: Safe / Low Risk / Moderate Risk / High Risk / DANGER / Uncertain
- **Output**: Risk assessment with health explanation and likely adulterants

### Step 4: Action Plan
- Recommends immediate consumer action
- Cites knowledge-base sources and authorities
- Provides NAFDAC contact information
- **Output**: Actionable guidance tied to the risk level

---

## Supported Foods

- **Fresh Fruits**: Artificial ripening agents, wax coating, pesticide residue
- **Palm Oil**: Sudan red dye, lard, transformer oil, separation anomalies
- **Ground Pepper**: Brick dust, sawdust, artificial dye, mold contamination
- **Frozen Fish**: Excess ice glazing, refreezing, spoilage masking

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit (Python web framework) |
| **Vision API** | Azure Computer Vision |
| **Language Model** | Azure OpenAI (gpt-4o-mini) |
| **Knowledge Base** | Azure Search (vector + keyword search) |
| **Image Processing** | PIL/Pillow |
| **Authentication** | Azure Identity (DefaultAzureCredential) |
| **Config Management** | python-dotenv |

---

## Prerequisites

- **Python 3.9+**
- **Azure Account** with:
  - Azure AI Foundry project
  - Computer Vision resource
  - OpenAI deployment (gpt-4o-mini)
  - Azure Search service
- **Git** (for version control)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/cipherBT/foodsafe-ai.git
cd foodsafe-ai
```

### 2. Create a Virtual Environment

```bash
python -m venv foodsafe
```

**On Windows:**
```powershell
.\foodsafe\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
source foodsafe/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Azure Credentials

Create a `.env` file in the project root with your Azure credentials:

```env
# Azure AI Foundry
FOUNDRY_PROJECT_ENDPOINT=https://<your-region>.api.azureml.ms
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# Azure Computer Vision
VISION_ENDPOINT=https://<region>.cognitiveservices.azure.com/
VISION_KEY=<your-vision-key>

# Azure Search
AZURE_SEARCH_ENDPOINT=https://<your-search-service>.search.windows.net/
AZURE_SEARCH_KEY=<your-search-key>
AZURE_SEARCH_INDEX=adulteration-kb

# Image Quality
MIN_IMAGE_DIMENSION=400
```

### 5. Build the Knowledge Base Index

```bash
python agents/build_index.py
```

This will:
- Create the Azure Search index schema
- Seed 7 adulteration patterns across multiple authorities
- Make the KB searchable for the app

---

## Usage

### Start the Streamlit App

```bash
streamlit run ui/app.py
```

The app will open at `http://localhost:8501`

### Using the App

1. **Select a food type** from the dropdown:
   - Palm Oil
   - Fresh Fruits
   - Ground Pepper
   - Frozen Fish

2. **Enter your location (LGA)** (e.g., Lagos, Abuja)

3. **Upload a photo** of the food product:
   - Take a clear, well-lit photo
   - Image should show the full product
   - Minimum recommended size: 400×400 pixels

4. **Click "Analyze for Adulteration"**

5. **Review the 4-step analysis**:
   - **Step 1**: Visual analysis and anomalies detected
   - **Step 2**: Knowledge-base matches from regulatory sources
   - **Step 3**: Health risk assessment and risk score
   - **Step 4**: Actionable consumer guidance

---

## Project Structure

```
foodsafe-ai/
├── agents/
│   ├── foodsafe_agent.py       # Core reasoning pipeline
│   └── build_index.py           # Knowledge-base indexer
├── ui/
│   └── app.py                   # Streamlit frontend
├── knowledge_base/              # Future: external KB files
├── requirements.txt             # Python dependencies
├── .env                         # Azure credentials (not committed)
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

## Key Features in Detail

### Image Quality Detection
- Automatically detects images that are too small or low-quality
- Distinguishes between image quality issues and inconclusive evidence
- Prevents false "retake the photo" warnings for clear images

### Multi-Authority Knowledge Base
The system pulls from:
- **NAFDAC** (National Agency for Food and Drug Administration and Control) — Nigerian regulator
- **WHO** (World Health Organization) — International food safety standards
- **FDA** (US Food and Drug Administration) — Produce safety guidance
- **Codex Alimentarius** — International food hygiene principles

### Risk Scoring
Risk scores are calculated based on:
- Visual evidence from the image
- Matched adulteration patterns
- Health risks associated with detected adulterants
- Regulatory guidance from multiple sources

### Confidence Thresholds
- Only high-confidence detections trigger immediate action
- Uncertain cases are marked as inconclusive and reference KB sources
- Configurable image dimension threshold via `MIN_IMAGE_DIMENSION`

---

## Example Workflow

**Scenario**: User uploads a clear Fresh Fruits image

1. **Visual Analysis**:
   - Azure Vision detects: glossy surface, uniform ripening, stem damage
   - Concern level: uncertain (insufficient evidence of adulteration)
   - Confidence: 0.55

2. **KB Matching**:
   - Finds 4 matches: NAFDAC, WHO, FDA, Codex
   - Topics: artificial ripening, waxing, produce safety

3. **Risk Assessment**:
   - Risk level: "Uncertain"
   - Risk score: 0 (can't confirm adulteration)
   - Explanation: "Visual evidence is ambiguous. Reference KB sources for guidance."

4. **Action Plan**:
   - Action: "The image is usable, but the evidence is inconclusive. Compare against the listed sources and buy from trusted sellers."
   - NAFDAC Hotline: 0800-162-3322

5. **UI Display**:
   - ✅ Image is usable (no retake warning)
   - ℹ️ Evidence is inconclusive
   - 📚 Shows all 4 knowledge-base sources
   - 📞 NAFDAC contact info provided

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MIN_IMAGE_DIMENSION` | 400 | Minimum image width/height (pixels) |
| `FOUNDRY_PROJECT_ENDPOINT` | - | Azure AI Foundry endpoint |
| `VISION_ENDPOINT` | - | Azure Computer Vision endpoint |
| `VISION_KEY` | - | Azure Computer Vision key |
| `AZURE_OPENAI_DEPLOYMENT` | - | OpenAI deployment name |
| `AZURE_SEARCH_ENDPOINT` | - | Azure Search endpoint |
| `AZURE_SEARCH_KEY` | - | Azure Search key |
| `AZURE_SEARCH_INDEX` | adulteration-kb | Azure Search index name |

---

## Recent Improvements (v1.1)

✨ **Enhanced confidence handling:**
- Clear but inconclusive photos no longer trigger automatic retake warnings
- Separated image-quality issues from uncertain evidence
- Multi-authority knowledge base for cross-reference validation

✨ **Multi-source support:**
- Added WHO, FDA, and Codex Alimentarius guidance
- Extended Fresh Fruits detection with 4 authority perspectives
- UI now displays all matched authorities

✨ **Smarter recommendations:**
- When evidence is inconclusive but sources are available, app suggests comparison instead of retake
- Action plans now reference source titles and authorities

---

## Testing

### Quick Local Test

```bash
# Activate environment
.\foodsafe\Scripts\Activate.ps1

# Run syntax checks
python -m py_compile agents\foodsafe_agent.py ui\app.py agents\build_index.py

# Rebuild index
python agents\build_index.py

# Start app
streamlit run ui\app.py
```

---

## Troubleshooting

### Azure Credentials Not Working
- Ensure `.env` file is in project root and contains all required keys
- Run: `az login` to refresh Azure authentication

### Index Build Fails
```bash
python agents/build_index.py
```
- Check that `AZURE_SEARCH_ENDPOINT` and `AZURE_SEARCH_KEY` are correct
- Verify index name matches `AZURE_SEARCH_INDEX`

### Streamlit Won't Start
```bash
# Verify packages
pip list | grep streamlit
pip install --upgrade streamlit

# Clear cache
streamlit cache clear
streamlit run ui/app.py
```

### Image Upload Issues
- Ensure image is less than 10MB
- Supported formats: JPG, JPEG, PNG
- For best results, use well-lit images 600×600 pixels or larger

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Commit (`git commit -m "Add your feature"`)
5. Push (`git push origin feature/your-feature`)
6. Open a Pull Request

---

## Roadmap

- [ ] Mobile app integration
- [ ] Offline mode with local model
- [ ] Historical tracking of analyzed products
- [ ] Community reporting and alerts
- [ ] Multi-language support
- [ ] Extended food types (cereals, dairy, beverages)
- [ ] Real-time market data integration

---

## Disclaimer

**Important**: FoodSafe is an AI-powered tool designed to **assist** in identifying potential food safety risks. It is **not a substitute** for:
- Professional lab testing
- Regulatory inspection
- Medical diagnosis or treatment

If you suspect food adulteration or have health concerns, **contact NAFDAC immediately** at **0800-162-3322** or visit **nafdac.gov.ng**.

---

## License

This project is licensed under the MIT License — see LICENSE file for details.

---

## Support & Contact

- 📧 Email: [your-email@example.com]
- 🐛 Report Issues: [GitHub Issues](https://github.com/cipherBT/foodsafe-ai/issues)
- 📞 NAFDAC Hotline: **0800-162-3322**

---

**Made with ❤️ for food safety in Nigeria**
