#!/usr/bin/env bash
cd "$(dirname "$0")"
. .env
curl -s https://codecov.io/bash | CODECOV_TOKEN="$cctoken" bash -s -
