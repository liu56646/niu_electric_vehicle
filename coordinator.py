"""
Data coordinator for Niu Electric Vehicle integration.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DATA_COORDINATOR, DEFAULT_SCAN_INTERVAL, DOMAIN
from .niu_api import NiuApiClient, NiuApiClientError

_LOGGER = logging.getLogger(__name__)

class NiuDataCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from the Niu API."""

    def __init__(
        self, hass: HomeAssistant, entry_data: dict[str, Any]
    ) -> None:
        """Initialize the coordinator."""
        self.api_client = NiuApiClient(
            entry_data["username"],
            entry_data["password"],
            entry_data["vehicle_id"],
            async_get_clientsession(hass),
        )
        self.vehicle_id = entry_data["vehicle_id"]

        super().__init__(
            hass,
            _LOGGER,
            name=f"Niu Vehicle {self.vehicle_id}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            data = await self.api_client.async_get_vehicle_data()
            _LOGGER.debug("Successfully updated vehicle data")
            return data
        except NiuApiClientError as error:
            raise UpdateFailed(f"Error fetching data: {error}") from error