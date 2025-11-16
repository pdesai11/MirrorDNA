#!/bin/bash
#
# MirrorDNA Quickstart Script
#
# Demonstrates core protocol functionality
# Usage: ./scripts/quickstart.sh
#

set -e

echo "========================================="
echo "MirrorDNA Protocol - Quickstart Demo"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create demo directory
DEMO_DIR="/tmp/mirrordna-quickstart-$(date +%s)"
mkdir -p "$DEMO_DIR"
cd "$DEMO_DIR"

echo -e "${BLUE}Demo directory:${NC} $DEMO_DIR"
echo ""

# 1. Generate configuration
echo -e "${GREEN}Step 1: Generating configuration templates${NC}"
mirrordna config generate --template minimal --format yaml --output master_citation.yaml
echo "  ✓ Created master_citation.yaml"
echo ""

# 2. Validate configuration
echo -e "${GREEN}Step 2: Validating configuration${NC}"
mirrordna config validate --master-citation master_citation.yaml
echo ""

# 3. Create an identity
echo -e "${GREEN}Step 3: Creating an agent identity${NC}"
identity_output=$(mirrordna identity create --type agent --metadata '{"name":"Demo Agent","version":"1.0"}' 2>&1)
identity_id=$(echo "$identity_output" | grep -o '"identity_id": "[^"]*"' | cut -d'"' -f4)
echo "$identity_output"
echo ""
echo -e "  ${YELLOW}Identity ID:${NC} $identity_id"
echo ""

# 4. Retrieve the identity
echo -e "${GREEN}Step 4: Retrieving the identity${NC}"
mirrordna identity get "$identity_id"
echo ""

# 5. Compute checksums
echo -e "${GREEN}Step 5: Computing checksums${NC}"
echo "Sample content for checksum" > sample.txt
checksum=$(mirrordna checksum compute --file sample.txt)
echo "  File: sample.txt"
echo "  Checksum: $checksum"
echo ""

# 6. Verify checksum
echo -e "${GREEN}Step 6: Verifying checksum${NC}"
mirrordna checksum verify sample.txt "$checksum"
echo ""

# 7. Create a snapshot
echo -e "${GREEN}Step 7: Creating state snapshot${NC}"
mirrordna snapshot create --output snapshot.json --format json
echo ""

# 8. Load the snapshot
echo -e "${GREEN}Step 8: Loading snapshot${NC}"
mirrordna snapshot load snapshot.json
echo ""

# Summary
echo "========================================="
echo -e "${GREEN}Quickstart Demo Complete!${NC}"
echo "========================================="
echo ""
echo "Files created in: $DEMO_DIR"
echo "  - master_citation.yaml"
echo "  - sample.txt"
echo "  - snapshot.json"
echo ""
echo "Try these commands:"
echo "  mirrordna --help                     # Show all commands"
echo "  mirrordna identity create --help     # Identity management"
echo "  mirrordna config validate --help     # Config validation"
echo "  mirrordna checksum compute --help    # Checksumming"
echo ""
echo "Learn more:"
echo "  ./docs/index.md                      # Documentation"
echo "  ./examples/                          # Code examples"
echo ""
