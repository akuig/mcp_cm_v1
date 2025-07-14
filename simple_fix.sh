#!/bin/bash
# The simplest way to get everything working

echo "🚀 SIMPLE FIX - Just 3 Steps!"
echo "============================="
echo ""

# Make this executable first
chmod +x final_fix_asyncio.sh

echo "Step 1 of 3: Applying all fixes..."
./final_fix_asyncio.sh

echo ""
echo "Step 2 of 3: Waiting for services (30 seconds)..."
sleep 30

echo ""
echo "Step 3 of 3: Verifying everything works..."
python3 verify_setup.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Now run: python test_fault_management.py"
