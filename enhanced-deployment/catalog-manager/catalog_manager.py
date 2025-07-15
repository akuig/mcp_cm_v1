#!/usr/bin/env python3
"""
Catalog Manager API - TMF Forum API Implementation
Supports TMF620, TMF629, TMF633, TMF637, TMF640, TMF673
"""

import os
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify, g
import mysql.connector
from mysql.connector import Error
import redis
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'mysql'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'catalog_user'),
    'password': os.getenv('DB_PASSWORD', 'catalog_pass'),
    'database': os.getenv('DB_NAME', 'telepath_catalog'),
    'charset': 'utf8mb4',
    'autocommit': True
}

REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'redis'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': int(os.getenv('REDIS_DB', 0))
}

# Global connections
redis_client = None

def get_db_connection():
    """Get database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Database connection error: {e}")
        raise InternalServerError("Database connection failed")

def get_redis_client():
    """Get Redis client for caching"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.Redis(**REDIS_CONFIG)
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            redis_client = None
    return redis_client

def generate_id(prefix: str = "") -> str:
    """Generate unique ID"""
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"

def log_audit(action: str, resource_type: str, resource_id: str, details: Dict = None):
    """Log audit trail"""
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "resourceType": resource_type,
        "resourceId": resource_id,
        "details": details or {}
    }
    logger.info(f"Audit: {json.dumps(audit_entry)}")

# ===== TMF633 - Service Catalog Management =====

@app.route('/tmf633/serviceSpecification', methods=['GET'])
def list_service_specifications():
    """List service specifications with optional filtering"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Build query with filters
        query = """
        SELECT ss.*, 
               GROUP_CONCAT(
                   JSON_OBJECT(
                       'id', ssc.id,
                       'name', ssc.name, 
                       'valueType', ssc.value_type,
                       'defaultValue', ssc.default_value,
                       'isConfigurable', ssc.is_configurable
                   )
               ) as characteristics
        FROM service_specifications ss
        LEFT JOIN service_spec_characteristics ssc ON ss.id = ssc.service_spec_id
        WHERE ss.status = 'active'
        """
        
        params = []
        
        # Add filters
        if request.args.get('category'):
            query += " AND ss.category = %s"
            params.append(request.args.get('category'))
        
        query += " GROUP BY ss.id ORDER BY ss.name"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Process characteristics
        for result in results:
            if result['characteristics']:
                try:
                    result['characteristics'] = json.loads(f"[{result['characteristics']}]")
                except:
                    result['characteristics'] = []
            else:
                result['characteristics'] = []
        
        cursor.close()
        connection.close()
        
        log_audit("LIST", "ServiceSpecification", "all", {"count": len(results)})
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error listing service specifications: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/tmf633/serviceSpecification', methods=['POST'])
def create_service_specification():
    """Create new service specification"""
    try:
        data = request.get_json()
        spec_id = generate_id("SS_")
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Insert service specification
        insert_query = """
        INSERT INTO service_specifications (id, name, description, category, service_type, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            spec_id,
            data.get('name'),
            data.get('description'),
            data.get('category'),
            data.get('serviceType'),
            'active'
        ))
        
        # Insert characteristics
        if data.get('characteristics'):
            for char in data['characteristics']:
                char_id = generate_id("CHR_")
                char_query = """
                INSERT INTO service_spec_characteristics 
                (id, service_spec_id, name, value_type, default_value, is_configurable)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(char_query, (
                    char_id,
                    spec_id,
                    char.get('name'),
                    char.get('valueType'),
                    char.get('defaultValue'),
                    char.get('isConfigurable', True)
                ))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        result = {"id": spec_id, **data, "status": "active"}
        log_audit("CREATE", "ServiceSpecification", spec_id, data)
        return jsonify(result), 201
        
    except Exception as e:
        logger.error(f"Error creating service specification: {e}")
        return jsonify({"error": str(e)}), 500

# ===== TMF620 - Product Catalog Management =====

@app.route('/tmf620/productOffering', methods=['GET'])
def list_product_offerings():
    """List product offerings with optional filtering"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT po.*,
               GROUP_CONCAT(ss.id) as service_specification_ids,
               GROUP_CONCAT(ss.name) as service_specification_names
        FROM product_offerings po
        LEFT JOIN offering_service_mappings osm ON po.id = osm.product_offering_id
        LEFT JOIN service_specifications ss ON osm.service_spec_id = ss.id
        WHERE po.status = 'active'
        """
        
        params = []
        
        # Add filters
        if request.args.get('category'):
            query += " AND po.category = %s"
            params.append(request.args.get('category'))
            
        if request.args.get('isBundle') is not None:
            is_bundle = request.args.get('isBundle').lower() == 'true'
            query += " AND po.is_bundle = %s"
            params.append(is_bundle)
        
        query += " GROUP BY po.id ORDER BY po.name"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Process results
        for result in results:
            # Format price
            if result['price_amount']:
                result['price'] = {
                    "amount": float(result['price_amount']),
                    "currency": result['price_currency'],
                    "period": result['price_period']
                }
            
            # Format service specifications
            if result['service_specification_ids']:
                spec_ids = result['service_specification_ids'].split(',')
                spec_names = result['service_specification_names'].split(',')
                result['serviceSpecifications'] = [
                    {"id": sid, "name": sname} 
                    for sid, sname in zip(spec_ids, spec_names)
                ]
            else:
                result['serviceSpecifications'] = []
            
            # Remove internal fields
            for field in ['price_amount', 'price_currency', 'price_period', 
                         'service_specification_ids', 'service_specification_names']:
                result.pop(field, None)
        
        cursor.close()
        connection.close()
        
        log_audit("LIST", "ProductOffering", "all", {"count": len(results)})
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error listing product offerings: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/tmf620/productOffering', methods=['POST'])
def create_product_offering():
    """Create new product offering"""
    try:
        data = request.get_json()
        offering_id = generate_id("PO_")
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Extract price information
        price = data.get('price', {})
        
        # Insert product offering
        insert_query = """
        INSERT INTO product_offerings 
        (id, name, description, category, is_bundle, status, price_amount, price_currency, price_period)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            offering_id,
            data.get('name'),
            data.get('description'),
            data.get('category'),
            data.get('isBundle', False),
            'active',
            price.get('amount'),
            price.get('currency', 'USD'),
            price.get('period', 'monthly')
        ))
        
        # Link to service specifications
        if data.get('productSpecificationIds'):
            for spec_id in data['productSpecificationIds']:
                mapping_id = generate_id("MAP_")
                mapping_query = """
                INSERT INTO offering_service_mappings (id, product_offering_id, service_spec_id)
                VALUES (%s, %s, %s)
                """
                cursor.execute(mapping_query, (mapping_id, offering_id, spec_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        result = {"id": offering_id, **data, "status": "active"}
        log_audit("CREATE", "ProductOffering", offering_id, data)
        return jsonify(result), 201
        
    except Exception as e:
        logger.error(f"Error creating product offering: {e}")
        return jsonify({"error": str(e)}), 500

# ===== TMF673 - Geographic Address Management =====

@app.route('/tmf673/geographicLocation', methods=['GET'])
def list_geographic_locations():
    """List geographic locations with service coverage"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT gl.*,
               GROUP_CONCAT(
                   JSON_OBJECT(
                       'serviceSpecId', ss.id,
                       'serviceSpecName', ss.name,
                       'serviceType', ss.service_type,
                       'coverageType', sc.coverage_type,
                       'installationType', sc.installation_type
                   )
               ) as service_coverage
        FROM geographic_locations gl
        LEFT JOIN service_coverage sc ON gl.id = sc.location_id
        LEFT JOIN service_specifications ss ON sc.service_spec_id = ss.id
        WHERE 1=1
        """
        
        params = []
        
        # Add filters
        if request.args.get('city'):
            query += " AND gl.city = %s"
            params.append(request.args.get('city'))
            
        if request.args.get('serviceType'):
            query += " AND ss.service_type = %s"
            params.append(request.args.get('serviceType'))
        
        query += " GROUP BY gl.id ORDER BY gl.city, gl.street_name, gl.street_number"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Process service coverage
        for result in results:
            if result['service_coverage']:
                try:
                    result['serviceCoverage'] = json.loads(f"[{result['service_coverage']}]")
                except:
                    result['serviceCoverage'] = []
            else:
                result['serviceCoverage'] = []
            result.pop('service_coverage', None)
        
        cursor.close()
        connection.close()
        
        log_audit("LIST", "GeographicLocation", "all", {"count": len(results)})
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error listing geographic locations: {e}")
        return jsonify({"error": str(e)}), 500

# ===== TMF637 - Service Qualification (Enhanced) =====

@app.route('/tmf637/serviceQualification', methods=['POST'])
def service_qualification():
    """Enhanced service qualification with proper availability checking"""
    try:
        data = request.get_json()
        address = data.get('address', {})
        service_spec = data.get('serviceSpecification', {})
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Find matching location
        location_query = """
        SELECT * FROM geographic_locations 
        WHERE street_name = %s AND street_number = %s AND city = %s
        """
        
        cursor.execute(location_query, (
            address.get('streetName'),
            address.get('streetNumber'),
            address.get('city')
        ))
        
        location = cursor.fetchone()
        
        if not location:
            return jsonify({
                "serviceQualificationItem": [{
                    "productOffering": service_spec,
                    "qualificationResult": "unqualified",
                    "reason": "Address not found in service area"
                }]
            })
        
        # Check service availability at location
        coverage_query = """
        SELECT sc.*, ss.name as service_name, ss.service_type
        FROM service_coverage sc
        JOIN service_specifications ss ON sc.service_spec_id = ss.id
        WHERE sc.location_id = %s AND ss.id = %s AND ss.status = 'active'
        """
        
        cursor.execute(coverage_query, (location['id'], service_spec.get('id')))
        coverage = cursor.fetchone()
        
        if not coverage:
            return jsonify({
                "serviceQualificationItem": [{
                    "productOffering": service_spec,
                    "qualificationResult": "unqualified",
                    "reason": "Service not available at this location"
                }]
            })
        
        # Get available product offerings for this service
        offerings_query = """
        SELECT po.*, osm.service_spec_id
        FROM product_offerings po
        JOIN offering_service_mappings osm ON po.id = osm.product_offering_id
        WHERE osm.service_spec_id = %s AND po.status = 'active'
        """
        
        cursor.execute(offerings_query, (service_spec.get('id'),))
        offerings = cursor.fetchall()
        
        available_offerings = []
        for offering in offerings:
            available_offerings.append({
                "id": offering['id'],
                "name": offering['name'],
                "description": offering['description'],
                "price": {
                    "amount": float(offering['price_amount']) if offering['price_amount'] else None,
                    "currency": offering['price_currency'],
                    "period": offering['price_period']
                }
            })
        
        cursor.close()
        connection.close()
        
        result = {
            "serviceQualificationItem": [{
                "productOffering": service_spec,
                "qualificationResult": "qualified",
                "reason": f"Service available with {coverage['coverage_type']} coverage",
                "installationType": coverage['installation_type'],
                "availableProductOfferings": available_offerings
            }]
        }
        
        log_audit("QUALIFY", "Service", service_spec.get('id'), {
            "address": address,
            "result": "qualified"
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in service qualification: {e}")
        return jsonify({"error": str(e)}), 500

# ===== TMF629 - Customer Management =====

@app.route('/tmf629/customer/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get customer information"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM customers WHERE id = %s"
        cursor.execute(query, (customer_id,))
        customer = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        # Format address
        customer['address'] = {
            "streetName": customer['street_name'],
            "streetNumber": customer['street_number'], 
            "city": customer['city'],
            "postalCode": customer['postal_code'],
            "state": customer['state'],
            "country": customer['country']
        }
        
        # Remove internal fields
        for field in ['street_name', 'street_number', 'postal_code', 'created_at', 'updated_at']:
            customer.pop(field, None)
        
        log_audit("GET", "Customer", customer_id)
        return jsonify(customer)
        
    except Exception as e:
        logger.error(f"Error getting customer: {e}")
        return jsonify({"error": str(e)}), 500

# ===== TMF622 - Product Ordering =====

@app.route('/tmf622/productOrder', methods=['POST'])
def create_product_order():
    """Create product order"""
    try:
        data = request.get_json()
        order_id = generate_id("ORD_")
        
        # For demo purposes, just return success
        # In real implementation, would integrate with ordering system
        
        result = {
            "id": order_id,
            "orderDate": data.get('orderDate'),
            "externalId": data.get('externalId'),
            "state": "acknowledged",
            "relatedParty": data.get('relatedParty', []),
            "orderItem": data.get('orderItem', [])
        }
        
        log_audit("CREATE", "ProductOrder", order_id, data)
        return jsonify(result), 201
        
    except Exception as e:
        logger.error(f"Error creating product order: {e}")
        return jsonify({"error": str(e)}), 500

# ===== TMF640 - Service Activation =====

@app.route('/tmf640/serviceActivation', methods=['POST'])
def activate_service():
    """Activate service"""
    try:
        data = request.get_json()
        activation_id = generate_id("ACT_")
        
        # For demo purposes, just return success
        # In real implementation, would integrate with network activation systems
        
        result = {
            "id": activation_id,
            "state": "completed",
            "service": data.get('service', {}),
            "activationDate": datetime.utcnow().isoformat() + "Z"
        }
        
        log_audit("ACTIVATE", "Service", activation_id, data)
        return jsonify(result), 201
        
    except Exception as e:
        logger.error(f"Error activating service: {e}")
        return jsonify({"error": str(e)}), 500

# ===== Administrative Endpoints =====

@app.route('/admin/syncCatalog', methods=['POST'])
def sync_catalog_data():
    """Synchronize and validate catalog data"""
    try:
        data = request.get_json()
        validate_only = data.get('validateOnly', True)
        fix_orphans = data.get('fixOrphans', False)
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        validation_results = {}
        fixes_applied = []
        recommendations = []
        
        # Check for orphaned service specifications
        cursor.execute("""
            SELECT COUNT(*) as count FROM service_specifications ss
            LEFT JOIN offering_service_mappings osm ON ss.id = osm.service_spec_id
            WHERE osm.service_spec_id IS NULL AND ss.status = 'active'
        """)
        validation_results['orphanedServiceSpecs'] = cursor.fetchone()['count']
        
        # Check for orphaned product offerings
        cursor.execute("""
            SELECT COUNT(*) as count FROM product_offerings po
            LEFT JOIN offering_service_mappings osm ON po.id = osm.product_offering_id
            WHERE osm.product_offering_id IS NULL AND po.status = 'active'
        """)
        validation_results['orphanedProductOfferings'] = cursor.fetchone()['count']
        
        # Check for invalid coverage entries
        cursor.execute("""
            SELECT COUNT(*) as count FROM service_coverage sc
            LEFT JOIN service_specifications ss ON sc.service_spec_id = ss.id
            LEFT JOIN geographic_locations gl ON sc.location_id = gl.id
            WHERE ss.id IS NULL OR gl.id IS NULL
        """)
        validation_results['invalidCoverageEntries'] = cursor.fetchone()['count']
        
        # Check for duplicate locations
        cursor.execute("""
            SELECT COUNT(*) as count FROM (
                SELECT street_name, street_number, city, COUNT(*) as cnt
                FROM geographic_locations
                GROUP BY street_name, street_number, city
                HAVING cnt > 1
            ) as duplicates
        """)
        validation_results['duplicateLocations'] = cursor.fetchone()['count']
        
        # Generate recommendations
        if validation_results['orphanedServiceSpecs'] > 0:
            recommendations.append("Consider creating product offerings for unused service specifications")
            
        if validation_results['orphanedProductOfferings'] > 0:
            recommendations.append("Link product offerings to service specifications")
            
        # Apply fixes if requested
        if not validate_only and fix_orphans:
            if validation_results['invalidCoverageEntries'] > 0:
                cursor.execute("""
                    DELETE sc FROM service_coverage sc
                    LEFT JOIN service_specifications ss ON sc.service_spec_id = ss.id
                    LEFT JOIN geographic_locations gl ON sc.location_id = gl.id
                    WHERE ss.id IS NULL OR gl.id IS NULL
                """)
                fixes_applied.append("Removed invalid coverage entries")
            
            connection.commit()
        
        cursor.close()
        connection.close()
        
        result = {
            "status": "completed",
            "validationResults": validation_results,
            "fixesApplied": fixes_applied,
            "recommendations": recommendations
        }
        
        log_audit("SYNC", "Catalog", "all", result)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error syncing catalog: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/admin/linkOffering/<offering_id>', methods=['POST'])
def link_offering_to_specification(offering_id):
    """Link product offering to service specifications"""
    try:
        data = request.get_json()
        spec_ids = data.get('serviceSpecificationIds', [])
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Remove existing mappings
        cursor.execute("DELETE FROM offering_service_mappings WHERE product_offering_id = %s", (offering_id,))
        
        # Add new mappings
        for spec_id in spec_ids:
            mapping_id = generate_id("MAP_")
            cursor.execute("""
                INSERT INTO offering_service_mappings (id, product_offering_id, service_spec_id)
                VALUES (%s, %s, %s)
            """, (mapping_id, offering_id, spec_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        result = {"status": "success", "mappingsCreated": len(spec_ids)}
        log_audit("LINK", "ProductOffering", offering_id, data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error linking offering: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/admin/coverage/<spec_id>', methods=['POST'])
def add_geographic_coverage(spec_id):
    """Add geographic coverage for service specification"""
    try:
        data = request.get_json()
        locations = data.get('locations', [])
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        coverage_added = 0
        
        for location_data in locations:
            # Find or create location
            cursor.execute("""
                SELECT id FROM geographic_locations 
                WHERE street_name = %s AND street_number = %s AND city = %s
            """, (
                location_data.get('streetName'),
                location_data.get('streetNumber'),
                location_data.get('city')
            ))
            
            location = cursor.fetchone()
            
            if not location:
                # Create new location
                location_id = generate_id("LOC_")
                cursor.execute("""
                    INSERT INTO geographic_locations (id, street_name, street_number, city)
                    VALUES (%s, %s, %s, %s)
                """, (
                    location_id,
                    location_data.get('streetName'),
                    location_data.get('streetNumber'),
                    location_data.get('city')
                ))
            else:
                location_id = location[0]
            
            # Add coverage
            coverage_id = generate_id("COV_")
            cursor.execute("""
                INSERT IGNORE INTO service_coverage 
                (id, service_spec_id, location_id, coverage_type)
                VALUES (%s, %s, %s, %s)
            """, (
                coverage_id,
                spec_id,
                location_id,
                location_data.get('coverage', 'full')
            ))
            
            if cursor.rowcount > 0:
                coverage_added += 1
        
        connection.commit()
        cursor.close()
        connection.close()
        
        result = {"status": "success", "coverageEntriesAdded": coverage_added}
        log_audit("ADD_COVERAGE", "ServiceSpecification", spec_id, data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error adding coverage: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/admin/health', methods=['GET'])
def health_check():
    """Health check and database statistics"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get statistics
        stats = {}
        
        cursor.execute("SELECT COUNT(*) as count FROM service_specifications WHERE status = 'active'")
        stats['serviceSpecifications'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM product_offerings WHERE status = 'active'")
        stats['productOfferings'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM geographic_locations")
        stats['geographicLocations'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM service_coverage")
        stats['coverageEntries'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM customers WHERE account_status = 'active'")
        stats['activeCustomers'] = cursor.fetchone()['count']
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "statistics": stats
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy", 
            "database": "disconnected",
            "error": str(e)
        }), 500

# ===== Error Handlers =====

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request", "message": str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "message": str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "message": str(error)}), 500

# ===== Main =====

if __name__ == '__main__':
    # Wait for database to be ready
    import time
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = get_db_connection()
            conn.close()
            logger.info("Database connection successful")
            break
        except Exception as e:
            logger.warning(f"Database not ready, attempt {i+1}/{max_retries}: {e}")
            time.sleep(1)
    else:
        logger.error("Could not connect to database after maximum retries")
        exit(1)
    
    # Start the server
    app.run(host='0.0.0.0', port=8080, debug=True)