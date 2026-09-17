#!/usr/bin/env bash

set -e


echo "Starting AI Coding Assistant backend..."


uvicorn backend.app.main:app --reload
