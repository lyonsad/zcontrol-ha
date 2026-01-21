"""The Z-Control Sump Pump Alarm integration."""

import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import ZControlApiClient, ZControlAuthError, ZControlApiError
from .const import DOMAIN
from .coordinator import ZControlCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SENSOR,
]

type ZControlConfigEntry = ConfigEntry[ZControlData]


class ZControlData:
    """Runtime data for Z-Control integration."""

    def __init__(
        self,
        coordinator: ZControlCoordinator,
        client: ZControlApiClient,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize runtime data."""
        self.coordinator = coordinator
        self.client = client
        self.session = session


async def async_setup_entry(hass: HomeAssistant, entry: ZControlConfigEntry) -> bool:
    """Set up Z-Control from a config entry."""
    # Create session and client
    session = aiohttp.ClientSession()

    client = ZControlApiClient(
        session,
        entry.data[CONF_EMAIL],
        entry.data[CONF_PASSWORD],
    )

    try:
        # Authenticate
        await client.authenticate()
    except ZControlAuthError as err:
        await session.close()
        raise ConfigEntryNotReady(f"Authentication failed: {err}") from err
    except ZControlApiError as err:
        await session.close()
        raise ConfigEntryNotReady(f"Connection failed: {err}") from err

    # Create coordinator
    coordinator = ZControlCoordinator(hass, client)

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store runtime data
    entry.runtime_data = ZControlData(coordinator, client, session)

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ZControlConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Close the session
        await entry.runtime_data.session.close()

    return unload_ok
