import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime
import re


class JourneyExecutor:
    """Executes API journey tests."""

    def __init__(self, base_url: str):
        """Initialize executor with target API base URL.
        
        Args:
            base_url: Base URL of the API to test
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def execute_journey(
        self,
        journey: Dict[str, Any],
        session_data: Dict[str, Any] = None,
        error_injections: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """Execute all steps in a journey sequentially.
        
        Args:
            journey: Journey object with nodes and edges
            session_data: Initial session data (auth tokens, etc.)
            error_injections: Dictionary of step_id -> error configuration
            
        Returns:
            List of step execution results
        """
        if session_data is None:
            session_data = {}
        if error_injections is None:
            error_injections = {}

        results = []
        nodes = journey.get("nodes", [])
        edges = journey.get("edges", [])

        for node in nodes:
            step_id = node["id"]

            # Check for error injection
            if step_id in error_injections:
                result = self._inject_error(node, error_injections[step_id])
            else:
                result = await self._execute_step(node, session_data)

            results.append(result)

            # Update session data for next steps
            self._update_session_data(session_data, result, edges)

            # Stop if step failed and continueOnError is false
            status_code = result.get("statusCode", 0)
            continue_on_error = node.get("data", {}).get("continueOnError", False)
            
            if status_code >= 400 and not continue_on_error:
                break

        return results

    async def _execute_step(
        self, node: Dict[str, Any], session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single API call step.
        
        Args:
            node: VueFlow node with endpoint data
            session_data: Current session state
            
        Returns:
            Step execution result with status, response, timing
        """
        data = node.get("data", {})
        step_id = node["id"]

        # Build URL
        url = self.base_url + data.get("path", "")
        url = self._interpolate_path_params(url, session_data)

        # Build headers
        headers = self._build_headers(data, session_data)

        # Build request body
        body = self._build_body(data, session_data)

        # Execute request
        method = data.get("method", "GET")
        
        try:
            start_time = datetime.utcnow()

            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                json=body if method in ["POST", "PUT", "PATCH"] and body else None,
            )

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Try to parse JSON response
            try:
                response_body = response.json()
            except Exception:
                response_body = response.text

            return {
                "stepId": step_id,
                "statusCode": response.status_code,
                "responseBody": response_body,
                "headers": dict(response.headers),
                "duration": duration,
                "timestamp": datetime.utcnow().isoformat(),
                "request": {
                    "method": method,
                    "url": url,
                    "headers": headers,
                    "body": body,
                },
            }

        except Exception as e:
            return {
                "stepId": step_id,
                "statusCode": 0,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "request": {
                    "method": method,
                    "url": url,
                    "headers": headers,
                    "body": body,
                },
            }

    def _update_session_data(
        self,
        session_data: Dict[str, Any],
        result: Dict[str, Any],
        edges: List[Dict[str, Any]],
    ):
        """Extract data from response and update session for next steps.
        
        Args:
            session_data: Session dictionary to update
            result: Step execution result
            edges: Journey edges with data mappings
        """
        if not result.get("responseBody"):
            return

        step_id = result["stepId"]

        # Find edges originating from this step
        relevant_edges = [e for e in edges if e.get("source") == step_id]

        for edge in relevant_edges:
            mappings = edge.get("data", {}).get("dataMapping", [])

            for mapping in mappings:
                if not isinstance(mapping, dict):
                    continue
                    
                # Extract value from response
                from_path = mapping.get("from", "").replace("response.", "")
                value = self._get_nested_value(result["responseBody"], from_path)

                if value is not None:
                    # Store for use in next step
                    to_path = mapping.get("to", "")
                    session_data[to_path] = value

    def _interpolate_path_params(
        self, url: str, session_data: Dict[str, Any]
    ) -> str:
        """Replace {param} in URL with values from session_data.
        
        Args:
            url: URL with parameter placeholders
            session_data: Session data with parameter values
            
        Returns:
            URL with interpolated parameters
        """
        def replacer(match):
            param_name = match.group(1)
            key = f"pathParams.{param_name}"
            return str(session_data.get(key, match.group(0)))

        return re.sub(r"\{(\w+)\}", replacer, url)

    def _build_headers(
        self, step_data: Dict[str, Any], session_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Build request headers, including auth from session.
        
        Args:
            step_data: Step configuration
            session_data: Current session state
            
        Returns:
            Headers dictionary
        """
        headers = {"Content-Type": "application/json"}

        # Add authorization if token exists in session
        auth_header = session_data.get("headers.Authorization")
        if auth_header:
            headers["Authorization"] = auth_header
        elif "auth_token" in session_data:
            headers["Authorization"] = f"Bearer {session_data['auth_token']}"

        return headers

    def _build_body(
        self, step_data: Dict[str, Any], session_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Build request body, interpolating values from session.
        
        Args:
            step_data: Step configuration
            session_data: Current session state
            
        Returns:
            Request body dictionary or None
        """
        request_body = step_data.get("requestBody")
        if not request_body:
            return None

        # If body template exists, interpolate with session data
        return self._interpolate_dict(request_body, session_data)

    def _get_nested_value(self, obj: Any, path: str) -> Any:
        """Get nested value from dict using dot notation.
        
        Args:
            obj: Dictionary to extract from
            path: Dot-notation path (e.g., 'user.id')
            
        Returns:
            Extracted value or None
        """
        if not path:
            return obj
            
        keys = path.split(".")
        value = obj

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list) and key.isdigit():
                try:
                    value = value[int(key)]
                except (IndexError, ValueError):
                    return None
            else:
                return None

        return value

    def _interpolate_dict(
        self, template: Any, session_data: Dict[str, Any]
    ) -> Any:
        """Recursively interpolate session values in a dict/list structure.
        
        Args:
            template: Template structure with {{placeholders}}
            session_data: Session data for interpolation
            
        Returns:
            Interpolated structure
        """
        if isinstance(template, dict):
            return {
                k: self._interpolate_dict(v, session_data)
                for k, v in template.items()
            }
        elif isinstance(template, list):
            return [self._interpolate_dict(item, session_data) for item in template]
        elif isinstance(template, str):
            # Replace {{sessionKey}} with session value
            def replacer(match):
                key = match.group(1)
                return str(session_data.get(key, match.group(0)))
            
            return re.sub(r"\{\{(\S+)\}\}", replacer, template)
        else:
            return template

    def _inject_error(
        self, node: Dict[str, Any], error_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Inject a simulated error for testing.
        
        Args:
            node: Node to inject error for
            error_config: Error configuration
            
        Returns:
            Simulated error result
        """
        error_type = error_config.get("type", "status")
        step_id = node["id"]

        if error_type == "timeout":
            return {
                "stepId": step_id,
                "statusCode": 0,
                "error": "Request timeout (injected)",
                "timestamp": datetime.utcnow().isoformat(),
            }
        elif error_type == "status":
            status_code = error_config.get("statusCode", 500)
            return {
                "stepId": step_id,
                "statusCode": status_code,
                "responseBody": {"error": "Injected error"},
                "headers": {},
                "duration": 0,
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            return {
                "stepId": step_id,
                "statusCode": 500,
                "error": "Unknown error injection type",
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
