#!/usr/bin/env python3
"""
Catalog Manager - Implements TM Forum APIs for the demo
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
        
        # Check if we have fiber coverage at this location
        cursor.execute("""
            SELECT * FROM service_coverage 
            WHERE street_name = %s 
            AND city = %s 
            AND service_type = 'fiber'
        """, (address.get('streetName'), address.get('city')))
        
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

@app.route('/tmf622/productOrder', methods=['POST'])
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
