from pydantic import BaseModel
from typing import List

from fastapi import status


class SatelliteBase(BaseModel):
  distance: float
  message: list


class Satellite(SatelliteBase):
    name: str


class SatellitesList(BaseModel):
    satellites: List[Satellite]


class TxResponse(BaseModel):
    position: dict
    message: str