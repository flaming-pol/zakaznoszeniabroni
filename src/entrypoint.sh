#!/bin/sh

alembic upgrade head
python znb.py
