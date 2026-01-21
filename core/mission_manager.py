from core.mission_manager_base import MissionManagerBase
from core.mission_manager_drive import MissionManagerDriveMixin
from core.mission_manager_menu import MissionManagerMenuMixin
from core.mission_manager_routes import MissionManagerRoutesMixin


class MissionManager(
    MissionManagerBase,
    MissionManagerMenuMixin,
    MissionManagerDriveMixin,
    MissionManagerRoutesMixin,
):
    pass
