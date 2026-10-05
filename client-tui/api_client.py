import httpx
from typing import Optional, Dict, Any, List

class BabelAPIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000/api"):
        self.base_url = base_url
        self.token: Optional[str] = None

    async def login(self, username: str, password: str) -> bool:
        """Authenticates the user and stores the JWT token locally."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                return True
            return False

    def _get_auth_headers(self) -> Dict[str, str]:
        """Helper method to format the token for HTTP requests."""
        if not self.token:
            raise Exception("User is not logged in!")
        return {"Authorization": f"Bearer {self.token}"}

    async def get_problems(self) -> List[Dict[str, Any]]:
        """Fetches the list of problems from the API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/problems",
                headers=self._get_auth_headers()
            )
            response.raise_for_status()
            return response.json()

    async def submit_code(self, problem_id: int, language: str, code: str) -> Dict[str, Any]:
        """Uses the token to submit code to a protected route."""
        payload = {
            "problem_id": problem_id,
            "language": language,
            "code": code
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/submissions",
                json=payload,
                headers=self._get_auth_headers()
            )
            response.raise_for_status()
            return response.json()
