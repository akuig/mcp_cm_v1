# 🎯 Demo Execution Guide - Sales Team Playbook

## 📋 **Quick Reference for Sales Teams**

This guide provides exact scripts, commands, and setup instructions for executing compelling demos of the Enhanced Catalog Manager.

---

## 🚀 **Demo Environment Setup**

### **Pre-Demo Checklist (30 minutes before)**

#### **System Startup**
```bash
# 1. Navigate to project directory
cd /Users/joe/dev/mcp_cm_v1

# 2. Start all services
docker-compose -f docker-compose.extended.yml up -d

# 3. Wait for services to initialize
sleep 30

# 4. Validate system health
curl http://localhost:8080/health
# Expected response: {"status": "healthy", "database": "connected"}

# 5. Quick system validation
./scripts/validate_deployment.sh
```

#### **Demo Data Preparation**
```bash
# Verify sample data is loaded
curl -s "http://localhost:8080/tmf629/customer/8452934" | jq '.name'
# Expected: "Jane Doe"

curl -s "http://localhost:8080/tmf622/productOrder?limit=3" | jq 'length'
# Expected: 3 (or more)

curl -s "http://localhost:8080/api/product-offerings?limit=5" | jq 'length'  
# Expected: 5 (or more)
```

#### **Screen Setup**
- **Primary screen**: Claude Desktop with Enhanced Catalog Manager tools visible
- **Secondary screen**: Browser with API endpoints for technical backup
- **Have ready**: Customer data, ROI calculator, follow-up materials

---

## 🎭 **Scenario 1: Customer Service Excellence**
### **Duration: 8 minutes**

#### **Setup Story**
*"Let me show you how Sarah, one of our customer service reps, handles a typical customer inquiry. This used to take 8+ minutes across multiple systems - watch how AI changes everything."*

#### **Live Demo Script**

##### **Step 1: Customer Lookup (2 minutes)**
```
Say: "Sarah receives a call from Jane Doe asking about her account..."

In Claude Desktop, type:
"Get customer information for customer ID 8452934"

AI will use: customer_management tool
Expected result: Complete customer profile with:
- Name: Jane Doe
- Account Status: Active  
- Credit Score: 720
- Address: 456 Main Street, Springfield
- No overdue payments

Key Message: "In 2 seconds, Sarah has complete customer context."
```

##### **Step 2: Service Availability Check (2 minutes)**
```
Say: "Jane asks about fiber internet availability at her address..."

In Claude Desktop, type:
"Check fiber internet availability at 456 Main Street, Springfield for fiber-internet-premium service"

AI will use: service_qualification tool
Expected result: Service qualification showing:
- Service: Qualified for fiber
- Speed: 1000 Mbps available
- Technology: Fiber optic
- Quality: Excellent

Key Message: "Real-time service qualification prevents customer disappointment."
```

##### **Step 3: Order History Review (2 minutes)**
```
Say: "Jane wants to know about her recent orders..."

In Claude Desktop, type:
"Show me recent orders for customer 8452934"

AI will use: order_management tool
Expected result: List of customer orders with:
- Order ID, dates, products
- Current status
- Service details
- Pricing information

Key Message: "Complete order visibility eliminates transfers and holds."
```

##### **Step 4: Business Impact Summary (2 minutes)**
```
Present metrics:
- Call time: 8 minutes → 3 minutes (62% reduction)
- System switches: 5 → 0 (100% elimination)
- Customer satisfaction: +16 points
- Agent productivity: +85%

Key Message: "This single interaction shows why our customers see immediate ROI."
```

---

## 🛠️ **Scenario 2: Network Operations Intelligence**
### **Duration: 10 minutes**

#### **Setup Story**
*"Now let's see how Marcus, our Network Operations Manager, handles service activation and network planning with AI assistance."*

#### **Live Demo Script**

##### **Step 1: Service Activation (2 minutes)**
```
Say: "Marcus needs to activate Jane's fiber service from her order..."

In Claude Desktop, type:
"Activate fiber internet service for customer at 456 Main Street, Springfield using service specification fiber-internet-premium"

AI will use: service_activation tool
Expected result: Service activation with:
- Service ID generated
- Activation timestamp
- Service type: Fiber Internet Premium
- Status: Activated

Key Message: "Zero-touch activation reduces errors and accelerates deployment."
```

##### **Step 2: Coverage Analysis (3 minutes)**
```
Say: "Marcus wants to analyze coverage gaps for expansion planning..."

In Claude Desktop, type:
"Show me geographic locations with coverage information, focusing on areas that need fiber expansion"

AI will use: list_geographic_locations tool
Expected result: Coverage analysis showing:
- Multiple locations with coverage details
- Service types available per location
- Coverage quality ratings
- Expansion opportunities

Key Message: "AI-powered coverage analysis drives strategic network investments."
```

##### **Step 3: Service Catalog Optimization (3 minutes)**
```
Say: "Marcus reviews service specifications for performance optimization..."

In Claude Desktop, type:
"List all fiber internet service specifications with their technical details"

AI will use: list_service_specifications tool
Expected result: Technical specifications showing:
- Service types and speeds
- Technical parameters
- Performance metrics
- Utilization data

Key Message: "Data-driven catalog optimization ensures competitive positioning."
```

##### **Step 4: Network Expansion (2 minutes)**
```
Say: "Marcus adds 5G coverage to a new area..."

In Claude Desktop, type:
"Add 5G mobile coverage to location cambridge-ma with excellent signal strength"

AI will use: add_geographic_coverage tool
Expected result: New coverage addition with:
- Location: Cambridge, MA
- Service type: 5G mobile
- Signal strength: Excellent
- Coverage confirmed

Key Message: "Streamlined expansion with comprehensive tracking."
```

---

## 📊 **Scenario 3: Strategic Product Management**
### **Duration: 12 minutes**

#### **Setup Story**
*"Finally, let's see how Lisa, our Product Manager, uses AI for strategic catalog management and new product development."*

#### **Live Demo Script**

##### **Step 1: Portfolio Analysis (3 minutes)**
```
Say: "Lisa analyzes the current product portfolio for market opportunities..."

In Claude Desktop, type:
"Show me all product offerings with pricing and category breakdown, include linked services"

AI will use: list_product_offerings tool
Expected result: Complete portfolio view with:
- Products by category
- Pricing distribution
- Linked technical specifications
- Market positioning

Key Message: "Comprehensive portfolio view enables strategic decisions."
```

##### **Step 2: New Product Development (3 minutes)**
```
Say: "Lisa creates a new enterprise fiber package..."

In Claude Desktop, type:
"Create a new product offering called 'Enterprise Fiber Pro' for business category, priced at $299.99 monthly with 24-month contract"

AI will use: create_product_offering tool
Expected result: New product created with:
- Name: Enterprise Fiber Pro
- Category: Business
- Pricing: $299.99/month
- Contract: 24 months
- Product ID generated

Key Message: "Rapid product development with automated catalog integration."
```

##### **Step 3: Technical Specification Creation (3 minutes)**
```
Say: "Lisa creates the technical specification for the new service..."

In Claude Desktop, type:
"Create a service specification called 'Enterprise Fiber 1GB' for business fiber internet with 1000 Mbps speeds and 99.9% SLA"

AI will use: create_service_specification tool
Expected result: Service spec created with:
- Name: Enterprise Fiber 1GB
- Type: Business fiber internet
- Speeds: 1000 Mbps
- SLA: 99.9%
- Technical compliance validated

Key Message: "Technical accuracy and TMF compliance automatically ensured."
```

##### **Step 4: Product-Service Linking & Validation (3 minutes)**
```
Say: "Lisa links the product to its technical specification and validates the catalog..."

In Claude Desktop, type:
"Link the Enterprise Fiber Pro product to the Enterprise Fiber 1GB service specification, then run a complete catalog integrity check"

AI will use: link_offering_to_specification and sync_catalog_data tools
Expected result: 
- Product-service link established
- Catalog integrity: 100% validated
- Compliance: TMF standards met
- Optimization recommendations provided

Key Message: "Automated validation ensures data quality and compliance."
```

---

## 🚀 **Advanced Integration Demo**
### **Duration: 15 minutes (Technical Audience)**

#### **End-to-End Customer Journey**
```
Demonstrate complete workflow:

1. "A new customer calls asking about internet service at 789 Pine Road"
   → Service qualification shows fiber available

2. "Customer wants to order Fiber 1GB service"
   → Product ordering creates new order

3. "Order flows automatically to network operations"
   → Service activation provisions the service

4. "Customer receives confirmation and service is live"
   → Complete journey in 15 minutes vs 3-5 days

Timeline demonstration:
- Minute 1-3: Qualification and selection
- Minute 4-8: Order creation and validation  
- Minute 9-12: Service provisioning
- Minute 13-15: Activation and confirmation
```

---

## 💰 **ROI Calculator Demo**
### **Duration: 5 minutes**

#### **Live ROI Calculation**
```
Input customer's current metrics:
"Let me show you the ROI calculation based on your current operations..."

Current State (get from customer):
- Number of agents: ___
- Average call time: ___ minutes
- Daily orders processed: ___
- Service activation time: ___ hours

Enhanced Catalog Manager Impact:
- Call time reduction: 62%
- Order processing acceleration: 99%
- Service activation speed: 99%
- Error reduction: 96%

Annual Savings Calculation:
[Use ROI calculator spreadsheet/tool]
- Labor cost savings: $___
- Error reduction savings: $___
- Efficiency gains: $___
- Customer satisfaction improvement: $___

Total Annual Benefit: $___
Implementation Cost: $___
ROI: ___%

Key Message: "Most customers see 1000%+ ROI in the first year."
```

---

## 🎯 **Technical Backup Demonstrations**

### **If AI Demo Fails - Direct API Demo**

#### **Customer Management (TMF629)**
```bash
curl "http://localhost:8080/tmf629/customer/8452934"
```

#### **Order Management (TMF622) - Show List Format**
```bash
curl "http://localhost:8080/tmf622/productOrder?limit=5"
```

#### **Service Qualification (TMF637)**
```bash
curl -X POST "http://localhost:8080/tmf637/serviceQualification" \
  -H "Content-Type: application/json" \
  -d '{
    "address": {
      "streetName": "Main Street",
      "streetNumber": "456", 
      "city": "Springfield"
    },
    "serviceSpecification": {
      "id": "fiber-internet-premium",
      "name": "Fiber Internet Premium"
    }
  }'
```

#### **Enhanced Product Catalog**
```bash
curl "http://localhost:8080/api/product-offerings?category=internet&max_price=100"
```

---

## 🎪 **Demo Flow Templates**

### **20-Minute Executive Demo**
```
0-2 min:   Problem statement and solution overview
2-8 min:   Customer service scenario (Sarah)
8-14 min:  Network operations scenario (Marcus)  
14-18 min: ROI calculation and business impact
18-20 min: Next steps and call to action
```

### **45-Minute Technical Demo**
```
0-5 min:   Architecture overview and TMF compliance
5-15 min:  Customer service scenario with deep dive
15-25 min: Network operations with technical details
25-35 min: Product management and catalog optimization
35-40 min: Integration capabilities and API demo
40-45 min: Implementation planning and next steps
```

### **60-Minute Discovery Demo**
```
0-10 min:  Discovery questions and current state analysis
10-25 min: Tailored scenarios based on customer pain points
25-40 min: Deep technical demonstration
40-50 min: Customized ROI calculation
50-60 min: Implementation planning and proposal discussion
```

---

## 🛠️ **Troubleshooting During Demo**

### **If System is Slow**
```
- Restart containers: docker-compose restart
- Check system resources: docker stats
- Use direct API calls as backup
- Have screenshot backups ready
```

### **If AI Tools Fail**
```
- Switch to direct API demonstration
- Use curl commands from backup
- Show recorded demo video
- Focus on business value and ROI
```

### **If Data is Missing**
```
- Reset database: docker-compose down -v && docker-compose up -d
- Use alternative customer IDs: 8452935, 8452936, etc.
- Have sample data screenshots ready
- Explain with mock scenarios
```

---

## 📞 **Demo Closing Scripts**

### **For Interested Prospects**
```
"Based on what you've seen today, I'd like to propose a 30-day pilot program
where we can deploy this in a limited environment and measure the exact impact
on your operations. We guarantee measurable results or we'll provide a full
refund. When would be a good time to discuss the pilot program details?"
```

### **For Technical Evaluators**
```
"I'd like to set up a technical deep-dive session where your team can test
the APIs directly, review the architecture, and validate the integration
capabilities. We can also provide a sandbox environment for hands-on
evaluation. What technical validation do you need to move forward?"
```

### **For Budget Holders**
```
"The ROI calculation shows [specific amount] in annual savings for your
organization. I'd like to prepare a detailed business case and implementation
timeline. What's your budget cycle, and who else needs to be involved in
the decision process?"
```

---

## 📋 **Post-Demo Follow-up Checklist**

### **Within 24 Hours**
- [ ] Send demo recording and documentation
- [ ] Provide customized ROI calculation
- [ ] Share relevant case studies
- [ ] Schedule follow-up meeting
- [ ] Send technical documentation if requested

### **Within 1 Week**
- [ ] Prepare custom proposal/pilot program
- [ ] Arrange technical deep-dive if needed
- [ ] Connect with customer's technical team
- [ ] Provide references and testimonials
- [ ] Create implementation timeline

### **Within 2 Weeks**
- [ ] Present formal proposal
- [ ] Address any technical concerns
- [ ] Negotiate pilot or full deployment
- [ ] Establish project timeline
- [ ] Begin contract discussions

---

**🎯 This demo execution guide provides sales teams with everything needed to deliver compelling, technically accurate demonstrations that convert prospects into customers.**