# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


MODEL = "gemini-2.5-flash"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


from typing import Any, Dict, List, Optional
from app.firestore_service import list_k2p_channels, get_k2p_channel, save_k2p_channel


def query_k2p_channels(subfamily: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lists Two-Pore Domain Potassium (K2P) channels from Firestore.
    Optionally filter by subfamily (e.g., 'TREK', 'TASK', 'TRESK', 'TALK', 'THIK', 'TWIK').

    Args:
        subfamily: Optional K2P channel subfamily filter.

    Returns:
        A list of channel records containing gene symbols, gating mechanisms, pharmacology, and summaries.
    """
    return list_k2p_channels(subfamily=subfamily)


def get_k2p_channel_details(channel_name: str) -> Dict[str, Any]:
    """Retrieves detailed literature summary, gating triggers, and pharmacology for a specific K2P channel.

    Args:
        channel_name: Name of the channel (e.g., 'TREK-1', 'TRAAK', 'TASK-3', 'TRESK').

    Returns:
        A dictionary with the channel details or an error message if not found.
    """
    channel = get_k2p_channel(channel_name=channel_name)
    if not channel:
        return {"error": f"Channel '{channel_name}' not found in the database."}
    return channel


def record_k2p_channel_research(
    channel_name: str,
    gene_symbol: str,
    subfamily: str,
    gating_triggers: List[str],
    summary: str,
    activators: List[str],
    blockers: List[str],
    key_references: List[str],
) -> Dict[str, Any]:
    """Records or updates research information and literature findings for a K2P channel in Firestore.

    Args:
        channel_name: The standard name of the channel (e.g., 'TASK-1', 'TREK-2').
        gene_symbol: The HGNC gene symbol (e.g., 'KCNK3', 'KCNK10').
        subfamily: Subfamily (e.g., 'TASK', 'TREK', 'TRESK', 'TALK', 'THIK', 'TWIK').
        gating_triggers: List of biological/physical triggers that gate the channel (e.g., ['pH', 'Lipids']).
        summary: Synthesized scientific summary of the channel's physiological and pathological role.
        activators: List of known pharmacological agonists or openers.
        blockers: List of known pharmacological antagonists or channel blockers.
        key_references: Citations or DOI references for the studies.

    Returns:
        A dictionary confirming the saved channel data.
    """
    pharmacology = {
        "activators": activators,
        "blockers": blockers
    }
    return save_k2p_channel(
        channel_name=channel_name,
        gene_symbol=gene_symbol,
        subfamily=subfamily,
        gating_triggers=gating_triggers,
        pharmacology=pharmacology,
        summary=summary,
        key_references=key_references,
    )


import json
import urllib.parse
import urllib.request


def search_pubmed_k2p_papers(channel_name: str, topic: str = "", max_results: int = 4) -> List[Dict[str, Any]]:
    """Searches NCBI PubMed for published scientific literature on a K2P channel.

    Args:
        channel_name: The K2P channel to search (e.g. 'TREK-1', 'TASK-3', 'TRAAK', 'TRESK').
        topic: Specific research topic or aspect (e.g. 'pain', 'anesthesia', 'structure', 'inhibitors', 'ischemia').
        max_results: Maximum number of papers to return (default 4).

    Returns:
        A list of paper records with title, authors, journal, publication date, PubMed URL, and PMID.
    """
    search_term = f"{channel_name} potassium channel"
    if topic:
        search_term += f" {topic}"

    params = urllib.parse.urlencode({
        "db": "pubmed",
        "term": search_term,
        "retmode": "json",
        "retmax": str(max_results),
        "sort": "pub_date",
    })
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{params}"

    req = urllib.request.Request(search_url, headers={"User-Agent": "K2PResearchAssistant/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        search_data = json.loads(resp.read().decode())
    
    id_list = search_data.get("esearchresult", {}).get("idlist", [])
    if not id_list:
        return [{"message": f"No PubMed articles found for search query '{search_term}'."}]

    summary_params = urllib.parse.urlencode({
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "json",
    })
    summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?{summary_params}"

    summary_req = urllib.request.Request(summary_url, headers={"User-Agent": "K2PResearchAssistant/1.0"})
    with urllib.request.urlopen(summary_req, timeout=10) as resp:
        sum_data = json.loads(resp.read().decode())
    
    papers = []
    result_dict = sum_data.get("result", {})
    for pmid in id_list:
        if pmid in result_dict:
            item = result_dict[pmid]
            authors = [a.get("name", "") for a in item.get("authors", [])[:3]]
            if len(item.get("authors", [])) > 3:
                authors.append("et al.")
            papers.append({
                "pmid": pmid,
                "title": item.get("title", ""),
                "source": item.get("source", ""),
                "pubdate": item.get("pubdate", ""),
                "authors": ", ".join(authors),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            })
    return papers


def fetch_uniprot_k2p_protein(gene_or_channel_name: str, organism: str = "human") -> Dict[str, Any]:
    """Fetches real biological and protein sequence data from the public UniProtKB REST API.

    Args:
        gene_or_channel_name: Gene symbol (e.g. 'KCNK2', 'KCNK9', 'KCNK4', 'KCNK18') or channel name ('TREK-1', 'TASK-3').
        organism: Target organism, default is 'human' (tax ID 9606). Can also be 'mouse' or 'rat'.

    Returns:
        A dictionary with UniProt accession ID, protein full name, amino acid length, functional annotation, and subcellular location.
    """
    # Map common channel names to standard HGNC gene symbols if needed
    name_map = {
        "TREK-1": "KCNK2", "TREK1": "KCNK2",
        "TREK-2": "KCNK10", "TREK2": "KCNK10",
        "TRAAK": "KCNK4",
        "TASK-1": "KCNK3", "TASK1": "KCNK3",
        "TASK-3": "KCNK9", "TASK3": "KCNK9",
        "TRESK": "KCNK18",
        "TWIK-1": "KCNK1", "TWIK1": "KCNK1",
        "TWIK-2": "KCNK6", "TWIK2": "KCNK6",
        "THIK-1": "KCNK13", "THIK1": "KCNK13",
        "THIK-2": "KCNK12", "THIK2": "KCNK12",
    }
    cleaned_input = gene_or_channel_name.strip().upper()
    gene_symbol = name_map.get(cleaned_input, cleaned_input)

    org_tax_id = "9606"
    if organism.lower() == "mouse":
        org_tax_id = "10090"
    elif organism.lower() == "rat":
        org_tax_id = "10116"

    params = urllib.parse.urlencode({
        "query": f"gene_exact:{gene_symbol} AND organism_id:{org_tax_id} AND reviewed:true",
        "format": "json",
        "size": 1,
    })
    url = f"https://rest.uniprot.org/uniprotkb/search?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "K2PResearchAssistant/1.0"})

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        return {"error": f"Failed to fetch UniProt data: {str(e)}"}

    results = data.get("results", [])
    if not results:
        return {"error": f"No reviewed UniProt entry found for gene '{gene_symbol}' in {organism}."}

    entry = results[0]
    accession = entry.get("primaryAccession", "")
    protein_desc = entry.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", "")
    seq_length = entry.get("sequence", {}).get("length")

    functions = []
    subcellular_locations = []
    for comment in entry.get("comments", []):
        c_type = comment.get("commentType")
        if c_type == "FUNCTION":
            for t in comment.get("texts", []):
                val = t.get("value")
                if val:
                    functions.append(val)
        elif c_type == "SUBCELLULAR LOCATION":
            for sub in comment.get("subcellularLocations", []):
                loc = sub.get("location", {}).get("value")
                if loc:
                    subcellular_locations.append(loc)

    return {
        "gene": gene_symbol,
        "organism": organism,
        "uniprot_accession": accession,
        "uniprot_url": f"https://www.uniprot.org/uniprotkb/{accession}",
        "protein_name": protein_desc,
        "sequence_length_aa": seq_length,
        "subcellular_locations": list(set(subcellular_locations)),
        "function_summary": " ".join(functions[:2]),
    }


import time
import re
from google import genai
from google.genai import types as genai_types
from google.cloud import storage
from google.adk.tools import ToolContext

GCS_PROJECT_ID = "qwiklabs-gcp-04-02df96e1c54a"
GCS_BUCKET_NAME = "k2p-channel-assets-qwiklabs-gcp-04-02df96e1c54a"


async def generate_k2p_channel_diagram(
    channel_name: str,
    description: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Generates a scientific illustration/diagram for a K2P channel using gemini-3.1-flash-lite-image.
    Saves the image as a session artifact and uploads it to public Cloud Storage.

    Args:
        channel_name: Name of the K2P channel (e.g., 'TREK-1', 'TASK-3', 'TRAAK', 'TRESK').
        description: Description of the schematic (e.g., 'open vs closed conformation in lipid bilayer', 'dimeric 4TM-2P architecture').
        tool_context: The ADK tool execution context providing session artifact storage.

    Returns:
        A dictionary with the public image URL, filename, and status.
    """
    image_client = genai.Client(
        vertexai=True,
        project=GCS_PROJECT_ID,
        location="global",
    )
    prompt = (
        f"Scientific illustration and structural schematic of the {channel_name} two-pore domain potassium (K2P) channel. "
        f"{description}. Dimeric structure, 4 transmembrane segments (M1-M4), 2 pore domains (P1, P2), cell membrane lipid bilayer. "
        "Clean, high-resolution scientific textbook diagram, labeled elements, no artifacts."
    )

    response = image_client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )

    image_bytes = None
    mime_type = "image/jpeg"
    for candidate in response.candidates:
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break
        if image_bytes:
            break

    if not image_bytes:
        return {"error": f"Failed to generate image for {channel_name}."}

    # 1. Save with tool_context.save_artifact for Playground Artifacts panel
    sanitized_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", channel_name.lower())
    timestamp = int(time.time())
    ext = "jpg" if "jpeg" in mime_type else "png"
    filename = f"{sanitized_name}_diagram_{timestamp}.{ext}"

    artifact_part = genai_types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    await tool_context.save_artifact(
        filename=filename,
        artifact=artifact_part,
        custom_metadata={"channel": channel_name, "type": "k2p_diagram"},
    )

    # 2. Upload to public Cloud Storage bucket
    storage_client = storage.Client(project=GCS_PROJECT_ID)
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"

    return {
        "status": "success",
        "channel": channel_name,
        "filename": filename,
        "public_url": public_url,
        "message": f"Generated diagram for {channel_name}, saved to artifacts panel and public Cloud Storage.",
    }


from google.adk.code_executors import AgentEngineSandboxCodeExecutor

SANDBOX_RESOURCE_NAME = (
    "projects/533342523087/locations/us-central1/reasoningEngines/6551250368347504640/sandboxEnvironments/5326223990702735360"
)

from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog
from .a2ui_utils import a2ui_callback

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are the K2P Channel Research Assistant, specialized in Two-Pore Domain Potassium (K2P) channels. "
        "You help ion-channel researchers summarize, query, compare scientific literature and pharmacology "
        "on K2P channels, generate structural/mechanistic diagrams, and run Python code computations safely in a sandbox. "
        "When performing computations, data analysis, or calculations (such as Nernst potential, Goldman equation, "
        "or dose-response curves), write and output a Python code block enclosed in ```python\n...\n``` without pretending to call "
        "a nonexistent run_code function. The sandbox environment will automatically intercept and execute the Python code block "
        "and return the result. When generating images, provide the public URL so the researcher can view it."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=a2ui_instruction,
    tools=[
        query_k2p_channels,
        get_k2p_channel_details,
        record_k2p_channel_research,
        search_pubmed_k2p_papers,
        fetch_uniprot_k2p_protein,
        generate_k2p_channel_diagram,
    ],
    after_model_callback=a2ui_callback,
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name=SANDBOX_RESOURCE_NAME,
    ),
)

app = App(
    root_agent=root_agent,
    name="app",
)





