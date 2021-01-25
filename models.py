from pydantic import BaseModel
from typing import List

from fastapi import status


class Satellite(BaseModel):
  name: str
  distance: float
  message: list

class SatellitesList(BaseModel):
    satellites: List[Satellite]


class TxResponse(BaseModel):
    position: dict
    message: str