#!/bin/bash

site_id=$1

if [ -z "$site_id" ]; then
    echo "Error: Site ID is required"
    exit 1
fi

site_path="/sites/$site_id"

if [ ! -d "$site_path" ]; then
    echo "Error: Site directory does not exist"
    exit 1
fi

cd "$site_path"

# Check Hugo config file
if [ ! -f "config.yaml" ] && [ ! -f "config.toml" ] && [ ! -f "config.json" ]; then
    echo "Error: No Hugo configuration file found"
    exit 1
fi

# Check content directory
if [ ! -d "content" ]; then
    echo "Error: No content directory found"
    exit 1
fi

# Validate Hugo site structure
hugo check

if [ $? -eq 0 ]; then
    echo "Site validation successful"
    exit 0
else
    echo "Site validation failed"
    exit 1
fi
