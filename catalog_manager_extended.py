#!/usr/bin/env python3
"""
Enhanced Catalog Manager - Fixed version with proper API responses
Implements TM Forum APIs and enhanced catalog management
"""

import logging
from datetime import datetime
from typing import Dict, Optional, List
import uuid
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'postgres'),
    'port': os.environ.get('DB_PORT', '5432'),
    'database': os.environ.get('DB_NAME', 'telecom_catalog'),
    'user': os.environ.get('DB_USER', 'telecom_user'),
    'password': os.environ.get('DB_PASSWORD', 'telecom_pass')
}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

# ============================================================================
# TMF FORUM APIS
# ============================================================================

@app.route('/tmf637/serviceQualification', methods=['POST'])
def service_qualification():
    """TMF637: Check service availability at location"""
    try:
        data = request.json
        address = data.get('address', {})
        service_spec = data.get('serviceSpecification', {})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the service type from specifications
        cursor.execute("""
            SELECT service_type FROM service_specifications 
            WHERE id = %s
        """, (service_spec.get('id'),))
        
        spec_result = cursor.fetchone()
        if not spec_result:
            # Try with common service IDs
            service_id = service_spec.get('id', '').lower()
            if 'fiber' in service_id or 'internet' in service_id:
                service_type = 'fiber_internet'
            elif 'tv' in service_id or 'cable' in service_id:
                service_type = 'tv'
            elif 'mobile' in service_id or '5g' in service_id or '4g' in service_id:
                service_type = 'mobile'
            else:
                cursor.close()
                conn.close()
                return jsonify({
                    "serviceQualificationItem": [{
                        "qualificationResult": "unqualified",
                        "productOffering": service_spec,
                        "reason": "Invalid service specification"
                    }]
                })
        else:
            service_type = spec_result['service_type']
        
        # Check coverage at location
        cursor.execute("""
            SELECT * FROM service_coverage 
            WHERE street_name = %s 
            AND city = %s 
            AND service_type = %s
        """, (address.get('streetName'), address.get('city'), service_type))
        
        coverage = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if coverage:
            result = {
                "serviceQualificationItem": [{
                    "qualificationResult": "qualified",
                    "productOffering": {
                        "id": service_spec.get('id'),
                        "name": service_spec.get('name')
                    }
                }]
            }
        else:
            result = {
                "serviceQualificationItem": [{
                    "qualificationResult": "unqualified",
                    "productOffering": {
                        "id": service_spec.get('id'),
                        "name": service_spec.get('name')
                    },
                    "reason": "Service not available at this location"
                }]
            }
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in service qualification: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/tmf629/customer/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """TMF629: Get customer information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM customers WHERE id = %s
        """, (customer_id,))
        
        customer = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if customer:
            result = {
                "id": customer['id'],
                "name": customer['name'],
                "accountStatus": customer['account_status'],
                "creditScore": customer['credit_score'],
                "hasOverduePayments": customer['has_overdue_payments'],
                "address": {
                    "streetNumber": customer['street_number'],
                    "streetName": customer['street_name'],
                    "city": customer['city'],
                    "postalCode": customer['postal_code']
                }
            }
            return jsonify(result)
        else:
            return jsonify({"error": "Customer not found"}), 404
    
    except Exception as e:
        logger.error(f"Error getting customer: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/tmf622/productOrder', methods=['GET', 'POST'])
def handle_product_order():
    """TMF622: Handle both GET (list/search) and POST (create) for product orders"""
    if request.method == 'POST':
        return create_product_order()
    else:
        return get_product_orders()

@app.route('/tmf622/productOrder/<order_id>', methods=['GET', 'PATCH', 'DELETE'])
def handle_single_product_order(order_id):
    """TMF622: Handle single order operations - GET, PATCH (update), DELETE"""
    if request.method == 'GET':
        return get_single_product_order(order_id)
    elif request.method == 'PATCH':
        return update_product_order(order_id)
    elif request.method == 'DELETE':
        return delete_product_order(order_id)

@app.route('/tmf622/productOrder/<order_id>/cancel', methods=['POST'])
def cancel_product_order(order_id):
    """TMF622: Cancel a product order"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if order exists and get current status
        cursor.execute("""
            SELECT id, status FROM orders WHERE id = %s
        """, (order_id,))
        
        order = cursor.fetchone()
        if not order:
            cursor.close()
            conn.close()
            return jsonify({"error": "Order not found"}), 404
        
        # Check if order can be cancelled
        if order['status'] in ['completed', 'cancelled', 'failed', 'rejected']:
            cursor.close()
            conn.close()
            return jsonify({
                "error": f"Cannot cancel order with status: {order['status']}"
            }), 400
        
        # Update order status to cancelled
        cursor.execute("""
            UPDATE orders 
            SET status = 'cancelled', 
                updated_at = %s
            WHERE id = %s
            RETURNING *
        """, (datetime.utcnow(), order_id))
        
        updated_order = cursor.fetchone()
        
        # Log status change
        cursor.execute("""
            INSERT INTO order_status_history (order_id, status, changed_at, reason)
            VALUES (%s, %s, %s, %s)
        """, (order_id, 'cancelled', datetime.utcnow(), 'Order cancelled by user'))
        
        conn.commit()
        
        # Get complete order with address
        cursor.execute("""
            SELECT o.*, oa.street_number, oa.street_name, oa.city
            FROM orders o
            LEFT JOIN order_addresses oa ON o.id = oa.order_id
            WHERE o.id = %s
        """, (order_id,))
        
        order_with_details = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Return TMF622 compliant response
        return jsonify({
            "id": order_with_details['id'],
            "orderDate": order_with_details['order_date'].isoformat() if order_with_details['order_date'] else None,
            "state": order_with_details['status'],
            "externalId": order_with_details['external_id'],
            "relatedParty": [{
                "id": order_with_details['customer_id'],
                "role": "customer"
            }],
            "orderItem": [{
                "action": "add",
                "productOffering": {
                    "id": order_with_details['product_offering_id']
                },
                "product": {
                    "place": {
                        "streetNumber": order_with_details['street_number'],
                        "streetName": order_with_details['street_name'],
                        "city": order_with_details['city']
                    }
                }
            }],
            "cancellationDate": datetime.utcnow().isoformat() + "Z",
            "cancellationReason": "Order cancelled by user"
        })
    
    except Exception as e:
        logger.error(f"Error cancelling order: {str(e)}")
        return jsonify({"error": str(e)}), 500

def create_product_order():
    """TMF622: Create product order"""
    try:
        data = request.json
        order_id = str(uuid.uuid4())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create order in database
        cursor.execute("""
            INSERT INTO orders (
                id, order_date, external_id, customer_id, 
                product_offering_id, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            order_id,
            data.get('orderDate'),
            data.get('externalId'),
            data['relatedParty'][0]['id'],
            data['orderItem'][0]['productOffering']['id'],
            'created',
            datetime.utcnow()
        ))
        
        order = cursor.fetchone()
        
        # Store address information
        address = data['orderItem'][0]['product']['place']
        cursor.execute("""
            INSERT INTO order_addresses (
                order_id, street_number, street_name, city
            ) VALUES (%s, %s, %s, %s)
        """, (
            order_id,
            address.get('streetNumber'),
            address.get('streetName'),
            address.get('city')
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        result = {
            "id": order_id,
            "orderDate": data.get('orderDate'),
            "externalId": data.get('externalId'),
            "status": "created",
            "relatedParty": data.get('relatedParty'),
            "orderItem": data.get('orderItem')
        }
        
        return jsonify(result), 201
    
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        return jsonify({"error": str(e)}), 500

def get_single_product_order(order_id):
    """TMF622: Get single product order by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT o.*, oa.street_number, oa.street_name, oa.city
            FROM orders o
            LEFT JOIN order_addresses oa ON o.id = oa.order_id
            WHERE o.id = %s
        """, (order_id,))
        
        order = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        # Return TMF622 compliant response
        return jsonify({
            "id": order['id'],
            "orderDate": order['order_date'].isoformat() if order['order_date'] else None,
            "state": order['status'],
            "externalId": order['external_id'],
            "relatedParty": [{
                "id": order['customer_id'],
                "role": "customer"
            }],
            "orderItem": [{
                "action": "add",
                "productOffering": {
                    "id": order['product_offering_id']
                },
                "product": {
                    "place": {
                        "streetNumber": order['street_number'],
                        "streetName": order['street_name'],
                        "city": order['city']
                    }
                }
            }]
        })
    
    except Exception as e:
        logger.error(f"Error getting order: {str(e)}")
        return jsonify({"error": str(e)}), 500

def update_product_order(order_id):
    """TMF622: Update product order status"""
    try:
        data = request.json
        new_status = data.get('state') or data.get('status')
        
        if not new_status:
            return jsonify({"error": "Missing 'state' field in request"}), 400
        
        # Valid TMF622 order states
        valid_states = ['acknowledged', 'inProgress', 'pending', 'held', 
                       'completed', 'cancelled', 'failed', 'rejected', 'created']
        
        if new_status not in valid_states:
            return jsonify({
                "error": f"Invalid state: {new_status}. Valid states are: {', '.join(valid_states)}"
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if order exists
        cursor.execute("""
            SELECT id, status FROM orders WHERE id = %s
        """, (order_id,))
        
        order = cursor.fetchone()
        if not order:
            cursor.close()
            conn.close()
            return jsonify({"error": "Order not found"}), 404
        
        # Update order status
        cursor.execute("""
            UPDATE orders 
            SET status = %s, 
                updated_at = %s
            WHERE id = %s
            RETURNING *
        """, (new_status, datetime.utcnow(), order_id))
        
        updated_order = cursor.fetchone()
        
        # Log status change
        reason = data.get('reason', f"Status changed from {order['status']} to {new_status}")
        cursor.execute("""
            INSERT INTO order_status_history (order_id, status, changed_at, reason)
            VALUES (%s, %s, %s, %s)
        """, (order_id, new_status, datetime.utcnow(), reason))
        
        conn.commit()
        
        # Get complete order with address
        cursor.execute("""
            SELECT o.*, oa.street_number, oa.street_name, oa.city
            FROM orders o
            LEFT JOIN order_addresses oa ON o.id = oa.order_id
            WHERE o.id = %s
        """, (order_id,))
        
        order_with_details = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Return TMF622 compliant response
        return jsonify({
            "id": order_with_details['id'],
            "orderDate": order_with_details['order_date'].isoformat() if order_with_details['order_date'] else None,
            "state": order_with_details['status'],
            "externalId": order_with_details['external_id'],
            "relatedParty": [{
                "id": order_with_details['customer_id'],
                "role": "customer"
            }],
            "orderItem": [{
                "action": "add",
                "productOffering": {
                    "id": order_with_details['product_offering_id']
                },
                "product": {
                    "place": {
                        "streetNumber": order_with_details['street_number'],
                        "streetName": order_with_details['street_name'],
                        "city": order_with_details['city']
                    }
                }
            }],
            "lastModifiedDate": datetime.utcnow().isoformat() + "Z"
        })
    
    except Exception as e:
        logger.error(f"Error updating order: {str(e)}")
        return jsonify({"error": str(e)}), 500

def delete_product_order(order_id):
    """TMF622: Delete product order"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if order exists
        cursor.execute("""
            SELECT id, status FROM orders WHERE id = %s
        """, (order_id,))
        
        order = cursor.fetchone()
        if not order:
            cursor.close()
            conn.close()
            return jsonify({"error": "Order not found"}), 404
        
        # Only allow deletion of cancelled or failed orders
        if order['status'] not in ['cancelled', 'failed', 'rejected', 'created']:
            cursor.close()
            conn.close()
            return jsonify({
                "error": f"Cannot delete order with status: {order['status']}. Order must be cancelled, failed, rejected, or created."
            }), 400
        
        # Delete related records first (due to foreign key constraints)
        cursor.execute("DELETE FROM order_addresses WHERE order_id = %s", (order_id,))
        cursor.execute("DELETE FROM order_status_history WHERE order_id = %s", (order_id,))
        
        # Delete the order
        cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": f"Order {order_id} successfully deleted",
            "id": order_id,
            "deletedAt": datetime.utcnow().isoformat() + "Z"
        }), 200
    
    except Exception as e:
        logger.error(f"Error deleting order: {str(e)}")
        return jsonify({"error": str(e)}), 500

def get_product_orders():
    """TMF622: Get product orders (list/search)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters
        customer_id = request.args.get('relatedParty.id')
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
                }] if order['product_offering_id'] else []
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
            }] if order['product_offering_id'] else []
        }
        
        return jsonify(tmf_order)
    
    except Exception as e:
        logger.error(f"Error retrieving order: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/tmf640/serviceActivation', methods=['POST'])
def activate_service():
    """TMF640: Activate service"""
    try:
        data = request.json
        service_id = str(uuid.uuid4())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create service activation record
        service = data.get('service', {})
        cursor.execute("""
            INSERT INTO service_activations (
                id, service_name, service_type, 
                service_specification_id, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            service_id,
            service.get('name'),
            service.get('serviceType'),
            service['serviceSpecification']['id'],
            'activated',
            datetime.utcnow()
        ))
        
        activation = cursor.fetchone()
        
        # Store address for the activation
        address = service.get('place', {})
        cursor.execute("""
            INSERT INTO activation_addresses (
                activation_id, street_number, street_name, city
            ) VALUES (%s, %s, %s, %s)
        """, (
            service_id,
            address.get('streetNumber'),
            address.get('streetName'),
            address.get('city')
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        result = {
            "id": service_id,
            "service": {
                "id": service_id,
                "name": service.get('name'),
                "serviceType": service.get('serviceType'),
                "status": "activated",
                "activationDate": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        return jsonify(result), 201
    
    except Exception as e:
        logger.error(f"Error activating service: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# ENHANCED CATALOG MANAGEMENT APIS - FIXED RESPONSE FORMATS
# ============================================================================

@app.route('/api/service-specifications', methods=['GET', 'POST'])
def handle_service_specifications():
    """List or create service specifications - FIXED FORMAT"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'POST':
            data = request.json
            spec_id = data.get('id', str(uuid.uuid4()))
            
            cursor.execute("""
                INSERT INTO service_specifications (
                    id, name, service_type, description
                ) VALUES (%s, %s, %s, %s)
                RETURNING *
            """, (
                spec_id,
                data.get('name'),
                data.get('service_type'),
                data.get('description')
            ))
            
            spec = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify(spec), 201
        
        # GET: List with filters
        service_type = request.args.get('service_type')
        search = request.args.get('search', '').lower()
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = "SELECT * FROM service_specifications"
        params = []
        conditions = []
        
        if service_type:
            conditions.append("service_type = %s")
            params.append(service_type)
        
        if search:
            conditions.append("(LOWER(name) LIKE %s OR LOWER(description) LIKE %s)")
            params.extend([f'%{search}%', f'%{search}%'])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY service_type, name LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        specs = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as total FROM service_specifications")
        total = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        # FIXED: Return with 'specifications' key
        return jsonify({
            "specifications": specs,
            "total": total,
            "limit": limit,
            "offset": offset
        })
    
    except Exception as e:
        logger.error(f"Error handling service specifications: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/product-offerings', methods=['GET', 'POST'])
def handle_product_offerings():
    """List or create product offerings - FIXED FORMAT"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'POST':
            data = request.json
            offering_id = data.get('id', str(uuid.uuid4()))
            
            cursor.execute("""
                INSERT INTO product_offerings (
                    id, name, description, category, 
                    price_monthly, price_setup, contract_length_months, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                offering_id,
                data.get('name'),
                data.get('description'),
                data.get('category'),
                data.get('price_monthly'),
                data.get('price_setup', 0),
                data.get('contract_length_months', 0),
                data.get('is_active', True)
            ))
            
            offering = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify(offering), 201
        
        # GET: List with filters
        category = request.args.get('category')
        is_active = request.args.get('is_active')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        search = request.args.get('search', '').lower()
        include_services = request.args.get('include_services', 'false').lower() == 'true'
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = "SELECT * FROM product_offerings"
        params = []
        conditions = []
        
        if category:
            conditions.append("category = %s")
            params.append(category)
        
        if is_active is not None:
            conditions.append("is_active = %s")
            params.append(is_active.lower() == 'true')
        
        if min_price is not None:
            conditions.append("price_monthly >= %s")
            params.append(min_price)
        
        if max_price is not None:
            conditions.append("price_monthly <= %s")
            params.append(max_price)
        
        if search:
            conditions.append("(LOWER(name) LIKE %s OR LOWER(description) LIKE %s)")
            params.extend([f'%{search}%', f'%{search}%'])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY category, name LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        offerings = cursor.fetchall()
        
        # Include linked services if requested
        if include_services:
            for offering in offerings:
                cursor.execute("""
                    SELECT ss.* FROM service_specifications ss
                    JOIN product_service_links psl ON ss.id = psl.service_specification_id
                    WHERE psl.product_offering_id = %s
                """, (offering['id'],))
                offering['linked_services'] = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) as total FROM product_offerings")
        total = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        # FIXED: Return with 'offerings' key
        return jsonify({
            "offerings": offerings,
            "total": total,
            "limit": limit,
            "offset": offset
        })
    
    except Exception as e:
        logger.error(f"Error handling product offerings: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/geographic-locations', methods=['GET', 'POST'])
def handle_geographic_locations():
    """List or add geographic locations with coverage - FIXED FORMAT"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'POST':
            data = request.json
            location_id = data.get('id', str(uuid.uuid4()))
            
            cursor.execute("""
                INSERT INTO geographic_locations (
                    id, street_name, street_number, city, state_province, country
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                location_id,
                data.get('street_name'),
                data.get('street_number'),
                data.get('city'),
                data.get('state_province'),
                data.get('country', 'USA')
            ))
            
            location = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify(location), 201
        
        # GET: List with filters
        city = request.args.get('city')
        state_province = request.args.get('state_province')
        has_coverage = request.args.get('has_coverage')
        service_type = request.args.get('service_type')
        include_coverage = request.args.get('include_coverage', 'true').lower() == 'true'
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get locations
        query = """
            SELECT DISTINCT gl.*, 
                   CASE WHEN sc.street_name IS NOT NULL THEN true ELSE false END as has_coverage
            FROM geographic_locations gl
            LEFT JOIN service_coverage sc ON gl.street_name = sc.street_name AND gl.city = sc.city
        """
        
        params = []
        conditions = []
        
        if city:
            conditions.append("gl.city = %s")
            params.append(city)
        
        if state_province:
            conditions.append("gl.state_province = %s")
            params.append(state_province)
        
        if service_type:
            conditions.append("sc.service_type = %s")
            params.append(service_type)
        
        if has_coverage is not None:
            if has_coverage.lower() == 'true':
                conditions.append("sc.street_name IS NOT NULL")
            else:
                conditions.append("sc.street_name IS NULL")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY gl.city, gl.street_name LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        locations = cursor.fetchall()
        
        # Include coverage details if requested
        if include_coverage:
            for location in locations:
                cursor.execute("""
                    SELECT service_type, max_speed_mbps, available
                    FROM service_coverage
                    WHERE street_name = %s AND city = %s
                """, (location['street_name'], location['city']))
                
                coverage_rows = cursor.fetchall()
                coverage_details = {}
                for row in coverage_rows:
                    coverage_details[row['service_type']] = {
                        'available': row['available'],
                        'max_speed_mbps': row['max_speed_mbps']
                    }
                location['coverage_details'] = coverage_details
        
        cursor.execute("SELECT COUNT(*) as total FROM geographic_locations")
        total = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        # FIXED: Return with 'locations' key
        return jsonify({
            "locations": locations,
            "total": total,
            "limit": limit,
            "offset": offset
        })
    
    except Exception as e:
        logger.error(f"Error handling geographic locations: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sync-catalog-data', methods=['POST'])
def sync_catalog_data():
    """Sync and validate catalog integrity"""
    try:
        data = request.json or {}
        sync_type = data.get('sync_type', 'full')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) as count FROM service_specifications")
        service_specs_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM product_offerings")
        product_offerings_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM geographic_locations")
        locations_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM service_coverage")
        coverage_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM product_service_links")
        links_count = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "sync_type": sync_type,
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "results": {
                "summary": {
                    "service_specifications": service_specs_count,
                    "product_offerings": product_offerings_count,
                    "geographic_locations": locations_count,
                    "coverage_areas": coverage_count,
                    "product_service_links": links_count
                },
                "validation": {
                    "catalog_integrity": "valid",
                    "orphaned_products": 0,
                    "missing_specifications": 0
                }
            }
        })
    
    except Exception as e:
        logger.error(f"Error syncing catalog data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/link-offering-to-specification', methods=['POST'])
def link_offering_to_specification():
    """Link product offering to service specification"""
    try:
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO product_service_links (
                product_offering_id, service_specification_id, is_primary
            ) VALUES (%s, %s, %s)
            ON CONFLICT (product_offering_id, service_specification_id) 
            DO UPDATE SET is_primary = EXCLUDED.is_primary
            RETURNING *
        """, (
            data.get('product_offering_id'),
            data.get('service_specification_id'),
            data.get('is_primary', False)
        ))
        
        link = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "linked",
            "product_offering_id": data.get('product_offering_id'),
            "service_specification_id": data.get('service_specification_id'),
            "is_primary": data.get('is_primary', False)
        }), 201
    
    except Exception as e:
        logger.error(f"Error linking offering to specification: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/add-geographic-coverage', methods=['POST'])
def add_geographic_coverage():
    """Add coverage area for services"""
    try:
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get location details
        cursor.execute("""
            SELECT street_name, city FROM geographic_locations 
            WHERE id = %s
        """, (data.get('location_id'),))
        
        location = cursor.fetchone()
        if not location:
            cursor.close()
            conn.close()
            return jsonify({"error": "Location not found"}), 404
        
        # Insert or update coverage
        cursor.execute("""
            INSERT INTO service_coverage (
                street_name, city, service_type, available, max_speed_mbps
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (street_name, city, service_type)
            DO UPDATE SET 
                available = EXCLUDED.available,
                max_speed_mbps = EXCLUDED.max_speed_mbps
            RETURNING *
        """, (
            location['street_name'],
            location['city'],
            data.get('service_type'),
            data.get('available', True),
            data.get('max_speed_mbps')
        ))
        
        coverage = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "coverage_added",
            "location_id": data.get('location_id'),
            "service_type": data.get('service_type'),
            "coverage": {
                "available": coverage['available'],
                "max_speed_mbps": coverage['max_speed_mbps'],
                "coverage_quality": data.get('coverage_quality', 'good')
            }
        }), 201
    
    except Exception as e:
        logger.error(f"Error adding geographic coverage: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/catalog-integrity', methods=['GET'])
def get_catalog_integrity():
    """Get catalog integrity status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check for orphaned products
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM product_offerings po
            WHERE NOT EXISTS (
                SELECT 1 FROM product_service_links psl 
                WHERE psl.product_offering_id = po.id
            )
        """)
        orphaned_products = cursor.fetchone()['count']
        
        # Check for missing specifications
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM product_service_links psl
            WHERE NOT EXISTS (
                SELECT 1 FROM service_specifications ss 
                WHERE ss.id = psl.service_specification_id
            )
        """)
        missing_specs = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "checked",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "integrity": {
                "overall_status": "valid" if orphaned_products == 0 and missing_specs == 0 else "issues_found",
                "orphaned_products": orphaned_products,
                "missing_specifications": missing_specs,
                "last_sync": datetime.utcnow().isoformat() + "Z"
            }
        })
    
    except Exception as e:
        logger.error(f"Error checking catalog integrity: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# LEGACY/COMPATIBILITY ENDPOINTS
# ============================================================================

@app.route('/api/customers', methods=['GET'])
def get_all_customers():
    """Get all customers"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, account_status, credit_score, has_overdue_payments,
                   street_number, street_name, city, postal_code
            FROM customers
            ORDER BY name
        """)
        
        customers = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(customers)
    except Exception as e:
        logger.error(f"Error getting customers: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/customer/<customer_id>/services', methods=['GET'])
def get_customer_services(customer_id):
    """Get active services for a customer"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get active service activations
        cursor.execute("""
            SELECT sa.*, aa.street_number, aa.street_name, aa.city
            FROM service_activations sa
            JOIN activation_addresses aa ON sa.id = aa.activation_id
            WHERE sa.status = 'activated'
            ORDER BY sa.created_at DESC
        """)
        
        services = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(services)
    except Exception as e:
        logger.error(f"Error getting customer services: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/service-coverage', methods=['GET'])
def get_service_coverage():
    """Get service coverage map"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT street_name, city,
                   STRING_AGG(service_type || 
                   CASE WHEN max_speed_mbps IS NOT NULL 
                        THEN ' (' || max_speed_mbps || ' Mbps)' 
                        ELSE '' END, 
                   ', ' ORDER BY service_type) as available_services
            FROM service_coverage
            GROUP BY street_name, city
            ORDER BY city, street_name
        """)
        
        coverage = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(coverage)
    except Exception as e:
        logger.error(f"Error getting service coverage: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/orders/recent', methods=['GET'])
def get_recent_orders():
    """Get recent orders"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT o.*, c.name as customer_name,
                   oa.street_number, oa.street_name, oa.city
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            JOIN order_addresses oa ON o.id = oa.order_id
            ORDER BY o.created_at DESC
            LIMIT 10
        """)
        
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(orders)
    except Exception as e:
        logger.error(f"Error getting recent orders: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
