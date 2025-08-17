# Demo Database Reset Scripts

This toolkit provides scripts to reset your Telepath AI catalog manager demo database, cleaning up test orders and service activations to prepare for fresh demonstrations.

## 🚀 Quick Start

```bash
# Make scripts executable
chmod +x demo_reset.sh

# Run a dry run to see what would be reset
./demo_reset.sh --dry-run

# Reset the demo database
./demo_reset.sh
```

## 📁 Files Included

| File | Description |
|------|-------------|
| `demo_reset.py` | Main Python script with reset logic |
| `demo_reset.sh` | Shell wrapper for easy execution |
| `config.yaml` | Configuration file for customization |
| `README_demo_reset.md` | This documentation |

## 🔧 Installation

1. **Place scripts in your project directory:**
   ```bash
   mkdir demo_reset_tools
   cd demo_reset_tools
   # Copy all scripts to this directory
   ```

2. **Install Python dependencies:**
   ```bash
   pip install aiohttp pyyaml
   ```

3. **Make shell script executable:**
   ```bash
   chmod +x demo_reset.sh
   ```

4. **Configure settings:**
   - Edit `config.yaml` to match your environment
   - Update the catalog manager URL
   - Add/remove demo customer IDs

## 💻 Usage Options

### Shell Script (Recommended)
```bash
# Basic reset
./demo_reset.sh

# Dry run (preview only)
./demo_reset.sh --dry-run

# Reset specific customer
./demo_reset.sh --customer-id 1234567

# Custom catalog manager URL
./demo_reset.sh --url http://localhost:8080

# Show help
./demo_reset.sh --help
```

### Python Script (Advanced)
```bash
# Basic usage
python3 demo_reset.py

# With options
python3 demo_reset.py --dry-run --customer-id 8452934 --url http://localhost:8080
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
# Change the catalog manager URL
catalog_manager:
  url: "http://your-server:8080"

# Add demo customers to reset
demo_customers:
  - id: "8452934"
    name: "Jane Doe"
  - id: "1234567" 
    name: "John Smith"

# Control what gets reset
reset_options:
  delete_orders: true
  deactivate_services: true
  cleanup_audit_logs: true
```

## 🎯 What Gets Reset

The script will clean up:

✅ **Demo Customer Orders**
- All orders for specified demo customers
- Associated order items and product offerings

✅ **Service Activations** 
- Services activated for demo customers
- Orphaned demo service activations

✅ **Audit Logs** (optional)
- Today's audit entries for demo operations

❌ **What's NOT Reset**
- Customer account information
- Product catalog (offerings, specifications)
- System configuration
- Production customer data

## 🔒 Safety Features

- **Dry Run Mode:** Preview changes without making them
- **Confirmation Required:** Prompts before destructive operations
- **Logging:** All operations logged with timestamps
- **Environment Checks:** Can be configured to only run in safe environments
- **Backup Options:** Optional data backup before deletion

## 📋 Typical Demo Workflow

1. **Before Demo:**
   ```bash
   ./demo_reset.sh --dry-run  # Preview what will be reset
   ./demo_reset.sh            # Clean slate for demo
   ```

2. **Run Demo:**
   - Create customer orders
   - Activate services
   - Show catalog features

3. **After Demo:**
   ```bash
   ./demo_reset.sh            # Clean up for next demo
   ```

## 🔍 Troubleshooting

### Common Issues

**"Python script not found"**
- Ensure `demo_reset.py` is in the same directory as `demo_reset.sh`
- Check file permissions

**"Could not connect to catalog manager"**
- Verify the URL in `config.yaml`
- Check if the catalog manager service is running
- Confirm network connectivity

**"Permission denied"**
- Make scripts executable: `chmod +x demo_reset.sh`
- Check if you have write access to the logs directory

### Log Files

All operations are logged to:
```
logs/demo_reset_YYYYMMDD_HHMMSS.log
```

Check recent logs for detailed error information:
```bash
ls -la logs/
tail -f logs/demo_reset_*.log
```

## 🛠️ Customization

### Adding New Demo Customers

Edit `config.yaml`:
```yaml
demo_customers:
  - id: "8452934"
    name: "Jane Doe"
  - id: "9876543"
    name: "New Demo Customer"
```

### Custom Reset Logic

Modify `demo_reset.py` to add custom cleanup:
```python
async def custom_cleanup(self):
    # Add your custom reset logic here
    pass
```

### Database Integration

For direct database access, configure in `config.yaml`:
```yaml
database:
  host: "localhost"
  database: "catalog_manager"
  # Add connection details
```

## 📞 Support

If you encounter issues:

1. Check the log files for detailed error messages
2. Verify your configuration in `config.yaml`
3. Test with `--dry-run` first
4. Ensure the catalog manager service is accessible

## 🔄 Version History

- **v1.0:** Initial release with order and service cleanup
- **Future:** Database backup, advanced filtering, web UI

---

**⚠️ Important:** Always test with `--dry-run` first, especially in production environments!
