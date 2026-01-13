#!/bin/bash

# OSRM Data Download and Setup Script
# This script downloads OpenStreetMap data and prepares it for OSRM

set -e

echo "=== OSRM Data Setup for Dashcam Backend ==="

# Check if running in the correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Create data directory
DATA_DIR="./osrm_data"
mkdir -p "$DATA_DIR"

# Region selection
echo ""
echo "Select a region to download:"
echo "1) North America"
echo "2) United States"
echo "3) California"
echo "4) Europe"
echo "5) Custom URL"
read -p "Enter your choice (1-5): " REGION_CHOICE

case $REGION_CHOICE in
    1)
        URL="http://download.geofabrik.de/north-america-latest.osm.pbf"
        FILE="north-america-latest.osm.pbf"
        ;;
    2)
        URL="http://download.geofabrik.de/north-america/us-latest.osm.pbf"
        FILE="us-latest.osm.pbf"
        ;;
    3)
        URL="http://download.geofabrik.de/north-america/us/california-latest.osm.pbf"
        FILE="california-latest.osm.pbf"
        ;;
    4)
        URL="http://download.geofabrik.de/europe-latest.osm.pbf"
        FILE="europe-latest.osm.pbf"
        ;;
    5)
        read -p "Enter the URL to download: " URL
        FILE=$(basename "$URL")
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Download the map data
echo "Downloading map data from $URL..."
echo "This may take a while depending on the region size..."
wget -O "$DATA_DIR/$FILE" "$URL"

echo "Map data downloaded successfully!"

# Process the data with OSRM
echo "Processing map data with OSRM..."
echo "This will take some time..."

# Extract
echo "Step 1/3: Extracting..."
docker run -t -v "$PWD/$DATA_DIR:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua "/data/$FILE"

# Partition
echo "Step 2/3: Partitioning..."
docker run -t -v "$PWD/$DATA_DIR:/data" osrm/osrm-backend osrm-partition "/data/${FILE%.osm.pbf}.osrm"

# Customize
echo "Step 3/3: Customizing..."
docker run -t -v "$PWD/$DATA_DIR:/data" osrm/osrm-backend osrm-customize "/data/${FILE%.osm.pbf}.osrm"

# Rename to map.osrm for consistency
echo "Finalizing..."
cd "$DATA_DIR"
for f in ${FILE%.osm.pbf}.osrm*; do
    if [ -f "$f" ]; then
        mv "$f" "map${f#${FILE%.osm.pbf}}"
    fi
done
cd ..

echo ""
echo "=== OSRM Setup Complete ==="
echo ""
echo "Map data is ready in $DATA_DIR"
echo "You can now start the OSRM backend with:"
echo "  docker-compose up -d osrm-backend"
echo ""
echo "Note: Make sure the osrm_data volume in docker-compose.yml points to $DATA_DIR"
