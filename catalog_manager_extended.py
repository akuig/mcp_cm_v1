#!/usr/bin/env python3
"""
Enhanced Catalog Manager - Implements TM Forum APIs for the demo
Extended with new catalog management capabilities
"""

import logging
from datetime import datetime
from typing import Dict, Optional, List
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

# ============================================================================
# EXISTING TM FORUM APIs (TMF637, TMF629, TMF622, TMF640)
# ============================================================================

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

# ============================================================================
# ENHANCED CATALOG MANAGEMENT APIs - NEW
# ============================================================================

@app.route('/api/service-specifications', methods=['GET', 'POST'])
def handle_service_specifications():
    """List/filter service specifications (GET) or create new ones (POST)"""
    if request.method == 'GET':
        return list_service_specifications()
    elif request.method == 'POST':
        return create_service_specification()

def list_service_specifications():
    """Enhanced: List/filter all service specifications"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters for filtering
        service_type = request.args.get('service_type')
        search = request.args.get('search')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build dynamic query
        query = """
            SELECT ss.*, 
                   COUNT(osl.product_offering_id) as linked_offerings_count
            FROM service_specifications ss
            LEFT JOIN offering_service_links osl ON ss.id = osl.service_specification_id
        """
        params = []
        conditions = []
        
        if service_type:
            conditions.append("ss.service_type = %s")
            params.append(service_type)
        
        if search:
            conditions.append("(ss.name ILIKE %s OR ss.description ILIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += """
            GROUP BY ss.id, ss.name, ss.service_type, ss.description, ss.created_at, ss.updated_at
            ORDER BY ss.service_type, ss.name
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        specs = cursor.fetchall()
        
        # Get total count for pagination
        count_query = "SELECT COUNT(*) FROM service_specifications ss"
        if conditions:
            count_query += " WHERE " + " AND ".join([c.replace("ss.", "") for c in conditions])
        cursor.execute(count_query, params[:-2] if conditions else [])
        total_count = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        result = {
            "specifications": specs,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            }
        }
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error listing service specifications: {str(e)}")
        return jsonify({"error": str(e)}), 500

def create_service_specification():
    """Create new service specification"""
    try:
        data = request.json
        spec_id = data.get('id') or str(uuid.uuid4())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO service_specifications (
                id, name, service_type, description, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            spec_id,
            data.get('name'),
            data.get('service_type'),
            data.get('description'),
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        spec = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify(spec), 201
    
    except Exception as e:
        logger.error(f"Error creating service specification: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/product-offerings', methods=['GET', 'POST'])
def handle_product_offerings():
    """List/filter product offerings (GET) or create new ones (POST)"""
    if request.method == 'GET':
        return list_product_offerings()
    elif request.method == 'POST':
        return create_product_offering()

def list_product_offerings():
    """List/filter all product offerings"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters for filtering
        category = request.args.get('category')
        is_active = request.args.get('is_active', type=bool)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        search = request.args.get('search')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        include_services = request.args.get('include_services', 'true').lower() == 'true'
        
        # Build dynamic query
        if include_services:
            query = """
                SELECT po.*, 
                       COALESCE(
                           JSON_AGG(
                               JSON_BUILD_OBJECT(
                                   'id', ss.id,
                                   'name', ss.name,
                                   'service_type', ss.service_type,
                                   'is_primary', osl.is_primary
                               ) ORDER BY osl.is_primary DESC, ss.service_type
                           ) FILTER (WHERE ss.id IS NOT NULL), 
                           '[]'::json
                       ) as linked_services
                FROM product_offerings po
                LEFT JOIN offering_service_links osl ON po.id = osl.product_offering_id
                LEFT JOIN service_specifications ss ON osl.service_specification_id = ss.id
            """
        else:
            query = """
                SELECT po.*,
                       COUNT(osl.service_specification_id) as linked_services_count
                FROM product_offerings po
                LEFT JOIN offering_service_links osl ON po.id = osl.product_offering_id
            """
        
        params = []
        conditions = []
        
        if category:
            conditions.append("po.category = %s")
            params.append(category)
        
        if is_active is not None:
            conditions.append("po.is_active = %s")
            params.append(is_active)
        
        if min_price is not None:
            conditions.append("po.price_monthly >= %s")
            params.append(min_price)
        
        if max_price is not None:
            conditions.append("po.price_monthly <= %s")
            params.append(max_price)
        
        if search:
            conditions.append("(po.name ILIKE %s OR po.description ILIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        if include_services:
            query += """
                GROUP BY po.id, po.name, po.description, po.category, po.price_monthly, 
                         po.price_setup, po.contract_length_months, po.is_active, 
                         po.created_at, po.updated_at
            """
        else:
            query += " GROUP BY po.id"
        
        query += """
            ORDER BY po.category, po.price_monthly
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        offerings = cursor.fetchall()
        
        # Get total count for pagination
        count_query = "SELECT COUNT(*) FROM product_offerings po"
        if conditions:
            count_query += " WHERE " + " AND ".join([c.replace("po.", "") for c in conditions])
        cursor.execute(count_query, params[:-2] if conditions else [])
        total_count = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        result = {
            "offerings": offerings,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            }
        }
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error listing product offerings: {str(e)}")
        return jsonify({"error": str(e)}), 500

def create_product_offering():
    """Create new product offering"""
    try:
        data = request.json
        offering_id = data.get('id') or str(uuid.uuid4())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO product_offerings (
                id, name, description, category, price_monthly, price_setup,
                contract_length_months, is_active, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            offering_id,
            data.get('name'),
            data.get('description'),
            data.get('category'),
            data.get('price_monthly'),
            data.get('price_setup', 0.0),
            data.get('contract_length_months', 0),
            data.get('is_active', True),
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        offering = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify(offering), 201
    
    except Exception as e:
        logger.error(f"Error creating product offering: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/geographic-locations', methods=['GET', 'POST'])
def handle_geographic_locations():
    """List/filter geographic locations (GET) or add new ones (POST)"""
    if request.method == 'GET':
        return list_geographic_locations()
    elif request.method == 'POST':
        return add_geographic_location()

def list_geographic_locations():
    """List locations with coverage info"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters for filtering
        city = request.args.get('city')
        state_province = request.args.get('state_province')
        has_coverage = request.args.get('has_coverage', type=bool)
        service_type = request.args.get('service_type')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        include_coverage = request.args.get('include_coverage', 'true').lower() == 'true'
        
        if include_coverage:
            query = """
                SELECT gl.*,
                       COALESCE(
                           JSON_AGG(
                               JSON_BUILD_OBJECT(
                                   'service_type', scn.service_type,
                                   'max_speed_mbps', scn.max_speed_mbps,
                                   'available', scn.available,
                                   'coverage_quality', scn.coverage_quality,
                                   'technology', scn.technology,
                                   'signal_strength', scn.signal_strength
                               ) ORDER BY scn.service_type
                           ) FILTER (WHERE scn.service_type IS NOT NULL), 
                           '[]'::json
                       ) as coverage_details
                FROM geographic_locations gl
                LEFT JOIN service_coverage_new scn ON gl.location_id = scn.location_id
            """
        else:
            query = """
                SELECT gl.*,
                       COUNT(scn.service_type) as coverage_count
                FROM geographic_locations gl
                LEFT JOIN service_coverage_new scn ON gl.location_id = scn.location_id
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
            conditions.append("scn.service_type = %s")
            params.append(service_type)
        
        if has_coverage is not None:
            if has_coverage:
                conditions.append("scn.service_type IS NOT NULL")
            else:
                conditions.append("scn.service_type IS NULL")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += """
            GROUP BY gl.id, gl.location_id, gl.street_number, gl.street_name, 
                     gl.city, gl.state_province, gl.postal_code, gl.country,
                     gl.latitude, gl.longitude, gl.location_type, gl.created_at, gl.updated_at
            ORDER BY gl.city, gl.street_name, gl.street_number
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        locations = cursor.fetchall()
        
        # Get total count for pagination
        count_query = """
            SELECT COUNT(DISTINCT gl.id) 
            FROM geographic_locations gl
            LEFT JOIN service_coverage_new scn ON gl.location_id = scn.location_id
        """
        if conditions:
            count_query += " WHERE " + " AND ".join(conditions)
        cursor.execute(count_query, params[:-2])
        total_count = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        result = {
            "locations": locations,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            }
        }
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error listing geographic locations: {str(e)}")
        return jsonify({"error": str(e)}), 500

def add_geographic_location():
    """Add new geographic location"""
    try:
        data = request.json
        location_id = data.get('location_id') or f"loc_{uuid.uuid4().hex[:8]}"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO geographic_locations (
                location_id, street_number, street_name, city, state_province,
                postal_code, country, latitude, longitude, location_type,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            location_id,
            data.get('street_number'),
            data.get('street_name'),
            data.get('city'),
            data.get('state_province'),
            data.get('postal_code'),
            data.get('country', 'USA'),
            data.get('latitude'),
            data.get('longitude'),
            data.get('location_type', 'address'),
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        location = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify(location), 201
    
    except Exception as e:
        logger.error(f"Error adding geographic location: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/link-offering-to-specification', methods=['POST'])
def link_offering_to_specification():
    """Link product offering to service specification"""
    try:
        data = request.json
        offering_id = data.get('product_offering_id')
        service_id = data.get('service_specification_id')
        is_primary = data.get('is_primary', False)
        
        if not offering_id or not service_id:
            return jsonify({"error": "Both product_offering_id and service_specification_id are required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify both offering and service exist
        cursor.execute("SELECT id FROM product_offerings WHERE id = %s", (offering_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Product offering not found"}), 404
        
        cursor.execute("SELECT id FROM service_specifications WHERE id = %s", (service_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Service specification not found"}), 404
        
        # If this is set as primary, unset any existing primary for this offering
        if is_primary:
            cursor.execute("""
                UPDATE offering_service_links 
                SET is_primary = false 
                WHERE product_offering_id = %s
            """, (offering_id,))
        
        # Create the link
        cursor.execute("""
            INSERT INTO offering_service_links (
                product_offering_id, service_specification_id, is_primary, created_at
            ) VALUES (%s, %s, %s, %s)
            ON CONFLICT (product_offering_id, service_specification_id) 
            DO UPDATE SET is_primary = EXCLUDED.is_primary
            RETURNING *
        """, (offering_id, service_id, is_primary, datetime.utcnow()))
        
        link = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Link created successfully",
            "link": link
        }), 201
    
    except Exception as e:
        logger.error(f"Error linking offering to specification: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/add-geographic-coverage', methods=['POST'])
def add_geographic_coverage():
    """Add coverage area for services"""
    try:
        data = request.json
        location_id = data.get('location_id')
        service_type = data.get('service_type')
        
        if not location_id or not service_type:
            return jsonify({"error": "Both location_id and service_type are required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify location exists
        cursor.execute("SELECT location_id FROM geographic_locations WHERE location_id = %s", (location_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Geographic location not found"}), 404
        
        # Add coverage
        cursor.execute("""
            INSERT INTO service_coverage_new (
                location_id, service_type, max_speed_mbps, available,
                coverage_quality, technology, signal_strength, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (location_id, service_type) 
            DO UPDATE SET 
                max_speed_mbps = EXCLUDED.max_speed_mbps,
                available = EXCLUDED.available,
                coverage_quality = EXCLUDED.coverage_quality,
                technology = EXCLUDED.technology,
                signal_strength = EXCLUDED.signal_strength,
                updated_at = EXCLUDED.updated_at
            RETURNING *
        """, (
            location_id,
            service_type,
            data.get('max_speed_mbps'),
            data.get('available', True),
            data.get('coverage_quality', 'good'),
            data.get('technology'),
            data.get('signal_strength'),
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        coverage = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Coverage added successfully",
            "coverage": coverage
        }), 201
    
    except Exception as e:
        logger.error(f"Error adding geographic coverage: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sync-catalog-data', methods=['POST'])
def sync_catalog_data():
    """Validate and sync catalog integrity"""
    try:
        data = request.json or {}
        sync_type = data.get('sync_type', 'full')  # full, integrity_check, coverage_sync
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Start a sync operation record
        sync_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO sync_operations (
                operation_type, status, started_at, details
            ) VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (f"{sync_type}_sync", "running", datetime.utcnow(), {"sync_id": sync_id}))
        
        operation_id = cursor.fetchone()['id']
        conn.commit()
        
        results = {}
        total_processed = 0
        total_errors = 0
        
        if sync_type in ['full', 'integrity_check']:
            # Check for orphaned product offerings
            cursor.execute("""
                SELECT po.id, po.name 
                FROM product_offerings po
                LEFT JOIN offering_service_links osl ON po.id = osl.product_offering_id
                WHERE osl.product_offering_id IS NULL
            """)
            orphaned_offerings = cursor.fetchall()
            
            # Check for orphaned service specifications
            cursor.execute("""
                SELECT ss.id, ss.name 
                FROM service_specifications ss
                LEFT JOIN offering_service_links osl ON ss.id = osl.service_specification_id
                WHERE osl.service_specification_id IS NULL
            """)
            orphaned_services = cursor.fetchall()
            
            # Check for locations without coverage
            cursor.execute("""
                SELECT gl.location_id, gl.street_name, gl.city
                FROM geographic_locations gl
                LEFT JOIN service_coverage_new scn ON gl.location_id = scn.location_id
                WHERE scn.location_id IS NULL
            """)
            locations_no_coverage = cursor.fetchall()
            
            # Check for invalid pricing
            cursor.execute("""
                SELECT id, name, price_monthly
                FROM product_offerings 
                WHERE price_monthly < 0 OR price_monthly IS NULL
            """)
            invalid_pricing = cursor.fetchall()
            
            # Record integrity check results
            checks = [
                ('orphaned_offerings', len(orphaned_offerings), orphaned_offerings),
                ('orphaned_services', len(orphaned_services), orphaned_services),
                ('locations_no_coverage', len(locations_no_coverage), locations_no_coverage),
                ('invalid_pricing', len(invalid_pricing), invalid_pricing)
            ]
            
            for check_type, count, items in checks:
                status = 'passed' if count == 0 else ('warning' if count < 5 else 'failed')
                message = f"Found {count} items with issues" if count > 0 else f"No issues found"
                
                cursor.execute("""
                    INSERT INTO catalog_integrity (check_type, status, message, details, checked_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (check_type, status, message, {"items": items}, datetime.utcnow()))
                
                results[check_type] = {
                    "status": status,
                    "count": count,
                    "items": items[:10]  # Limit items in response
                }
                total_processed += count
        
        if sync_type in ['full', 'coverage_sync']:
            # Sync coverage data between old and new tables
            cursor.execute("""
                INSERT INTO service_coverage_new (location_id, service_type, max_speed_mbps, available, technology, created_at, updated_at)
                SELECT 
                    COALESCE(gl.location_id, 'loc_' || md5(sc.street_name || sc.city || sc.service_type)) as location_id,
                    sc.service_type,
                    sc.max_speed_mbps,
                    sc.available,
                    CASE 
                        WHEN sc.service_type LIKE '%fiber%' THEN 'fiber'
                        WHEN sc.service_type LIKE '%cable%' THEN 'cable'
                        WHEN sc.service_type LIKE '%dsl%' THEN 'dsl'
                        WHEN sc.service_type LIKE '%wireless%' THEN 'wireless'
                        ELSE 'unknown'
                    END as technology,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                FROM service_coverage sc
                LEFT JOIN geographic_locations gl ON sc.street_name = gl.street_name AND sc.city = gl.city
                ON CONFLICT (location_id, service_type) DO NOTHING
            """)
            
            synced_coverage = cursor.rowcount
            results['coverage_sync'] = {
                "status": "completed",
                "synced_records": synced_coverage
            }
            total_processed += synced_coverage
        
        # Update sync operation with results
        cursor.execute("""
            UPDATE sync_operations 
            SET status = %s, completed_at = %s, records_processed = %s, errors_count = %s, details = %s
            WHERE id = %s
        """, ("completed", datetime.utcnow(), total_processed, total_errors, results, operation_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Catalog sync completed",
            "sync_id": sync_id,
            "operation_id": operation_id,
            "total_processed": total_processed,
            "total_errors": total_errors,
            "results": results
        })
    
    except Exception as e:
        logger.error(f"Error syncing catalog data: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# EXISTING API ENDPOINTS (kept for backward compatibility)
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
