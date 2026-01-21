from core.telemetry_core import TelemetryCore
from core.telemetry_finalize import TelemetryFinalizeMixin
from core.telemetry_sensors import TelemetrySensorsMixin
from core.telemetry_metrics import TelemetryMetricsMixin


class Telemetry(
    TelemetryCore,
    TelemetrySensorsMixin,
    TelemetryMetricsMixin,
    TelemetryFinalizeMixin,
):
    pass
