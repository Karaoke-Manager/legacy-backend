#!/usr/bin/env python
from data import Dataset
from karman import Model
from karman import app_config
from karman import make_session

Model.metadata.drop_all(app_config.db_engine)
Model.metadata.create_all(app_config.db_engine)
Dataset().load(make_session())
