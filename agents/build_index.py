import os
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchFieldDataType
)
from azure.core.credentials import AzureKeyCredential

load_dotenv()

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX")

def build():
    print(f"Connecting to Search Service: {SEARCH_ENDPOINT}")
    index_client = SearchIndexClient(SEARCH_ENDPOINT, AzureKeyCredential(SEARCH_KEY))
    
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="authority", type=SearchFieldDataType.String),
        SearchableField(name="food_item", type=SearchFieldDataType.String),
        SearchableField(name="adulterant", type=SearchFieldDataType.String),
        SearchableField(name="visual_signs", type=SearchFieldDataType.String),
        SearchableField(name="health_risks", type=SearchFieldDataType.String),
        SearchableField(name="nafdac_action", type=SearchFieldDataType.String),
        SearchableField(name="source", type=SearchFieldDataType.String),
        SearchableField(name="reference_url", type=SearchFieldDataType.String),
    ]
    
    index = SearchIndex(name=INDEX_NAME, fields=fields)
    index_client.create_or_update_index(index)
    print(f"Index '{INDEX_NAME}' ready.")

    documents = [
        {
            "id": "palm-oil-001",
            "authority": "NAFDAC",
            "food_item": "Palm Oil",
            "adulterant": "Sudan red dye, lard (pork fat), transformer oil (paraffin)",
            "visual_signs": "Abnormally bright red/orange colour, unusual sheen, separated layers",
            "health_risks": "Sudan dye causes liver cancer. Paraffin causes gastrointestinal damage.",
            "nafdac_action": "Report to NAFDAC hotline 0800-162-3322. FCCPC evacuation powers.",
            "source": "FCCPC Sensitisation Alert June 2024",
            "reference_url": "https://fccpc.gov.ng"
        },
        {
            "id": "ground-pepper-001",
            "authority": "NAFDAC",
            "food_item": "Ground Pepper",
            "adulterant": "Brick dust, sawdust, artificial dye, mold contamination",
            "visual_signs": "Uneven colour, gritty texture, clumps, dull or overly uniform appearance",
            "health_risks": "Can trigger gastrointestinal irritation and long-term toxin exposure.",
            "nafdac_action": "Reject visibly contaminated sachets and report suspicious batches to NAFDAC.",
            "source": "Common spice adulteration guidance",
            "reference_url": "https://www.nafdac.gov.ng"
        },
        {
            "id": "frozen-fish-001",
            "authority": "WHO",
            "food_item": "Frozen Fish",
            "adulterant": "Excess ice glazing, refreezing, chemical preservatives, spoilage masking",
            "visual_signs": "Heavy ice coating, freezer burn, dull eyes, discoloured flesh, torn packaging",
            "health_risks": "Refreezing and spoilage increase foodborne illness risk.",
            "nafdac_action": "Do not buy fish with broken cold chain signs or off-smells; report unsafe storage.",
            "source": "WHO food safety guidance",
            "reference_url": "https://www.who.int/health-topics/food-safety"
        },
        {
            "id": "fresh-fruits-001",
            "authority": "NAFDAC",
            "food_item": "Fresh Fruits",
            "adulterant": "Artificial ripening agents, wax coating, pesticide residue",
            "visual_signs": "Overly uniform colour, glossy surface, uneven ripening, damaged stems",
            "health_risks": "Chemical residues can irritate the stomach and may pose longer-term toxic effects.",
            "nafdac_action": "Wash thoroughly, prefer reputable sellers, and report suspicious fruit treatment.",
            "source": "Produce safety guidance",
            "reference_url": "https://www.nafdac.gov.ng"
        },
        {
            "id": "fresh-fruits-002",
            "authority": "WHO",
            "food_item": "Fresh Fruits",
            "adulterant": "Pesticide residue and surface contamination",
            "visual_signs": "Residual sheen, dusting on the skin, damaged stems, uneven ripening",
            "health_risks": "Improper handling can increase chemical exposure and foodborne illness risk.",
            "nafdac_action": "Wash under running water, peel when appropriate, and buy from trusted sellers.",
            "source": "WHO food safety and hygiene guidance",
            "reference_url": "https://www.who.int/news-room/fact-sheets/detail/food-safety"
        },
        {
            "id": "fresh-fruits-003",
            "authority": "FDA",
            "food_item": "Fresh Fruits",
            "adulterant": "Excess waxing and post-harvest treatment masking spoilage",
            "visual_signs": "Overly glossy skin, uniform shine, bruises hidden under the surface, packaging condensation",
            "health_risks": "Masking spoilage can delay detection of unsafe produce.",
            "nafdac_action": "Inspect for bruising, avoid overly glossy produce, and prefer reputable vendors.",
            "source": "US FDA produce safety guidance",
            "reference_url": "https://www.fda.gov/food/food-safety-modernization-act-fsma"
        },
        {
            "id": "fresh-fruits-004",
            "authority": "Codex Alimentarius",
            "food_item": "Fresh Fruits",
            "adulterant": "Contaminant exposure during handling and storage",
            "visual_signs": "Mixed ripeness, stem damage, bruising, visible dirt or residue",
            "health_risks": "Poor handling can compromise quality and safety.",
            "nafdac_action": "Choose fruit with intact skins and minimal handling damage.",
            "source": "Codex general principles of food hygiene",
            "reference_url": "https://www.fao.org/fao-who-codexalimentarius"
        },
    ]

    search_client = SearchClient(SEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(SEARCH_KEY))
    search_client.upload_documents(documents=documents)
    print(f"Successfully indexed {len(documents)} adulteration patterns.")

if __name__ == "__main__":
    build()