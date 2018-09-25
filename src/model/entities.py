#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from decimal import Decimal
from typing import Optional, Union

from dataclasses import dataclass


@dataclass
class User:
    name: str
    min_: Union[Decimal, int]
    max_: Union[Decimal, int]
    current: Union[Decimal, int]
    id_: Optional[int] = None
