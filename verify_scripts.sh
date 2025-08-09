#!/bin/bash
# Quick verification that scripts are properly formatted

echo "🔍 Verifying script file formats..."
echo ""

scripts=("restart_with_order_tool.sh" "make_executable.sh" "restart_with_orders.sh")

for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        # Check if file has literal \n characters
        if grep -q '\\n' "$script"; then
            echo "❌ $script has literal \\n characters"
        else
            echo "✅ $script is properly formatted"
        fi
        
        # Make it executable
        chmod +x "$script" 2>/dev/null
    else
        echo "⚠️  $script not found"
    fi
done

echo ""
echo "✅ Script verification complete!"
echo ""
echo "Ready to use:"
echo "• make restart-with-orders"
echo "• ./restart_with_order_tool.sh"
echo ""
