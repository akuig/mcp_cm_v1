#!/bin/bash
# Add TMF622 Order Management functionality to Enhanced MCP System

echo "🔧 Adding TMF622 Order Management to Enhanced MCP System"
echo "======================================================="

# Check if files exist
if [ ! -f "catalog_manager_extended.py" ]; then
    echo "❌ Error: catalog_manager_extended.py not found"
    exit 1
fi

# Backup existing files
echo "Creating backups..."
cp catalog_manager_extended.py catalog_manager_extended.py.backup
echo "✅ Backup created: catalog_manager_extended.py.backup"

# Check if TMF622 GET endpoint already exists
if grep -q "get_product_orders" catalog_manager_extended.py; then
    echo "⚠️  TMF622 GET endpoints already exist in catalog manager"
else
    echo "Adding TMF622 GET endpoints to catalog manager..."
    
    # Add the TMF622 GET endpoints before the last line of the file
    head -n -1 catalog_manager_extended.py > temp_catalog.py
    
    cat >> temp_catalog.py << 'EOF'

# ============================================================================
# TMF622 ORDER RETRIEVAL ENDPOINTS - ADDED
# ============================================================================

@app.route('/tmf622/productOrder', methods=['GET'])
def get_product_orders():
    """TMF622: Get product orders (list/search)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters
        customer_id = request.args.get('relatedParty.id')  # TMF standard parameter
        order_id = request.args.get('id')
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = """
            SELECT o.*, c.name as customer_name,
                   oa.street_number, oa.street_name, oa.city,
                   po.name as product_name, po.price_monthly
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            LEFT JOIN order_addresses oa ON o.id = oa.order_id
            LEFT JOIN product_offerings po ON o.product_offering_id = po.id
        """
        
        params = []
        conditions = []
        
        if order_id:
            conditions.append("o.id = %s")
            params.append(order_id)
        
        if customer_id:
            conditions.append("o.customer_id = %s")
            params.append(customer_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY o.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        orders = cursor.fetchall()
        
        # Format response in TMF622 standard format
        tmf_orders = []
        for order in orders:
            tmf_order = {
                "id": order['id'],
                "orderDate": order['order_date'].isoformat() if order['order_date'] else None,
                "externalId": order['external_id'],
                "state": order['status'],  # TMF uses 'state' instead of 'status'
                "relatedParty": [{
                    "id": order['customer_id'],
                    "name": order['customer_name'],
                    "role": "customer"
                }] if order['customer_id'] else [],
                "orderItem": [{
                    "id": "1",
                    "action": "add",
                    "productOffering": {
                        "id": order['product_offering_id'],
                        "name": order['product_name']
                    },
                    "product": {
                        "place": {
                            "streetNumber": order['street_number'],
                            "streetName": order['street_name'],
                            "city": order['city']
                        }
                    }
                }] if order['product_offering_id'] else [],
                "orderTotalPrice": {
                    "price": {
                        "dutyFreeAmount": {
                            "value": float(order['price_monthly']) if order['price_monthly'] else 0,
                            "unit": "USD"
                        }
                    }
                } if order['price_monthly'] else None
            }
            tmf_orders.append(tmf_order)
        
        cursor.close()
        conn.close()
        
        return jsonify(tmf_orders)
    
    except Exception as e:
        logger.error(f"Error retrieving orders: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/tmf622/productOrder/<order_id>', methods=['GET'])
def get_product_order_by_id(order_id):
    """TMF622: Get specific product order by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT o.*, c.name as customer_name,
                   oa.street_number, oa.street_name, oa.city,
                   po.name as product_name, po.price_monthly
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            LEFT JOIN order_addresses oa ON o.id = oa.order_id
            LEFT JOIN product_offerings po ON o.product_offering_id = po.id
            WHERE o.id = %s
        """, (order_id,))
        
        order = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        # Format response in TMF622 standard format
        tmf_order = {
            "id": order['id'],
            "orderDate": order['order_date'].isoformat() if order['order_date'] else None,
            "externalId": order['external_id'],
            "state": order['status'],
            "relatedParty": [{
                "id": order['customer_id'],
                "name": order['customer_name'],
                "role": "customer"
            }] if order['customer_id'] else [],
            "orderItem": [{
                "id": "1",
                "action": "add",
                "productOffering": {
                    "id": order['product_offering_id'],
                    "name": order['product_name']
                },
                "product": {
                    "place": {
                        "streetNumber": order['street_number'],
                        "streetName": order['street_name'],
                        "city": order['city']
                    }
                }
            }] if order['product_offering_id'] else [],
            "orderTotalPrice": {
                "price": {
                    "dutyFreeAmount": {
                        "value": float(order['price_monthly']) if order['price_monthly'] else 0,
                        "unit": "USD"
                    }
                }
            } if order['price_monthly'] else None
        }
        
        return jsonify(tmf_order)
    
    except Exception as e:
        logger.error(f"Error retrieving order: {str(e)}")
        return jsonify({"error": str(e)}), 500

EOF

    # Add the last line back
    tail -n 1 catalog_manager_extended.py >> temp_catalog.py
    
    # Replace the original file
    mv temp_catalog.py catalog_manager_extended.py
    
    echo "✅ TMF622 GET endpoints added to catalog manager"
fi

echo ""
echo "📋 Next Steps:"
echo "============="
echo ""
echo "1. 🔧 Restart the enhanced services:"
echo "   make enhanced-down"
echo "   make enhanced-up"
echo ""
echo "2. 🧪 Test the new API endpoints:"
echo "   curl \"http://localhost:8080/tmf622/productOrder\""
echo "   curl \"http://localhost:8080/tmf622/productOrder?relatedParty.id=8452935\""
echo ""
echo "3. 📝 Add MCP Tool (requires manual editing of MCP server file):"
echo "   - Add order_management_tool() method"
echo "   - Add handle_order_management() method"
echo "   - Register the tool in __init__()"
echo "   - Update handle_tool_call() method"
echo ""
echo "4. 📄 Reference the artifacts above for complete MCP tool code"
echo ""
echo "🎯 After completing step 3, you'll have the order_management MCP tool available!"
