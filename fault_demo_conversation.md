# Fault Management Demo Conversation

This demonstrates how an AI agent using the MCP tools would handle a customer service call about a network fault.

## Customer Call Scenario

**Time**: 10:15 AM  
**Customer**: Jane Doe, 123 Main Street, Dublin

---

### Initial Contact

**Customer**: "Hi, I'm Jane Doe and I live at 123 Main Street in Dublin. My internet service just stopped working completely about 15 minutes ago. I work from home and really need this fixed!"

**Agent**: "I'm so sorry to hear you're experiencing issues with your internet service, Jane. I understand how important this is, especially when you're working from home. Let me check the service status for your location right away."

*[Agent uses: `check_service_status` with location: {streetName: "Main Street", streetNumber: "123", city: "Dublin"}]*

### Diagnosis

**Agent**: "Jane, I've identified the issue. There's been a fiber optic cable cut on Main Street due to construction work. This is affecting multiple customers in your area, including your service. The good news is I have several options to help restore your service quickly."

**Customer**: "Oh no! When will it be fixed? I have important video calls this afternoon!"

**Agent**: "I completely understand your concern. Let me take immediate action to get you back online as quickly as possible. I have both a temporary solution that will have you working within 15 minutes, and I'll also arrange for a permanent fix."

### Immediate Action

**Agent**: "First, I'm going to reroute your internet traffic through our backup network path. This will restore your service temporarily within the next 15 minutes."

*[Agent uses: `execute_remedial_action` with action: "REROUTE_TRAFFIC"]*

**Agent**: "Great news! I've successfully rerouted your traffic. Your internet service should be restored within 15 minutes. It might be slightly slower than your usual speeds - you'll get about 80% of your normal bandwidth - but it will definitely support your video calls."

### Creating Trouble Ticket

*[Agent uses: `create_trouble_ticket` with customer details and issue description]*

**Agent**: "I've also created a trouble ticket for you - the reference number is TT-2024-001234. You can use this to track the progress of the permanent repair."

### Scheduling Permanent Fix

**Agent**: "Now, let me dispatch a field technician to permanently repair the fiber cut."

*[Agent uses: `execute_remedial_action` with action: "DISPATCH_TECHNICIAN"]*

**Agent**: "Perfect! I've dispatched our technician John Smith to your area. He'll arrive around 11:00 AM - that's in about 45 minutes. The permanent repair should be completed by 2:00 PM today."

### Customer Notification

*[Agent uses: `execute_remedial_action` with action: "NOTIFY_CUSTOMERS"]*

**Agent**: "I've also arranged for you to receive SMS updates about the repair progress, so you'll know exactly when everything is back to normal."

### Addressing Concerns

**Customer**: "That's fantastic! Thank you so much for the quick response. Will I get any compensation for this outage?"

**Agent**: "Absolutely! Since this is a service disruption on our end, you'll automatically receive a credit on your next bill for the affected period. This will be calculated from when the outage started until full service is restored, and will appear on your next statement. You don't need to do anything - it's all handled automatically."

**Customer**: "One more question - will this affect my service quality once it's fixed?"

**Agent**: "Not at all. Once the fiber cable is repaired, your service will return to full speed and quality. The temporary rerouting is just to keep you connected while we make the permanent fix. After 2:00 PM today, everything will be back to normal."

### Checking Area Impact

**Agent**: "I can also see that this issue is affecting about 150 customers in your area. We're prioritizing this repair because of the number of people impacted. Is there anything else I can help you with while we work on this?"

*[Agent could use: `get_service_problems` to show area-wide impact if needed]*

### Closing

**Customer**: "No, I think that covers everything. I'm really impressed with how quickly you've handled this!"

**Agent**: "Thank you, Jane! Just to summarize:
- Your internet will be restored via our backup network within 15 minutes
- Technician John Smith will arrive around 11:00 AM for the permanent repair
- Full service will be restored by 2:00 PM
- You'll receive SMS updates throughout the process
- A credit will automatically appear on your next bill
- Your trouble ticket number is TT-2024-001234

If you experience any issues or need anything else, please don't hesitate to call back. Have a great day and good luck with your video calls!"

---

## Key Features Demonstrated

1. **Proactive Diagnosis**: Immediate identification of network fault
2. **Multi-layered Solution**: Temporary fix (15 min) + permanent repair (4 hours)
3. **Clear Communication**: Explaining the issue and timeline clearly
4. **Automated Processes**: Ticket creation, technician dispatch, customer notifications
5. **Compensation Handling**: Automatic billing credits
6. **Empathy & Understanding**: Acknowledging customer's work-from-home needs
7. **Complete Resolution**: End-to-end handling in a single call

## Tools Used

- `check_service_status`: Initial diagnosis
- `execute_remedial_action` (REROUTE_TRAFFIC): Immediate relief
- `create_trouble_ticket`: Issue tracking
- `execute_remedial_action` (DISPATCH_TECHNICIAN): Permanent fix
- `execute_remedial_action` (NOTIFY_CUSTOMERS): Proactive updates
- `get_service_problems`: Area-wide visibility (if needed)
