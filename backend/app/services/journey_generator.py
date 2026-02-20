import json
from typing import List, Dict, Any
from ollama import AsyncClient
from app.config import settings
from fastapi import WebSocket
import os
import asyncio
import httpx
from datetime import datetime
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
        self.timeout = 300.0  # 5 minutes timeout for Ollama

    async def generate_journeys(
        self, endpoints: List[EndpointInfo], websocket: WebSocket
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

IMPORTANT: Every journey MUST start with an authentication endpoint (EITHER LOGIN OR REGISTER). This is a strict requirement. If no login/register endpoint exists in the endpoints list, you MUST NOT generate any journeys.

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

CRITICAL REQUIREMENT:
- The FIRST step in EVERY journey MUST be a login or register endpoint (e.g., /auth/login, /auth/register, /users/register, /token, etc.)
- Identify login/register endpoints by looking for paths containing: login, signin, register, signup, token, auth, authenticate, session
- If no authentication endpoint exists in the provided endpoints, return an EMPTY array - do not generate any journeys

Mapping Rules:
1. AUTH: If an endpoint provides a token (e.g., login/register), map it to 'auth_token'. 
2. PATH PARAMS: If a subsequent endpoint has a path like '/users/{{id}}', ensure you map the ID from a previous 'create' or 'list' response to 'pathParams.id'.
3. DATA FLOW: Map IDs, UUIDs, or primary keys from 'create' responses to use in 'get', 'update', or 'delete' steps.
4. NAMING: In 'to', use 'auth_token' for bearers, 'pathParams.{{name}}' for URL vars, or any descriptive key for body interpolation.

Journey Logic:
- MUST start with Auth (login/register) endpoint - this is required!
- Follow a CRUD pattern where possible (Create -> Get/Update -> Delete).
- Include "Success" flows and "Business Logic" flows (e.g., Add to Cart -> Checkout).

Return ONLY a JSON array, no explanation.
"""

        try:
            await self._send_progress(websocket, 5, "Initializing AI journey generator...")
            await asyncio.sleep(0.1)  # Small delay to ensure message is sent
            await self._send_progress(websocket, 10, "Parsing API endpoints from specification...")
            await asyncio.sleep(0.1)
            
            endpoint_summary = self._format_endpoints(endpoints)
            
            await self._send_progress(websocket, 20, f"Analyzing {len(endpoints)} endpoints for user journeys...")
            await asyncio.sleep(0.1)
            await self._send_progress(websocket, 30, "Sending request to AI model...")
            await asyncio.sleep(0.1)
            
            try:
                response = await asyncio.wait_for(
                    self.client.chat(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        format="json",
                    ),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                await self._send_progress(websocket, 0, "AI request timed out")
                raise Exception(f"Timeout after {self.timeout}s - Ollama took too long to respond")
            
            await self._send_progress(websocket, 50, "Received response from AI model, parsing results...")
            await asyncio.sleep(0.1)
            await self._send_progress(websocket, 60, "Processing journey data...")
            
            await self._send_progress(websocket, 70, "Analyzing AI response and extracting journey steps...")
            await asyncio.sleep(0.1)

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
            await self._send_progress(websocket, 85, "Building journey nodes and connections...")
            await asyncio.sleep(0.1)
            result = self._convert_to_vueflow_format(journeys, endpoints)
            await self._send_progress(websocket, 95, "Finalizing journeys...")
            await asyncio.sleep(0.1)
            await self._send_progress(websocket, 100, "Journey generation complete!")
            return result
    
        except Exception as e:
            await self._send_progress(websocket, 0, f"Error: {str(e)}")
            raise
    
    async def _send_progress(self, websocket: WebSocket, progress: int, message: str):
        """Send progress via WebSocket if available."""
        if websocket:
            try:
                await websocket.send_json({
                    "type": "progress",
                    "progress": progress,
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except:
                pass
    
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
        # Find auth/login/register endpoints first
        auth_keywords = ['login', 'signin', 'register', 'signup', 'token', 'auth', 'authenticate', 'session']
        auth_endpoints = [e for e in endpoints if any(k in e.path.lower() or k in (e.summary or '').lower() for k in auth_keywords)]
        
        if auth_endpoints:
            # Use auth endpoint as first step
            steps = [auth_endpoints[0]]
            # Add some other endpoints if available
            non_auth = [e for e in endpoints if e not in auth_endpoints][:4]
            steps.extend(non_auth)
        else:
            # No auth endpoint, use first few endpoints
            steps = endpoints[:5] if len(endpoints) >= 5 else endpoints
        
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
                    for e in steps
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
