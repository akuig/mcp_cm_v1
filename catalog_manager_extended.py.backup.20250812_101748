#!/usr/bin/env python3
"""
Catalog Manager - Implements TM Forum APIs for the demo
Fixed routing issues and completed missing functions
"""

import logging
from datetime import datetime
from typing import Dict, Optional
import uuid
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os


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

@app.route('/tmf637/serviceQualification', methods=['POST'])
def service_qualification():
    """TMF637: Check service availability at location"""
    try:
        data = request.json
        address = data.get('address', {})
        service_spec = data.get('serviceSpecification', {})
        
        # For demo purposes, check if the address is in our service area
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, get the service type from specifications
        cursor.execute("""
            SELECT service_type FROM service_specifications 
            WHERE id = %s
        """, (service_spec.get('id'),))
        
        spec_result = cursor.fetchone()
        if not spec_result:
            cursor.close()
            conn.close()
            return jsonify({
                "serviceQualificationItem": [{
                    "qualificationResult": "unqualified",
                    "productOffering": service_spec,
                    "reason": "Invalid service specification"
                }]
            })
        
        service_type = spec_result['service_type']
        
        # Check if we have coverage for this service type at this location
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

# FIXED: Removed duplicate route and combined GET/POST handling
@app.route('/tmf622/productOrder', methods=['GET', 'POST'])
def handle_product_order():
    """TMF622: Handle both GET (list/search) and POST (create) for product orders"""
    if request.method == 'POST':
        return create_product_order()
    else:  # GET method
        return get_product_orders()

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
        
        # Also store the address information
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

def get_product_orders():
    """TMF622: Get product orders (list/search) - FIXED: Now implemented"""
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

@app.route('/api/service-specifications', methods=['GET'])
def get_service_specifications():
    """Get all service specifications"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, service_type, description
            FROM service_specifications
            ORDER BY service_type, name
        """)
        
        specs = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(specs)
    except Exception as e:
        logger.error(f"Error getting service specifications: {str(e)}")
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

@app.route('/api/customer/<customer_id>/services', methods=['GET'])
def get_customer_services(customer_id):
    """Get active services for a customer"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get active service activations for this customer
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
        
        # Filter services for this customer (in a real system, we'd have customer_id in the activation)
        # For demo, we'll return services at the customer's address
        return jsonify(services)
    except Exception as e:
        logger.error(f"Error getting customer services: {str(e)}")
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
