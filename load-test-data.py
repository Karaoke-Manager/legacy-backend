#!/usr/bin/env python

from karman.database import get_db_engine, make_session
from karman.models import Model
from tests.data import Dataset

Model.metadata.bind = get_db_engine()
Model.metadata.drop_all()
Model.metadata.create_all()
Dataset().load(make_session())
