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
        # print(data)
        step_id = node["id"]

        # Build URL
        url = self.base_url + data.get("path", "")
        url = self._interpolate_path_params(url, session_data)

        # Build headers
        headers = self._build_headers(data, session_data)

        # Build request body
        body = self._build_body(data, session_data)
        # print(body)

        # Execute request
        method = data.get("method", "GET")
        # print(method)
        
        try:
            start_time = datetime.utcnow()

            # Determine how to send the body
            req_kwargs = {}
            if method in ["POST", "PUT", "PATCH"] and body:
                content_spec = data.get("requestBodySpec", data.get("requestBody", {})).get("content", {})
                if "multipart/form-data" in content_spec:
                    # Handle binary fields (uploads)
                    schema = content_spec["multipart/form-data"].get("schema", {})
                    properties = schema.get("properties", {}) or {}
                    
                    files = {}
                    form_data = {}
                    
                    # Iterate through body fields to separate files and regular data
                    for field_name, value in body.items():
                        prop = properties.get(field_name, {})
                        if prop.get("format") == "binary" and isinstance(value, str) and value.startswith("http"):
                            try:
                                # Fetch the actual binary content from the URL
                                img_resp = await self.client.get(value)
                                if img_resp.status_code == 200:
                                    ext = "jpg"
                                    if "png" in value.lower(): ext = "png"
                                    elif "webp" in value.lower(): ext = "webp"
                                    
                                    # Create a file tuple for httpx: (filename, content, content-type)
                                    files[field_name] = (
                                        f"upload.{ext}", 
                                        img_resp.content, 
                                        img_resp.headers.get("Content-Type", "image/jpeg")
                                    )
                                else:
                                    form_data[field_name] = value
                            except Exception:
                                form_data[field_name] = value
                        else:
                            form_data[field_name] = value

                    if files:
                        req_kwargs["data"] = form_data
                        req_kwargs["files"] = files
                        # Remove default JSON content-type to let httpx set boundary
                        if "Content-Type" in headers:
                            del headers["Content-Type"]
                    else:
                        req_kwargs["data"] = body
                elif "application/x-www-form-urlencoded" in content_spec:
                    req_kwargs["data"] = body
                else:
                    req_kwargs["json"] = body

            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                **req_kwargs
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

        # SMART EXTRACTION: Automatically look for tokens/IDs if they aren't explicitly mapped
        response_body = result.get("responseBody")
        if isinstance(response_body, dict):
            # 1. Look for Auth Tokens
            token_keys = ["access", "token", "jwt", "access_token", "authToken", "id_token"]
            
            # Check top level
            found_token = None
            for tk in token_keys:
                if tk in response_body and isinstance(response_body[tk], str):
                    found_token = response_body[tk]
                    break
            
            # Check nested "tokens" object (common logic for many APIs)
            if not found_token and "tokens" in response_body and isinstance(response_body["tokens"], dict):
                for tk in token_keys:
                    if tk in response_body["tokens"] and isinstance(response_body["tokens"][tk], str):
                        found_token = response_body["tokens"][tk]
                        break
            
            if found_token and "auth_token" not in session_data:
                session_data["auth_token"] = found_token

            # 2. Look for IDs to pass forward
            id_keys = ["id", "uuid", "pk", "restaurant_id", "order_id", "user_id"]
            
            def extract_ids(obj):
                if not isinstance(obj, dict):
                    return
                for k, v in obj.items():
                    if k in id_keys and (isinstance(v, str) or isinstance(v, int)):
                        session_data[k] = v
                        if f"pathParams.{k}" not in session_data:
                            session_data[f"pathParams.{k}"] = v
                    # Check one level deeper if it's 'detail' or 'data'
                    if k in ["detail", "data"] and isinstance(v, dict):
                        extract_ids(v)

            extract_ids(response_body)

        # Scan headers if auth_token still not found
        if "auth_token" not in session_data:
            resp_headers = result.get("headers", {})
            auth_header = resp_headers.get("Authorization") or resp_headers.get("authorization")
            if auth_header:
                session_data["auth_token"] = auth_header

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
            # Try specific pathParams key first, then fallback to direct key
            value = session_data.get(f"pathParams.{param_name}")
            if value is None:
                value = session_data.get(param_name)
                
            return str(value) if value is not None else match.group(0)

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
        # Determine Content-Type from spec
        content_spec = step_data.get("requestBodySpec", step_data.get("requestBody", {})).get("content", {})
        
        content_type = "application/json"
        if "application/x-www-form-urlencoded" in content_spec:
            content_type = "application/x-www-form-urlencoded"
        elif "multipart/form-data" in content_spec:
            # Note: For multipart with files, we'll actually delete this header later 
            # to let httpx set the boundary automatically
            content_type = "multipart/form-data"

        headers = {"Content-Type": content_type}

        # Add authorization if token exists in session
        auth_header = session_data.get("headers.Authorization")
        if auth_header:
            headers["Authorization"] = auth_header
        else:
            # Check various common token keys
            token = session_data.get("auth_token") or session_data.get("token") or session_data.get("access")
            if token:
                if not str(token).startswith(("Bearer", "Token", "JWT")):
                    headers["Authorization"] = f"Bearer {token}"
                else:
                    headers["Authorization"] = str(token)

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
            # Check if the entire string is exactly a placeholder like "{{key}}"
            # to preserve the original data type (e.g., int, bool, object)
            match = re.fullmatch(r"\{\{(\S+)\}\}", template)
            if match:
                key = match.group(1)
                return session_data.get(key, template)

            # Otherwise do string interpolation for partial matches
            def replacer(match):
                key = match.group(1)
                value = session_data.get(key, match.group(0))
                return str(value)
            
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
