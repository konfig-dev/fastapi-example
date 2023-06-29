#!/bin/bash

cd "$(dirname "$0")"

poetry install
poetry run uvicorn main:app --reload
