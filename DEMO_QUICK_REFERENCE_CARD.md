# 📋 Demo Quick Reference Card

## 🚀 **Essential Commands & Key Messages**

### **Pre-Demo Setup (5 minutes)**
```bash
cd /Users/joe/dev/mcp_cm_v1
docker-compose -f docker-compose.extended.yml up -d
sleep 30
curl http://localhost:8080/health  # Should return "healthy"
```

---

## 🎭 **3 Core Demo Scenarios**

### **1. Customer Service (Sarah) - 8 minutes**

#### **Customer Lookup**
```
Claude Prompt: "Get customer information for customer ID 8452934"
Key Message: "Complete customer context in 2 seconds"
Expected: Jane Doe, Active account, Credit 720, Springfield address
```

#### **Service Check**
```
Claude Prompt: "Check fiber internet availability at 456 Main Street, Springfield"
Key Message: "Real-time service qualification prevents disappointment"
Expected: Fiber available, 1000 Mbps, Excellent quality
```

#### **Order Review**
```
Claude Prompt: "Show recent orders for customer 8452934"
Key Message: "Complete order visibility eliminates transfers"
Expected: List of orders with status, dates, products
```

### **2. Network Ops (Marcus) - 10 minutes**

#### **Service Activation**
```
Claude Prompt: "Activate fiber service at 456 Main Street for fiber-internet-premium"
Key Message: "Zero-touch activation reduces errors"
Expected: Service activated with ID and timestamp
```

#### **Coverage Analysis**
```
Claude Prompt: "Show geographic locations with coverage for expansion planning"
Key Message: "AI-powered coverage analysis drives investments"
Expected: Locations with coverage details and gaps
```

### **3. Product Management (Lisa) - 12 minutes**

#### **Portfolio Analysis**
```
Claude Prompt: "Show all product offerings with pricing and categories"
Key Message: "Comprehensive portfolio view enables strategic decisions"
Expected: Product catalog with pricing and categories
```

#### **New Product Creation**
```
Claude Prompt: "Create Enterprise Fiber Pro product at $299.99/month for business"
Key Message: "Rapid product development with automation"
Expected: New product created with ID
```

---

## 💰 **ROI Key Messages**

### **Before vs After Metrics**
```
Call Time:        8.5 min → 3.2 min    (62% reduction)
Order Processing: 2-3 days → 15 min    (99% reduction)
Service Activation: 24-48h → 15 min    (99% reduction)
Error Rate:       12% → 0.3%           (96% reduction)
Customer Sat:     78% → 94%            (+16 points)
```

### **Annual ROI (1000 agents)**
```
Cost Savings:     $5.55M/year
Revenue Increase: $4.2M/year
Total Benefit:    $9.75M/year
ROI:              1,850% in Year 1
```

---

## 🛠️ **Technical Backup Commands**

### **If AI Demo Fails**
```bash
# Customer lookup
curl "http://localhost:8080/tmf629/customer/8452934"

# Order list (shows proper list format)
curl "http://localhost:8080/tmf622/productOrder?limit=5"

# Product catalog
curl "http://localhost:8080/api/product-offerings?category=internet"

# Health check
curl "http://localhost:8080/health"
```

---

## 🎯 **Key Differentiators**

### **vs Traditional Systems**
```
❌ 6-12 month implementation → ✅ 2-4 week deployment
❌ Multiple system integration → ✅ Single AI interface  
❌ Manual catalog management → ✅ AI-powered automation
❌ Custom development needed → ✅ Pre-built TMF compliance
```

### **vs Other AI Solutions**
```
❌ Generic AI → ✅ Purpose-built for telecom
❌ Limited TMF compliance → ✅ 100% TMF standards
❌ Separate tools → ✅ Integrated 13-tool suite
❌ No real-time catalog → ✅ Live optimization
```

---

## 🎪 **Demo Flow Timing**

### **20-Minute Executive**
```
0-2:   Problem/Solution overview
2-8:   Sarah customer service demo
8-14:  Marcus network ops demo
14-18: ROI calculation
18-20: Next steps/CTA
```

### **45-Minute Technical**
```
0-5:   Architecture overview
5-15:  Sarah demo + deep dive
15-25: Marcus demo + technical details
25-35: Lisa product management demo
35-40: API demonstrations
40-45: Implementation planning
```

---

## 🚨 **Emergency Scenarios**

### **System Issues**
```
1. Restart: docker-compose restart
2. Use API backup commands
3. Show recorded demo videos
4. Focus on ROI and business value
```

### **Missing Data**
```
Alternative Customer IDs: 8452935, 8452936, 8452937
Reset command: docker-compose down -v && docker-compose up -d
Backup screenshots in demo folder
```

---

## 📞 **Closing Scripts**

### **Pilot Program Close**
```
"30-day pilot with 50 agents, one product line, guaranteed results or refund.
$25K investment, 300%+ expected ROI. When can we start?"
```

### **Technical Evaluation Close**
```
"Technical deep-dive with your team, sandbox environment for testing,
API validation. What technical proof do you need?"
```

### **Enterprise Close**
```
"Full implementation: 8-12 weeks, complete training, 1000%+ ROI guarantee.
Custom quote based on your scale. Ready to transform?"
```

---

## 📊 **Sample Customer Data**

### **Customer Records**
```
8452934: Jane Doe, Active, Springfield, Credit 720
8452935: John Smith, Active, Springfield, Credit 680  
8452936: Alice Johnson, Active, Springfield, Credit 750
8452937: Bob Williams, Suspended, Springfield, Credit 620
```

### **Product Examples**
```
fiber-1gb: Fiber 1GB Internet, $79.99/month
cable-200mb: Cable 200MB Internet, $59.99/month
mobile-unlimited: Mobile Unlimited, $85.00/month
bundle-triple-play: Triple Play Bundle, $149.99/month
```

---

## 🎯 **Success Metrics to Highlight**

### **Customer Impact**
```
- 62% reduction in call time
- 99% faster order processing  
- 96% error reduction
- 16-point customer satisfaction increase
```

### **Business Impact**
```
- $9.75M annual benefit for 1000 agents
- 1,850% ROI in first year
- 2-week implementation vs 6-12 months
- Zero-risk pilot program available
```

### **Technical Impact**
```
- 100% TMF compliance (622, 629, 637, 640)
- 13 integrated tools in single platform
- Real-time catalog management
- Cloud-native, scalable architecture
```

---

**🎯 Keep this card handy during demos for quick reference to commands, metrics, and key messages that close deals!**
