class DeviceAdapterError(Exception):
    """Base adapter error."""


class DeviceConfigurationError(DeviceAdapterError):
    """Raised when a device config is invalid."""


class DeviceConnectivityError(DeviceAdapterError):
    """Raised when a device cannot be reached or returns an invalid response."""
