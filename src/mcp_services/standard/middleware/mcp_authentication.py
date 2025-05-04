import json
import logging

import jwt
from starlette.authentication import AuthenticationError
from starlette.datastructures import MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

log = logging.getLogger(__name__)

COGNITO_USER_POOL_ID = "eu-west-1_vi9honYY0"
COGNITO_REGION = "eu-west-1"
JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"


class McpAuthentication(BaseHTTPMiddleware):
    """Middleware to authenticate all requests to the MCP server."""

    @staticmethod
    def _process_bearer_token(token: str) -> str:
        """Parse the bearer token.

        Args:
            token (str): The token from the request header.

        Return:
            str: The extracted token.

        Raises:
            AuthenticationError: If the token format is invalid or missing.
        """
        try:
            scheme, token = token.split()
        except ValueError as e:
            raise AuthenticationError("Invalid token format") from e
        if scheme.lower() != "bearer":
            raise AuthenticationError(f"Invalid token scheme: {scheme}")
        if not token:
            raise AuthenticationError("Missing token")
        return token

    @staticmethod
    def _validate_token(token: str) -> dict:
        """Validate the token using public keys.

        Args:
            token (str): The token to validate.

        Returns:
            dict: The decoded token if valid.

        Raises:
            AuthenticationError: If the token is expired, invalid, or cannot be decoded.
        """
        try:
            jwk_client = jwt.PyJWKClient(JWKS_URL)
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            decoded_token = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
            )
        except jwt.ExpiredSignatureError as e:
            raise AuthenticationError("Token has expired") from e
        except jwt.DecodeError as e:
            raise AuthenticationError("Token decode error") from e
        except Exception as e:
            raise AuthenticationError("Token validation failed") from e
        return decoded_token

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Could you change the main body here to add meta data? For scopes etc.
        if "Authorization" not in request.headers:
            response = Response(status_code=401)
            return response
        try:
            bearer_token = request.headers["Authorization"]
            token = self._process_bearer_token(bearer_token)
            validated_token = self._validate_token(token)
        except AuthenticationError as e:
            response = Response(status_code=403)
            log.error(e)
            return response

        original_body = await request.body()
        log.debug(f"Original body: {original_body}")
        try:
            body_data = json.loads(original_body)
            if "params" in body_data.keys():
                body_data["params"] = body_data["params"] | validated_token
            modified_body = json.dumps(body_data).encode("utf-8")

            async def changed_receive() -> dict:
                return {
                    "type": "http.request",
                    "body": modified_body,
                    "more_body": False,
                }

            modified_request = Request(request.scope, changed_receive, request._send)

            headers = MutableHeaders(request.headers)
            headers["content-length"] = str(len(modified_body))
            modified_request._headers = headers

            log.debug(f"Modified body: {await modified_request.body()}")
        except json.JSONDecodeError:
            log.error("Invalid JSON body")
            modified_request = request
            # return Response(status_code=400, content="Invalid JSON body")
        return await call_next(modified_request)
