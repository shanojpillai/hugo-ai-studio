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

# Build the Hugo site
hugo --minify

if [ $? -eq 0 ]; then
    echo "Site built successfully"
    exit 0
else
    echo "Error building site"
    exit 1
fi
