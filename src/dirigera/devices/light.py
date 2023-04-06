from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List

from ..hub.abstract_smart_home_hub import AbstractSmartHomeHub


class StartupEnum(Enum):
    START_ON = "startOn"
    START_OFF = "startOff"


@dataclass
class Light:
    dirigera_client: AbstractSmartHomeHub
    light_id: str
    is_reachable: bool
    custom_name: str
    is_on: bool
    startup_on_off: StartupEnum | None
    light_level: int | None
    color_temp: int | None
    color_temp_min: int | None
    color_temp_max: int | None
    color_hue: int | None
    color_saturation: float | None
    can_receive: List[str]

    def refresh(self) -> None:
        data = self.dirigera_client.get(route=f"/devices/{self.light_id}")
        attributes: Dict[str, Any] = data["attributes"]
        self.light_id=data["id"]
        self.is_reachable=data["isReachable"]
        self.custom_name=attributes["customName"]
        self.is_on=attributes["isOn"]
        self.startup_on_off=attributes.get("startupOnOff")
        self.light_level=attributes.get("lightLevel")
        self.color_temp=attributes.get("colorTemperature")
        self.color_temp_min=attributes.get("colorTemperatureMin")
        self.color_temp_max=attributes.get("colorTemperatureMax")
        self.color_hue=attributes.get("colorHue")
        self.color_saturation=attributes.get("colorSaturation")
        self.can_receive=data["capabilities"]["canReceive"]

    def set_name(self, name: str) -> None:
        if "customName" not in self.can_receive:
            raise AssertionError("This lamp does not support the swith-off function")

        data = [{"attributes": {"customName": name}}]
        self.dirigera_client.patch(route=f"/devices/{self.light_id}", data=data)
        self.custom_name = name

    def set_light(self, lamp_on: bool) -> None:
        if "isOn" not in self.can_receive:
            raise AssertionError("This lamp does not support the swith-off function")

        data = [{"attributes": {"isOn": lamp_on}}]
        self.dirigera_client.patch(route=f"/devices/{self.light_id}", data=data)
        self.is_on = lamp_on

    def set_light_level(self, light_level: int) -> None:
        if "lightLevel" not in self.can_receive:
            raise AssertionError(
                "This lamp does not support the set lightLevel function"
            )
        if light_level < 0 or light_level > 100:
            raise AssertionError("light_level must be a value between 0 and 100")

        data = [{"attributes": {"lightLevel": light_level}}]
        self.dirigera_client.patch(route=f"/devices/{self.light_id}", data=data)
        self.light_level = light_level

    def set_color_temperature(self, color_temp: int) -> None:
        if "colorTemperature" not in self.can_receive:
            raise AssertionError(
                "This lamp does not support the set colorTemperature function"
            )
        if color_temp < self.color_temp_max or color_temp > self.color_temp_min:
            raise AssertionError(
                f"color_temperature must be a value between {self.color_temp_max} and {self.color_temp_min}"
            )

        data = [{"attributes": {"colorTemperature": color_temp}}]
        self.dirigera_client.patch(route=f"/devices/{self.light_id}", data=data)
        self.color_temp = color_temp

    def set_light_color(self, hue: int, saturation: float) -> None:
        if (
            "colorHue" not in self.can_receive
            or "colorSaturation" not in self.can_receive
        ):
            raise AssertionError(
                "This lamp does not support the set light color function"
            )
        if hue < 0 or hue > 360:
            raise AssertionError("hue must be a value between 0 and 360")
        if saturation < 0.0 or saturation > 1.0:
            raise AssertionError("saturation must be a value between 0.0 and 1.0")

        data = [{"attributes": {"colorHue": hue, "colorSaturation": saturation}}]
        self.dirigera_client.patch(route=f"/devices/{self.light_id}", data=data)
        self.color_hue = hue
        self.color_saturation = saturation

    def set_startup_behaviour(self, behaviour: StartupEnum) -> None:
        """
        Sets the behaviour of the lamp in case of a power outage.
        When set to START_ON the lamp will turn on once the power is back.
        When set to START_OFF the lamp will stay off once the power is back.
        """
        data = [{"attributes": {"startupOnOff": behaviour}}]
        self.dirigera_client.patch(route=f"/devices/{self.light_id}", data=data)
        self.startup_on_off = behaviour


def dict_to_light(data: Dict[str, Any], dirigera_client: AbstractSmartHomeHub):
    attributes: Dict[str, Any] = data["attributes"]

    light_level = attributes.get("lightLevel")
    color_temp = attributes.get("colorTemperature")
    color_temp_min = attributes.get("colorTemperatureMin")
    color_temp_max = attributes.get("colorTemperatureMax")
    color_hue = attributes.get("colorHue")
    color_saturation = attributes.get("colorSaturation")

    return Light(
        dirigera_client=dirigera_client,
        light_id=data["id"],
        is_reachable=data["isReachable"],
        custom_name=attributes["customName"],
        is_on=attributes["isOn"],
        startup_on_off=attributes.get("startupOnOff"),
        light_level=light_level,
        color_temp=color_temp,
        color_temp_min=color_temp_min,
        color_temp_max=color_temp_max,
        color_hue=color_hue,
        color_saturation=color_saturation,
        can_receive=data["capabilities"]["canReceive"],
    )
