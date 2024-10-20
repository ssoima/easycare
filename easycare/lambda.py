import json
import requests
import json
import os
from aixplain.modules.agent import PipelineTool
from aixplain.factories import AgentFactory


# Base URL for the API
BASE_URL = "https://sdk.senso.ai/api"

# Your API key
API_KEY = "ZD6TXdlfl168Qq4ChQiWk4Op2oywzgCv9MbDBzHj"

headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

def api_request(method, url, json=None):
    """Make an API request and return the response"""
    response = requests.request(method, url, headers=headers, json=json)
    print(f"API Request: {method} {url}")
    print(f"Response Status: {response.status_code}")
    print(f"Response Content: {response.text}\n")
    response.raise_for_status()
    return response.json()

def create_tag(org_id, category_id, name, description=None):
    """Create a new tag for a specific category in an organization"""
    payload = {"name": name}
    if description:
        payload["description"] = description
    return api_request("POST", f"{BASE_URL}/orgs/{org_id}/categories/{category_id}/tags", json=payload)

def create_organization(name):
    """Create a new organization"""
    url = f"{BASE_URL}/orgs"
    payload = {"name": name}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()

def create_document(org_id, title, content):
    """Create a new document in an organization"""
    payload = {"title": title, "content": content}
    return api_request("POST", f"{BASE_URL}/orgs/{org_id}/documents", json=payload)

def add_document_to_collection(org_id, collection_id, document_id):
    """Add an existing document to a specific collection"""
    return api_request("POST", f"{BASE_URL}/orgs/{org_id}/collections/{collection_id}/documents/{document_id}")

def create_collection(org_id, name, visibility=None):
    """Create a new collection for an organization"""
    url = f"{BASE_URL}/orgs/{org_id}/collections"
    payload = {"name": name}
    if visibility is not None:
        payload["visibility"] = visibility
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def get_organizations():
    """Get a list of all organizations you have access to"""
    url = f"{BASE_URL}/orgs"
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()

def add_document_to_collection(org_id, collection_id, document_id):
    """Add an existing document to a specific collection"""
    return api_request("POST", f"{BASE_URL}/orgs/{org_id}/collections/{collection_id}/documents/{document_id}")

def lambda_handler(event, context):
    # Log the event for debugging purposes
    print("Received event: ", json.dumps(event, indent=2))
    os.environ["TEAM_API_KEY"] = "b2390515d67dd611d3a7d87867c713f2cfcd9022b158d81fe825aee52a7d458d"

    pipeline_tool = PipelineTool(
        pipeline="67156e1fc784692b8d4c54a4",
        description="this pipeline identifies whether a blood test should be taken"
    )

    agent = AgentFactory.create(
        name="Doctor assistant",
        tools=[
            pipeline_tool
        ],
        description="This is an agent that prepares patient information for the doctor",
        # required llm_id
        llm_id="6646261c6eb563165658bbb1" # GPT 4o
    )

    agent_response1 =agent.run(event)
    print(agent_response1)

    org_name = 'EasyCare'
    # Create a new organization
    org_response = create_organization(org_name)
    orgs = get_organizations()
    org_id = 'b34ce1c1-a10d-451b-931b-359810641966'
    collection = create_collection(org_id, 'Michi Muster', None)
    document = create_document(org_id, "Michi Phone Call", agent_response1)
    document_id = document['document_id']
    print(f"\nDocument created successfully. Document ID: {document_id}")

    collection_id = collection['collection_id']
    result = add_document_to_collection(org_id, collection_id, document_id)

    # Create a response
    response = {
        'statusCode': 200,
    }

    return response