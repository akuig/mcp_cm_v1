#!/usr/bin/env python3
"""
Enhanced Catalog Manager with all API routes properly configured
This should be added to or replace the existing catalog manager routes
"""

from flask import Flask, request, jsonify
from typing import Dict, List, Optional
import json
import uuid
from datetime import datetime

app = Flask(__name__)

# In-memory storage for demo (replace with actual database)
service_specifications = []
product_offerings = []
geographic_locations = []
orders = []
coverage_data = []
product_service_links = []

# Initialize with sample data
def init_sample_data():
    """Initialize with sample catalog data"""
    global service_specifications, product_offerings, geographic_locations
    
    # Sample service specifications
    service_specifications = [
        {
            "id": "fiber-100",
            "name": "Fiber 100Mbps",
            "service_type": "fiber_internet",
            "description": "100Mbps fiber internet service",
            "characteristics": {"max_speed": "100", "technology": "fiber"}
        },
        {
            "id": "fiber-500",
            "name": "Fiber 500Mbps",
            "service_type": "fiber_internet",
            "description": "500Mbps fiber internet service",
            "characteristics": {"max_speed": "500", "technology": "fiber"}
        },
        {
            "id": "tv-basic",
            "name": "Basic TV Package",
            "service_type": "tv",
            "description": "Basic TV package with 50+ channels",
            "characteristics": {"channels": "50+", "hd": "true"}
        }
    ]
    
    # Sample product offerings
    product_offerings = [
        {
            "id": "offer-fiber-100",
            "name": "Fiber 100 Plan",
            "description": "100Mbps fiber internet plan",
            "category": "internet",
            "price_monthly": 49.99,
            "price_setup": 99.00,
            "contract_length_months": 12,
            "is_active": True,
            "linked_services": ["fiber-100"]
        },
        {
            "id": "offer-fiber-500",
            "name": "Fiber 500 Plan",
            "description": "500Mbps fiber internet plan",
            "category": "internet",
            "price_monthly": 79.99,
            "price_setup": 99.00,
            "contract_length_months": 12,
            "is_active": True,
            "linked_services": ["fiber-500"]
        },
        {
            "id": "offer-bundle-1",
            "name": "Internet + TV Bundle",
            "description": "100Mbps internet + Basic TV",
            "category": "bundle",
            "price_monthly": 89.99,
            "price_setup": 149.00,
            "contract_length_months": 24,
            "is_active": True,
            "linked_services": ["fiber-100", "tv-basic"]
        }
    ]
    
    # Sample geographic locations
    geographic_locations = [
        {
            "id": "loc-001",
            "streetName": "Main Street",
            "streetNumber": "100-200",
            "city": "Dublin",
            "state_province": "Leinster",
            "country": "IE",
            "has_coverage": True,
            "coverage_details": {
                "fiber_internet": {"available": True, "max_speed_mbps": 500, "technology": "fiber"},
                "tv": {"available": True, "technology": "cable"},
                "mobile": {"available": True, "technology": "5G", "signal_strength": 4}
            }
        },
        {
            "id": "loc-002",
            "streetName": "Oak Avenue",
            "streetNumber": "1-50",
            "city": "Cork",
            "state_province": "Munster",
            "country": "IE",
            "has_coverage": True,
            "coverage_details": {
                "fiber_internet": {"available": True, "max_speed_mbps": 100, "technology": "fiber"},
                "tv": {"available": False},
                "mobile": {"available": True, "technology": "4G", "signal_strength": 3}
            }
        }
    ]

# Core TMF Endpoints (existing functionality)
@app.route('/tmf637/serviceQualification', methods=['POST'])
def service_qualification():
    """TMF637: Service Qualification"""
    data = request.json
    address = data.get('address', {})
    service_spec = data.get('serviceSpecification', {})
    
    # Check if location has coverage
    for loc in geographic_locations:
        if loc['city'].lower() == address.get('city', '').lower():
            service_type = next((s['service_type'] for s in service_specifications 
                                if s['id'] == service_spec.get('id')), None)
            
            if service_type and service_type in loc.get('coverage_details', {}):
                coverage = loc['coverage_details'][service_type]
                return jsonify({
                    "id": str(uuid.uuid4()),
                    "qualificationResult": "qualified" if coverage.get('available') else "unqualified",
                    "serviceAvailable": coverage.get('available', False),
                    "estimatedProvisioningDate": "2025-01-15T10:00:00Z",
                    "serviceSpecification": service_spec,
                    "address": address
                })
    
    return jsonify({
        "id": str(uuid.uuid4()),
        "qualificationResult": "unqualified",
        "serviceAvailable": False,
        "serviceSpecification": service_spec,
        "address": address
    })

@app.route('/tmf629/customer/<customer_id>', methods=['GET'])
def customer_management(customer_id):
    """TMF629: Customer Management"""
    # Mock customer data
    return jsonify({
        "id": customer_id,
        "name": f"Customer {customer_id}",
        "status": "active",
        "customerType": "residential",
        "validFor": {
            "startDateTime": "2020-01-01T00:00:00Z"
        },
        "contactMedium": [
            {
                "type": "email",
                "preferred": True,
                "characteristic": {
                    "emailAddress": f"{customer_id}@example.com"
                }
            }
        ]
    })

@app.route('/tmf622/productOrder', methods=['POST', 'GET'])
def product_order():
    """TMF622: Product Ordering"""
    if request.method == 'POST':
        data = request.json
        order = {
            "id": str(uuid.uuid4()),
            "orderDate": data.get('orderDate'),
            "externalId": data.get('externalId'),
            "state": "acknowledged",
            "relatedParty": data.get('relatedParty', []),
            "orderItem": data.get('orderItem', [])
        }
        orders.append(order)
        return jsonify(order), 201
    
    # GET: List orders
    customer_id = request.args.get('customerId')
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    
    filtered_orders = orders
    if customer_id:
        filtered_orders = [o for o in orders 
                          if any(p.get('id') == customer_id for p in o.get('relatedParty', []))]
    
    return jsonify({
        "orders": filtered_orders[offset:offset+limit],
        "total": len(filtered_orders)
    })

@app.route('/tmf640/serviceActivation', methods=['POST'])
def service_activation():
    """TMF640: Service Activation"""
    data = request.json
    return jsonify({
        "id": str(uuid.uuid4()),
        "service": data.get('service'),
        "state": "active",
        "activationDate": datetime.utcnow().isoformat() + "Z"
    })

# Enhanced Catalog Endpoints
@app.route('/api/service-specifications', methods=['GET', 'POST'])
@app.route('/tmf633/serviceSpecification', methods=['GET', 'POST'])
def handle_service_specifications():
    """List or create service specifications"""
    if request.method == 'POST':
        data = request.json
        spec = {
            "id": data.get('id', str(uuid.uuid4())),
            "name": data.get('name'),
            "service_type": data.get('service_type'),
            "description": data.get('description'),
            "characteristics": data.get('characteristics', {})
        }
        service_specifications.append(spec)
        return jsonify(spec), 201
    
    # GET: List with filters
    service_type = request.args.get('service_type')
    search = request.args.get('search', '').lower()
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    filtered = service_specifications
    
    if service_type:
        filtered = [s for s in filtered if s['service_type'] == service_type]
    
    if search:
        filtered = [s for s in filtered 
                   if search in s['name'].lower() or search in s['description'].lower()]
    
    return jsonify({
        "serviceSpecifications": filtered[offset:offset+limit],
        "total": len(filtered)
    })

@app.route('/api/product-offerings', methods=['GET', 'POST'])
@app.route('/tmf620/productOffering', methods=['GET', 'POST'])
def handle_product_offerings():
    """List or create product offerings"""
    if request.method == 'POST':
        data = request.json
        offering = {
            "id": data.get('id', str(uuid.uuid4())),
            "name": data.get('name'),
            "description": data.get('description'),
            "category": data.get('category'),
            "price_monthly": data.get('price_monthly'),
            "price_setup": data.get('price_setup', 0),
            "contract_length_months": data.get('contract_length_months', 0),
            "is_active": data.get('is_active', True),
            "linked_services": []
        }
        product_offerings.append(offering)
        return jsonify(offering), 201
    
    # GET: List with filters
    category = request.args.get('category')
    is_active = request.args.get('is_active')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    search = request.args.get('search', '').lower()
    include_services = request.args.get('include_services', 'true').lower() == 'true'
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    filtered = product_offerings
    
    if category:
        filtered = [p for p in filtered if p['category'] == category]
    
    if is_active is not None:
        active = is_active.lower() == 'true'
        filtered = [p for p in filtered if p['is_active'] == active]
    
    if min_price is not None:
        filtered = [p for p in filtered if p['price_monthly'] >= min_price]
    
    if max_price is not None:
        filtered = [p for p in filtered if p['price_monthly'] <= max_price]
    
    if search:
        filtered = [p for p in filtered 
                   if search in p['name'].lower() or search in p['description'].lower()]
    
    # Include linked services if requested
    if include_services:
        for offering in filtered:
            offering['services'] = [s for s in service_specifications 
                                   if s['id'] in offering.get('linked_services', [])]
    
    return jsonify({
        "productOfferings": filtered[offset:offset+limit],
        "total": len(filtered)
    })

@app.route('/api/geographic-locations', methods=['GET'])
@app.route('/tmf673/geographicLocation', methods=['GET'])
def handle_geographic_locations():
    """List geographic locations with coverage"""
    city = request.args.get('city')
    state_province = request.args.get('state_province')
    has_coverage = request.args.get('has_coverage')
    service_type = request.args.get('service_type')
    include_coverage = request.args.get('include_coverage', 'true').lower() == 'true'
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    filtered = geographic_locations
    
    if city:
        filtered = [l for l in filtered if l['city'].lower() == city.lower()]
    
    if state_province:
        filtered = [l for l in filtered if l['state_province'].lower() == state_province.lower()]
    
    if has_coverage is not None:
        coverage = has_coverage.lower() == 'true'
        filtered = [l for l in filtered if l['has_coverage'] == coverage]
    
    if service_type:
        filtered = [l for l in filtered 
                   if service_type in l.get('coverage_details', {}) 
                   and l['coverage_details'][service_type].get('available')]
    
    if not include_coverage:
        # Remove coverage details if not requested
        filtered = [{k: v for k, v in l.items() if k != 'coverage_details'} 
                   for l in filtered]
    
    return jsonify({
        "geographicLocations": filtered[offset:offset+limit],
        "total": len(filtered)
    })

@app.route('/api/orders', methods=['GET'])
@app.route('/api/product-orders', methods=['GET'])
def handle_orders():
    """List orders (alias for TMF622)"""
    return product_order()

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get specific order"""
    order = next((o for o in orders if o['id'] == order_id), None)
    if order:
        return jsonify(order)
    return jsonify({"error": "Order not found"}), 404

@app.route('/api/sync', methods=['POST'])
@app.route('/api/catalog/sync', methods=['POST'])
def sync_catalog():
    """Sync catalog data"""
    data = request.json or {}
    sync_type = data.get('type', 'full')
    
    return jsonify({
        "sync_type": sync_type,
        "status": "success",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "statistics": {
            "service_specifications": len(service_specifications),
            "product_offerings": len(product_offerings),
            "geographic_locations": len(geographic_locations),
            "orders": len(orders)
        }
    })

@app.route('/api/product-offerings/<offering_id>/link-service', methods=['POST'])
def link_service_to_offering(offering_id):
    """Link service specification to product offering"""
    data = request.json
    service_id = data.get('service_specification_id')
    
    offering = next((p for p in product_offerings if p['id'] == offering_id), None)
    if not offering:
        return jsonify({"error": "Product offering not found"}), 404
    
    if service_id not in offering.get('linked_services', []):
        offering.setdefault('linked_services', []).append(service_id)
    
    return jsonify({
        "product_offering_id": offering_id,
        "service_specification_id": service_id,
        "status": "linked"
    })

@app.route('/api/geographic-locations/<location_id>/coverage', methods=['POST'])
def add_coverage(location_id):
    """Add coverage to geographic location"""
    data = request.json
    
    location = next((l for l in geographic_locations if l['id'] == location_id), None)
    if not location:
        return jsonify({"error": "Location not found"}), 404
    
    service_type = data.get('service_type')
    coverage_info = {
        "available": data.get('available', True),
        "max_speed_mbps": data.get('max_speed_mbps'),
        "technology": data.get('technology'),
        "signal_strength": data.get('signal_strength'),
        "coverage_quality": data.get('coverage_quality', 'good')
    }
    
    location.setdefault('coverage_details', {})[service_type] = coverage_info
    location['has_coverage'] = True
    
    return jsonify({
        "location_id": location_id,
        "service_type": service_type,
        "coverage": coverage_info
    })

# Health and info endpoints
@app.route('/', methods=['GET'])
@app.route('/api', methods=['GET'])
def api_info():
    """API information"""
    return jsonify({
        "name": "Telepath Catalog Manager",
        "version": "2.0.0",
        "endpoints": {
            "core_tmf": [
                "/tmf637/serviceQualification",
                "/tmf629/customer/{id}",
                "/tmf622/productOrder",
                "/tmf640/serviceActivation"
            ],
            "enhanced_catalog": [
                "/api/service-specifications",
                "/api/product-offerings",
                "/api/geographic-locations",
                "/api/orders",
                "/api/sync"
            ]
        }
    })

@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

if __name__ == '__main__':
    init_sample_data()
    app.run(host='0.0.0.0', port=8080, debug=True)
