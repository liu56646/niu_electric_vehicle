"""
API client for Niu Electric Vehicle integration.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

class NiuApiClientError(HomeAssistantError):
    """Error to indicate something went wrong with the API client."""

class NiuApiClient:
    """Niu API Client."""

    def __init__(
        self, username: str, password: str, vehicle_id: str, session: aiohttp.ClientSession
    ):
        """Initialize the API client."""
        self.username = username
        self.password = password
        self.vehicle_id = vehicle_id
        self.session = session
        self.base_url = "https://api-factory.niu.com"
        self.access_token: str | None = None

    async def async_authenticate(self) -> None:
        """Authenticate with the API."""
        url = f"{self.base_url}/v1/oauth2/token"
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }

        try:
            async with self.session.post(url, data=data) as response:
                if response.status != 200:
                    _LOGGER.error("Authentication failed with status: %s", response.status)
                    raise NiuApiClientError("Authentication failed")
                result = await response.json()
                self.access_token = result.get("access_token")
                if not self.access_token:
                    _LOGGER.error("No access token in response")
                    raise NiuApiClientError("No access token received")
        except aiohttp.ClientError as error:
            _LOGGER.error("Error during authentication: %s", error)
            raise NiuApiClientError(f"Network error: {error}") from error

    async def async_get_vehicle_data(self) -> dict[str, Any]:
        """Get vehicle data from the API."""
        if not self.access_token:
            await self.async_authenticate()

        url = f"{self.base_url}/v3/vehicle/{self.vehicle_id}/status"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 401:
                    # Token expired, reauthenticate
                    _LOGGER.info("Token expired, reauthenticating")
                    await self.async_authenticate()
                    # Try again with new token
                    headers["Authorization"] = f"Bearer {self.access_token}"
                    async with self.session.get(url, headers=headers) as new_response:
                        if new_response.status != 200:
                            _LOGGER.error("Failed to get vehicle data after reauth: %s", new_response.status)
                            raise NiuApiClientError("Failed to get vehicle data")
                        return await new_response.json()
                elif response.status != 200:
                    _LOGGER.error("Failed to get vehicle data: %s", response.status)
                    raise NiuApiClientError("Failed to get vehicle data")
                return await response.json()
        except aiohttp.ClientError as error:
            _LOGGER.error("Error getting vehicle data: %s", error)
            raise NiuApiClientError(f"Network error: {error}") from error

    async def async_get_battery_level(self) -> int:
        """Get battery level."""
        data = await self.async_get_vehicle_data()
        # Extract battery level from data
        return data.get("battery", {}).get("level", 0)

    async def async_get_range(self) -> float:
        """Get remaining range."""
        data = await self.async_get_vehicle_data()
        # Extract range from data
        return data.get("range", 0.0)

    async def async_get_current_speed(self) -> float:
        """Get current speed."""
        data = await self.async_get_vehicle_data()
        # Extract speed from data
        return data.get("speed", 0.0)

    async def async_get_total_mileage(self) -> float:
        """Get total mileage."""
        data = await self.async_get_vehicle_data()
        # Extract mileage from data
        return data.get("mileage", 0.0)