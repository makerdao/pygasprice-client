#!/bin/sh

py.test --cov=pygasprice_client --cov-report=term --cov-append tests/ $@
