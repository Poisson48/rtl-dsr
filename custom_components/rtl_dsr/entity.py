"""Entity base class for the RTL-SDR integration."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RtlDsrCoordinator
from .model import SdrState


class RtlDsrEntity(CoordinatorEntity[RtlDsrCoordinator]):
    """Base entity bound to a :class:`RtlDsrCoordinator`."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: RtlDsrCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._key = key
        idx = coordinator._device_index
        self._attr_unique_id = f"rtl_dsr_{idx}_{key}"
        tuner = (coordinator.data.tuner_type if coordinator.data else "unknown")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"rtl_dsr_{idx}")},
            name=f"RTL-SDR #{idx}",
            manufacturer="Realtek",
            model=f"RTL2832U / {tuner}",
            sw_version="1.0",
        )

    @property
    def state(self) -> SdrState | None:
        return self.coordinator.data

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data is not None and self.coordinator.data.connected
