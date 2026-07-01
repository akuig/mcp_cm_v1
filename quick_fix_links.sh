#!/bin/bash
# Quick fix script - creates product_service_links table directly

echo "Creating product_service_links table..."

PGPASSWORD="telecom_catalog" psql -h localhost -U telecom_user -d telecom_catalog -f create_product_service_links.sql

echo ""
echo "Done! Check output above for any errors."
