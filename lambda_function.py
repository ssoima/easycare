import json
import requests
from aixplain.modules.agent import PipelineTool
from aixplain.factories import AgentFactory

# ------------ SENSO helper functions ------------
API_HOST_URL = "https://sdk.senso.ai/api"
# Your API key
SENSO_API_KEY = "<ADD YOUR SENSO API KEY>"
senso_headers = {
    "Content-Type": "application/json",
    "x-api-key": SENSO_API_KEY
}

def api_request(method, url, json=None):
    """Make an API request and return the response"""
    response = requests.request(method, url, headers=senso_headers, json=json)
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
    return api_request("POST", f"{API_HOST_URL}/orgs/{org_id}/categories/{category_id}/tags", json=payload)

def create_organization(name):
    """Create a new organization"""
    url = f"{API_HOST_URL}/orgs"
    payload = {"name": name}
    response = requests.post(url, headers=senso_headers, json=payload)
    response.raise_for_status()  # This will raise an exception for HTTP errors
    return response.json()

def create_document(org_id, title, content):
    """Create a new document in an organization"""
    payload = {"title": title, "content": content}
    return api_request("POST", f"{API_HOST_URL}/orgs/{org_id}/documents", json=payload)

def add_document_to_collection(org_id, collection_id, document_id):
    """Add an existing document to a specific collection"""
    return api_request("POST", f"{API_HOST_URL}/orgs/{org_id}/collections/{collection_id}/documents/{document_id}")

def create_collection(org_id, name, visibility=None):
    """Create a new collection for an organization"""
    url = f"{API_HOST_URL}/orgs/{org_id}/collections"
    payload = {"name": name}
    if visibility is not None:
        payload["visibility"] = visibility
    response = requests.post(url, headers=senso_headers, json=payload)
    response.raise_for_status()
    return response.json()


def get_organizations():
    """Get a list of all organizations you have access to"""
    url = f"{API_HOST_URL}/orgs"
    response = requests.get(url, headers=senso_headers)
    print("-"*80)
    if response.status_code == 200:
        print(response.json())
    else:
        print(response.text)
    print("-"*80)
    return response.json()

def add_document_to_collection(org_id, collection_id, document_id):
    """Add an existing document to a specific collection"""
    return api_request("POST", f"{API_HOST_URL}/orgs/{org_id}/collections/{collection_id}/documents/{document_id}")

# ------------ END SENSO helper functions ------------


def lambda_handler(event, context):
    AGENT_LLM_ID = "6646261c6eb563165658bbb1" # GPT 4o
    AIXPLAIN_PIPELINE_ID = "67156e1fc784692b8d4c54a4" #Copy this from AiXplain

    # Initialize Aixplain pipeline tool
    pipeline_tool = PipelineTool(
        pipeline=AIXPLAIN_PIPELINE_ID,
        description="This tool is used to extract patient information (name, age, pain degree, problem summary) for the doctor and to identify whether some tests should be made before the visit."
    )

    # Create agent
    agent = AgentFactory.create(
        name="Doctor assistant",
        tools=[pipeline_tool],
        description="You are an agent an agent that prepares patient information (name, age, pain degree, problem summary) for the doctor and identifies whether some tests should be made before the visit. Please structure the output using markdown. Do not make any other affirmation, output directly the requested information!",
        llm_id=AGENT_LLM_ID
    )

    # Parse event JSON
    event_body = json.loads(event["body"])

    # Extract the transcript
    transcript = event_body["call"]["transcript"]

    # Set default content for the Senso front-end in case something went wrong
    document_content = "Information extraction from the call failed"

    # Run the agent and capture the response
    try:
        agent_response = agent.run(transcript)
        print("Agent response is: ", agent_response)

        # Set document content that should be stored in the Senso front-end
        document_content = agent_response.data.get("output", document_content)

        # Extract only the required fields
        response_data = {
            "status": getattr(agent_response, "status", None),
            "completed": getattr(agent_response, "completed", None),
            "output": agent_response.data.get("output") if isinstance(agent_response.data, dict) else None
        }

        response = {
            'statusCode': 200,
            'body': json.dumps(response_data)
        }

    except Exception as e:
        print(f"Error processing request: {e}")
        response = {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)}),
            'message': 'Failed to run the Aixplain agent'
        }

    try:
        org_name = 'Aixplain Demo Org'
        collection_name = 'Patient Records'
        document_title = 'Patient Visit Notes'

        # Create an organization
        print(f"Creating organization: {org_name}...")
        org_response = create_organization(org_name)
        org_id = org_response['org_id']
        print(f"Organization created with ID: {org_id}")

        # Create a collection
        print(f"Creating collection: {collection_name}...")
        collection_response = create_collection(org_id, collection_name)
        collection_id = collection_response['collection_id']
        print(f"Collection created: {collection_id}")

        # Create a document
        print(f"Creating document: {document_title}...")
        document_response = create_document(org_id, document_title, document_content)
        document_id = document_response['document_id']
        print(f"Document created: {document_id}")

        # Add document to collection
        print("Adding document to collection...")
        add_response = add_document_to_collection(org_id, collection_id, document_id)
        print(f"Document added to collection: {add_response}")

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'organization_id': org_id,
                'collection_id': collection_id,
                'document_id': document_id,
                'status': 'success',
                'message': 'Successfully created organization, collection, and document'
            })
        }

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'status': 'error',
                'message': 'Failed to store content to Senso'
            })
        }

    return response
