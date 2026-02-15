import json
from typing import List, Dict, Any
from ollama import AsyncClient
from app.config import settings
import os
import asyncio
import httpx
from app.services.spec_parser import EndpointInfo


class JourneyGenerator:
    """AI-powered journey generator using Ollama."""

    def __init__(self):
        """Initialize Ollama client."""
        self.client = AsyncClient(
            host="https://ollama.com",
            headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')} if os.environ.get('OLLAMA_API_KEY') else None
        )
        self.model = settings.OLLAMA_MODEL
        self.timeout = 120.0

    async def generate_journeys(
        self, endpoints: List[EndpointInfo]
    ) -> List[Dict[str, Any]]:
        """Generate logical user journeys from API endpoints using AI.
        
        Args:
            endpoints: List of parsed endpoint information
            
        Returns:
            List of journey dictionaries with nodes and edges in VueFlow format
        """
        endpoint_summary = self._format_endpoints(endpoints)

        prompt = f"""You are an API testing expert. Given these API endpoints and their schemas, identify 3-5 logical user journeys.

Endpoints:
{endpoint_summary}

For each journey, return JSON with:
- name: Short descriptive name
- description: what this journey tests
- steps: Array of {{
    operationId: string,
    name: string,
    data_mappings: [{{ 
        from: "response.field_path", 
        to: "session_key",
        description: "why we map this"
    }}]
  }}

Mapping Rules:
1. AUTH: If an endpoint provides a token (e.g., login/register), map it to 'auth_token'. 
2. PATH PARAMS: If a subsequent endpoint has a path like '/users/{{id}}', ensure you map the ID from a previous 'create' or 'list' response to 'pathParams.id'.
3. DATA FLOW: Map IDs, UUIDs, or primary keys from 'create' responses to use in 'get', 'update', or 'delete' steps.
4. NAMING: In 'to', use 'auth_token' for bearers, 'pathParams.{{name}}' for URL vars, or any descriptive key for body interpolation.

Journey Logic:
- Start with Auth if endpoints require it (see 'security' field).
- Follow a CRUD pattern where possible (Create -> Get/Update -> Delete).
- Include "Success" flows and "Business Logic" flows (e.g., Add to Cart -> Checkout).

Return ONLY a JSON array, no explanation.
"""

        # Call Ollama API
        print("Calling Ollama API...")
        response = await self.client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            format="json",
        )
        print("Response:", response)
        print('Done calling Ollama API')

        # Parse response
        try:
            journeys_text = response["message"]["content"]
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in journeys_text:
                journeys_text = journeys_text.split("```json")[1].split("```")[0]
            elif "```" in journeys_text:
                journeys_text = journeys_text.split("```")[1].split("```")[0]
            
            journeys = json.loads(journeys_text.strip())
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            # Fallback to basic journey if AI fails
            print(f"AI journey generation failed: {e}")
            journeys = self._create_fallback_journey(endpoints)

        # Convert to VueFlow format
        return self._convert_to_vueflow_format(journeys, endpoints)
    
    def _format_endpoints(self, endpoints: List[EndpointInfo]) -> str:
        """Format endpoints for AI prompt with schema details.
        
        Args:
            endpoints: List of endpoint information
            
        Returns:
            Formatted string of endpoints with full context
        """
        summary_items = []
        for e in endpoints:
            # Create a cleaned version to save tokens while keeping schema structure
            item = {
                "method": e.method,
                "path": e.path,
                "operationId": e.operation_id,
                "summary": e.summary,
                "security": e.security,
                "requestBody": self._clean_schema(e.request_body),
                "responses": {code: self._clean_schema(res) for code, res in e.responses.items()},
                "parameters": [self._clean_schema(p) for p in e.parameters]
            }
            summary_items.append(json.dumps(item))
            
        return "\n---\n".join(summary_items)

    def _clean_schema(self, schema: Any) -> Any:
        """Recursively remove descriptions and examples to save tokens."""
        if isinstance(schema, dict):
            return {
                k: self._clean_schema(v) 
                for k, v in schema.items() 
                if k not in ["description", "example", "examples", "x-enumNames"]
            }
        elif isinstance(schema, list):
            return [self._clean_schema(i) for i in schema]
        return schema

    def _create_fallback_journey(
        self, endpoints: List[EndpointInfo]
    ) -> List[Dict[str, Any]]:
        """Create a basic fallback journey if AI fails.
        
        Args:
            endpoints: List of endpoint information
            
        Returns:
            Basic journey structure
        """
        return [
            {
                "name": "Basic API Flow",
                "description": "Auto-generated basic flow",
                "steps": [
                    {
                        "operationId": e.operation_id,
                        "name": e.summary or e.operation_id,
                        "data_mappings": [],
                    }
                    for e in endpoints[:5]  # Limit to first 5
                ],
            }
        ]

    def _convert_to_vueflow_format(
        self, journeys: List[Dict[str, Any]], endpoints: List[EndpointInfo]
    ) -> List[Dict[str, Any]]:
        """Convert AI-generated journeys to VueFlow node/edge format.
        
        Args:
            journeys: AI-generated journey structures
            endpoints: List of all available endpoints
            
        Returns:
            List of journeys with VueFlow-compatible nodes and edges
        """
        result = []

        for journey in journeys:
            nodes = []
            edges = []

            steps = journey.get("steps", [])
            for idx, step in enumerate(steps):
                # Find matching endpoint
                endpoint = next(
                    (
                        e
                        for e in endpoints
                        if e.operation_id == step.get("operationId")
                    ),
                    None,
                )

                if not endpoint:
                    continue

                # Create VueFlow node
                nodes.append(
                    {
                        "id": f"step-{idx}",
                        "type": "endpoint",
                        "position": {"x": 100, "y": idx * 150},
                        "data": {
                            "method": endpoint.method,
                            "path": endpoint.path,
                            "operationId": endpoint.operation_id,
                            "summary": endpoint.summary,
                            "requestBody": {}, # This will hold the actual data/mock
                            "request_body": endpoint.request_body, # Helper for consistency with Manual nodes
                            "requestBodySpec": endpoint.request_body, # This holds the OpenAPI spec
                            "responses": endpoint.responses,
                            "parameters": endpoint.parameters,
                            "status": "pending",
                        },
                    }
                )

                # Create edge to previous step
                if idx > 0:
                    data_mappings = step.get("data_mappings", [])
                    edge_label = ""
                    
                    if data_mappings and len(data_mappings) > 0:
                        mapping = data_mappings[0]
                        edge_label = f"{mapping.get('from', '')} → {mapping.get('to', '')}"

                    # Accumulate all mappings into edge data
                    all_mappings = []
                    for sm in data_mappings:
                        all_mappings.append({
                            "from": sm.get("from", ""),
                            "to": sm.get("to", "")
                        })

                    edges.append(
                        {
                            "id": f"e{idx-1}-{idx}",
                            "source": f"step-{idx-1}",
                            "target": f"step-{idx}",
                            "type": "mapping",
                            "label": edge_label,
                            "animated": True,
                            "data": {"dataMapping": all_mappings},
                        }
                    )

            result.append(
                {
                    "name": journey.get("name", "Unnamed Journey"),
                    "description": journey.get("description", ""),
                    "nodes": nodes,
                    "edges": edges,
                }
            )

        return result
