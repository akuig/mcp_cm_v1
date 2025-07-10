#!/usr/bin/env python3
"""
Fault Manager - Implements TMF656 Service Problem Management APIs
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
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
    return jsonify({"status": "healthy", "service": "fault-manager"})

@app.route('/tmf656/serviceProblem', methods=['POST'])
def create_service_problem():
    """TMF656: Create a new service problem (customer reported issue)"""
    try:
        data = request.json
        problem_id = str(uuid.uuid4())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO service_problems (
                id, description, category, priority, status,
                affected_service, affected_location, reported_by,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            problem_id,
            data.get('description'),
            data.get('category', 'service_degradation'),
            data.get('priority', 'medium'),
            'acknowledged',
            data.get('affectedService'),
            data.get('affectedLocation'),
            data.get('reportedBy'),
            datetime.utcnow()
        ))
        
        problem = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify(problem), 201
        
    except Exception as e:
        logger.error(f"Error creating service problem: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/tmf656/serviceProblem/<problem_id>', methods=['GET'])
def get_service_problem(problem_id):
    """TMF656: Get service problem details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM service_problems WHERE id = %s
        """, (problem_id,))
        
        problem = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if problem:
            return jsonify(problem)
        else:
            return jsonify({"error": "Problem not found"}), 404
            
    except Exception as e:
        logger.error(f"Error getting service problem: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/tmf656/serviceOutage', methods=['POST'])
def create_service_outage():
    """Create a service outage affecting an area"""
    try:
        data = request.json
        outage_id = str(uuid.uuid4())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO service_outages (
                id, title, description, severity, status,
                affected_area, service_type, estimated_resolution,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            outage_id,
            data.get('title'),
            data.get('description'),
            data.get('severity', 'major'),
            'active',
            data.get('affectedArea'),
            data.get('serviceType'),
            data.get('estimatedResolution'),
            datetime.utcnow()
        ))
        
        outage = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify(outage), 201
        
    except Exception as e:
        logger.error(f"Error creating service outage: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/tmf656/serviceOutage/area/<area>', methods=['GET'])
def get_area_outages(area):
    """Get active outages for a specific area"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM service_outages 
            WHERE affected_area LIKE %s 
            AND status = 'active'
            ORDER BY created_at DESC
        """, (f'%{area}%',))
        
        outages = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify(outages)
        
    except Exception as e:
        logger.error(f"Error getting area outages: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/tmf656/troubleTicket', methods=['POST'])
def create_trouble_ticket():
    """Create a trouble ticket for a service problem"""
    try:
        data = request.json
        ticket_id = str(uuid.uuid4())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO trouble_tickets (
                id, problem_id, customer_id, severity, status,
                description, resolution_action, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            ticket_id,
            data.get('problemId'),
            data.get('customerId'),
            data.get('severity', 'medium'),
            'open',
            data.get('description'),
            data.get('resolutionAction'),
            datetime.utcnow()
        ))
        
        ticket = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify(ticket), 201
        
    except Exception as e:
        logger.error(f"Error creating trouble ticket: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/tmf656/troubleTicket/<ticket_id>/resolve', methods=['PATCH'])
def resolve_trouble_ticket(ticket_id):
    """Resolve a trouble ticket"""
    try:
        data = request.json
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE trouble_tickets 
            SET status = 'resolved',
                resolution_notes = %s,
                resolved_at = %s
            WHERE id = %s
            RETURNING *
        """, (
            data.get('resolutionNotes'),
            datetime.utcnow(),
            ticket_id
        ))
        
        ticket = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        if ticket:
            return jsonify(ticket)
        else:
            return jsonify({"error": "Ticket not found"}), 404
            
    except Exception as e:
        logger.error(f"Error resolving trouble ticket: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/fault-status/<customer_id>', methods=['GET'])
def get_customer_fault_status(customer_id):
    """Get fault status for a customer including area outages"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get customer location
        cursor.execute("""
            SELECT street_name, city FROM customers WHERE id = %s
        """, (customer_id,))
        
        customer = cursor.fetchone()
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        
        # Check for area outages
        cursor.execute("""
            SELECT * FROM service_outages 
            WHERE affected_area LIKE %s 
            AND status = 'active'
        """, (f'%{customer["street_name"]}%',))
        
        outages = cursor.fetchall()
        
        # Get customer's trouble tickets
        cursor.execute("""
            SELECT * FROM trouble_tickets 
            WHERE customer_id = %s 
            AND status != 'resolved'
            ORDER BY created_at DESC
        """, (customer_id,))
        
        tickets = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "customerId": customer_id,
            "location": f"{customer['street_name']}, {customer['city']}",
            "activeOutages": outages,
            "openTickets": tickets,
            "serviceStatus": "degraded" if outages else "normal"
        })
        
    except Exception as e:
        logger.error(f"Error getting customer fault status: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
