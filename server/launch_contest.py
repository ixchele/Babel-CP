import asyncio
import httpx

API_URL = "http://127.0.0.1:8000/api"

async def launch_contest(username: str, password: str, duration: int):
    async with httpx.AsyncClient() as client:
        auth_res = await client.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password}
        )
        
        if auth_res.status_code != 200:
            print("󰚌 Authentication failed")
            return
            
        token = auth_res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        start_res = await client.post(
            f"{API_URL}/contest/start?duration_minutes={duration}",
            headers=headers
        )
        
        if start_res.status_code == 200:
            print("󰔛 Contest successfully started for all active nodes.")
        else:
            print(f"󰚌 Server rejected the request: {start_res.status_code}")

if __name__ == "__main__":
    asyncio.run(launch_contest("ixchele", "123456",120))
