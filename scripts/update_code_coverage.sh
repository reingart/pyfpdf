#!/usr/bin/env bash
cd "$(dirname "$0")"
. .env
cd ..
coverage run setup.py test
curl -s https://codecov.io/bash | CODECOV_TOKEN="$cctoken" bash -s -
