import json
from typing import List, Dict, Any
from ollama import Client

from app.config import settings
from app.services.spec_parser import EndpointInfo


class JourneyGenerator:
    """AI-powered journey generator using Ollama."""

    def __init__(self):
        """Initialize Ollama client."""
        self.client = Client(host=settings.OLLAMA_HOST)
        self.model = settings.OLLAMA_MODEL

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

        prompt = f"""You are an API testing expert. Given these API endpoints, identify 3-5 logical user journeys.

Endpoints:
{endpoint_summary}

For each journey, return JSON with:
- name: Short descriptive name
- description: What this journey tests
- steps: Array of {{
    operationId: string,
    name: string,
    data_mappings: [{{ from: "response.field", to: "request.field" }}]
  }}

Rules:
1. Auth endpoints (login/register) should be first steps
2. Map data between steps (e.g., login token → auth header)
3. Follow logical workflows (e.g., create resource → update → delete)
4. Include error testing journeys (e.g., "Test unauthorized access")

Return ONLY a JSON array, no explanation.
"""

        # Call Ollama API
        response = self.client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )

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
        """Format endpoints for AI prompt.
        
        Args:
            endpoints: List of endpoint information
            
        Returns:
            Formatted string of endpoints
        """
        return "\n".join(
            [
                f"{e.method} {e.path} - {e.operation_id} ({e.summary})"
                for e in endpoints
            ]
        )

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
                            "requestBody": endpoint.request_body,
                            "responses": endpoint.responses,
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

                    edges.append(
                        {
                            "id": f"e{idx-1}-{idx}",
                            "source": f"step-{idx-1}",
                            "target": f"step-{idx}",
                            "label": edge_label,
                            "data": {"dataMapping": data_mappings},
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
