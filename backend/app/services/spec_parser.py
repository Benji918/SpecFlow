import prance
from typing import Dict, List, Optional
from pydantic import BaseModel


class EndpointInfo(BaseModel):
    path: str
    method: str
    operation_id: str
    summary: str
    description: str
    parameters: List[Dict]
    request_body: Optional[Dict] = None
    responses: Dict
    security: List[Dict]
    tags: List[str]


class SpecParser:
    """Parser for OpenAPI specifications."""

    def __init__(self, spec_content: Dict):
        """Initialize parser with OpenAPI spec content.
        
        Args:
            spec_content: Dictionary containing the OpenAPI specification
        """
        # Resolve all $ref pointers
        import json
        parser = prance.ResolvingParser(
            spec_string=json.dumps(spec_content),
            backend='openapi-spec-validator',
            strict=False,
            validate=False  #skip validation
        )
        self.spec = parser.specification

    def extract_endpoints(self) -> List[EndpointInfo]:
        """Extract all endpoints from the OpenAPI spec.
        
        Returns:
            List of EndpointInfo objects containing endpoint details
        """
        endpoints = []

        paths = self.spec.get("paths", {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() in ["get", "post", "put", "patch", "delete"]:
                    endpoints.append(
                        EndpointInfo(
                            path=path,
                            method=method.upper(),
                            operation_id=details.get(
                                "operationId", f"{method}_{path.replace('/', '_')}"
                            ),
                            summary=details.get("summary", ""),
                            description=details.get("description", ""),
                            parameters=details.get("parameters", []),
                            request_body=details.get("requestBody"),
                            responses=details.get("responses", {}),
                            security=details.get("security", []),
                            tags=details.get("tags", []),
                        )
                    )

        return endpoints

    def get_schemas(self) -> Dict:
        """Extract component schemas from the spec.
        
        Returns:
            Dictionary of schema definitions
        """
        return self.spec.get("components", {}).get("schemas", {})

    def get_security_schemes(self) -> Dict:
        """Extract security schemes from the spec.
        
        Returns:
            Dictionary of security scheme definitions
        """
        return self.spec.get("components", {}).get("securitySchemes", {})

    def get_version(self) -> str:
        """Get the OpenAPI version.
        
        Returns:
            OpenAPI version string
        """
        return self.spec.get("info", {}).get("version", "1.0.0")

    def get_title(self) -> str:
        """Get the API title.
        
        Returns:
            API title string
        """
        return self.spec.get("info", {}).get("title", "API")
