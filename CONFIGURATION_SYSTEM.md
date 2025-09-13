# ⚙️ Configuration System Template
## Making Your AI Code Reviewer Customizable for Different Clients

---

## 🎯 **Configuration Structure**

### **1. Client-Specific Config Files**
```yaml
# config/startup_team.yml
client_name: "TechStartup Inc"
plan: "professional"

# AI Review Settings
ai_review:
  enabled: true
  models: ["bedrock-nova-micro"]  # Cost-effective for startups
  languages: ["javascript", "python", "typescript"]
  max_file_size: 1000  # lines
  
# Critical Words Detection
critical_words:
  enabled: true
  threshold: 8  # Lower threshold for small teams
  categories:
    security: high
    quality: medium
    development: low
  custom_words:
    - "hack"
    - "temp_password"
    - "bypass_security"

# Team Settings  
team:
  size: 15
  experience_level: "mixed"
  review_style: "educational"  # More explanatory comments
  
# Integrations
integrations:
  slack: 
    enabled: true
    channel: "#code-reviews"
  jira:
    enabled: false
```

### **2. Enterprise Config Example**
```yaml
# config/enterprise_bank.yml
client_name: "SecureBank Corp"
plan: "enterprise"

# AI Review Settings
ai_review:
  enabled: true
  models: ["bedrock-claude-v3"]  # More powerful for enterprise
  languages: ["java", "python", "c++", "go", "typescript"]
  max_file_size: 5000
  custom_rules: "financial_compliance.yml"
  
# Critical Words Detection
critical_words:
  enabled: true
  threshold: 15  # Higher threshold for enterprise
  strict_mode: true
  categories:
    security: critical
    financial: critical
    compliance: critical
    quality: high
    development: medium
  
  # Custom word lists for banking
  custom_words:
    - "credit_card"
    - "ssn"
    - "account_number"
    - "wire_transfer"
    - "admin_override"

# Enterprise Features
enterprise:
  audit_logging: true
  compliance_reporting: true
  role_based_access: true
  custom_integrations: true
  
# Security Requirements
security:
  data_residency: "US"
  encryption: "AES-256"
  access_logs: true
  ip_whitelist: ["10.0.0.0/8", "192.168.1.0/24"]

# Team Structure
team:
  size: 500
  departments: ["backend", "frontend", "security", "devops"]
  approval_workflow: "multi-stage"
```

---

## 🛠️ **Configuration Management System**

### **1. Configuration Loader (Python)**
```python
# config_manager.py
import yaml
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration for specific client"""
        config_path = f"config/{self.client_id}.yml"
        
        # Load default config first
        with open("config/default.yml", 'r') as f:
            config = yaml.safe_load(f)
        
        # Override with client-specific config
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                client_config = yaml.safe_load(f)
                config.update(client_config)
        
        return config
    
    def get_ai_settings(self) -> Dict[str, Any]:
        """Get AI review settings"""
        return self.config.get('ai_review', {})
    
    def get_critical_words_config(self) -> Dict[str, Any]:
        """Get critical words detection settings"""
        return self.config.get('critical_words', {})
    
    def get_threshold(self) -> int:
        """Get critical words threshold"""
        return self.config.get('critical_words', {}).get('threshold', 10)
    
    def get_enabled_languages(self) -> list:
        """Get list of enabled programming languages"""
        return self.config.get('ai_review', {}).get('languages', ['python', 'javascript'])
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        return self.config.get(feature, {}).get('enabled', False)

# Usage example
config = ConfigManager("startup_team")
threshold = config.get_threshold()
languages = config.get_enabled_languages()
```

### **2. Dynamic Configuration in GitHub Actions**
```yaml
# .github/workflows/configurable-ai-review.yml
name: Configurable AI Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Load Client Configuration
      id: config
      run: |
        # Determine client from repository or environment
        CLIENT_ID="${{ github.repository_owner }}"
        echo "client_id=$CLIENT_ID" >> $GITHUB_OUTPUT
        
        # Load configuration
        if [ -f "config/${CLIENT_ID}.yml" ]; then
          echo "Using client config: ${CLIENT_ID}.yml"
          CONFIG_FILE="config/${CLIENT_ID}.yml"
        else
          echo "Using default config"
          CONFIG_FILE="config/default.yml"
        fi
        echo "config_file=$CONFIG_FILE" >> $GITHUB_OUTPUT
    
    - name: AI Code Review
      env:
        CONFIG_FILE: ${{ steps.config.outputs.config_file }}
        CLIENT_ID: ${{ steps.config.outputs.client_id }}
      run: |
        python3 << 'EOF'
        import yaml
        import os
        
        # Load configuration
        with open(os.environ['CONFIG_FILE'], 'r') as f:
            config = yaml.safe_load(f)
        
        # Use configuration in AI review
        ai_models = config.get('ai_review', {}).get('models', ['bedrock-nova-micro'])
        languages = config.get('ai_review', {}).get('languages', ['python'])
        threshold = config.get('critical_words', {}).get('threshold', 10)
        
        print(f"🔧 Configuration loaded for: {os.environ['CLIENT_ID']}")
        print(f"📊 AI Models: {ai_models}")
        print(f"🔤 Languages: {languages}")
        print(f"⚠️ Threshold: {threshold}")
        
        # Your AI review logic here...
        EOF
```

---

## 🏗️ **Multi-Tenant Architecture**

### **1. Database Schema**
```sql
-- clients table
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    plan VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    config JSONB
);

-- client_repos table  
CREATE TABLE client_repos (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    repo_name VARCHAR(255) NOT NULL,
    repo_url VARCHAR(500),
    active BOOLEAN DEFAULT true
);

-- review_history table
CREATE TABLE review_history (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    repo_name VARCHAR(255),
    pr_number INTEGER,
    ai_findings INTEGER,
    critical_words INTEGER,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **2. Configuration API**
```python
# config_api.py
from flask import Flask, request, jsonify
from database import get_client_config, update_client_config

app = Flask(__name__)

@app.route('/api/config/<client_id>', methods=['GET'])
def get_config(client_id):
    """Get client configuration"""
    config = get_client_config(client_id)
    if not config:
        return jsonify({'error': 'Client not found'}), 404
    return jsonify(config)

@app.route('/api/config/<client_id>', methods=['PUT'])
def update_config(client_id):
    """Update client configuration"""
    new_config = request.json
    
    # Validate configuration
    if not validate_config(new_config):
        return jsonify({'error': 'Invalid configuration'}), 400
    
    # Update in database
    update_client_config(client_id, new_config)
    return jsonify({'message': 'Configuration updated'})

@app.route('/api/config/<client_id>/test', methods=['POST'])
def test_config(client_id):
    """Test configuration with sample code"""
    config = get_client_config(client_id)
    sample_code = request.json.get('code', '')
    
    # Run AI review with this config
    results = run_ai_review(sample_code, config)
    return jsonify(results)

def validate_config(config):
    """Validate configuration structure"""
    required_fields = ['ai_review', 'critical_words']
    return all(field in config for field in required_fields)
```

---

## 🎛️ **Web Dashboard for Configuration**

### **1. React Configuration Component**
```jsx
// ConfigurationDashboard.jsx
import React, { useState, useEffect } from 'react';

function ConfigurationDashboard({ clientId }) {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchConfig();
  }, [clientId]);

  const fetchConfig = async () => {
    const response = await fetch(`/api/config/${clientId}`);
    const data = await response.json();
    setConfig(data);
    setLoading(false);
  };

  const updateConfig = async (newConfig) => {
    await fetch(`/api/config/${clientId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newConfig)
    });
    await fetchConfig();
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="config-dashboard">
      <h2>Configuration for {config.client_name}</h2>
      
      {/* AI Review Settings */}
      <section>
        <h3>🤖 AI Review Settings</h3>
        <label>
          AI Models:
          <select 
            value={config.ai_review.models[0]}
            onChange={(e) => updateConfig({
              ...config,
              ai_review: {
                ...config.ai_review,
                models: [e.target.value]
              }
            })}
          >
            <option value="bedrock-nova-micro">Nova Micro (Cost-effective)</option>
            <option value="bedrock-claude-v3">Claude v3 (Advanced)</option>
          </select>
        </label>
        
        <label>
          Languages:
          <MultiSelect
            options={['python', 'javascript', 'java', 'c++', 'go']}
            value={config.ai_review.languages}
            onChange={(languages) => updateConfig({
              ...config,
              ai_review: { ...config.ai_review, languages }
            })}
          />
        </label>
      </section>

      {/* Critical Words Settings */}
      <section>
        <h3>🛡️ Critical Words Detection</h3>
        <label>
          Threshold:
          <input
            type="number"
            value={config.critical_words.threshold}
            onChange={(e) => updateConfig({
              ...config,
              critical_words: {
                ...config.critical_words,
                threshold: parseInt(e.target.value)
              }
            })}
          />
        </label>
        
        <label>
          Custom Words:
          <textarea
            value={config.critical_words.custom_words.join('\n')}
            onChange={(e) => updateConfig({
              ...config,
              critical_words: {
                ...config.critical_words,
                custom_words: e.target.value.split('\n').filter(Boolean)
              }
            })}
          />
        </label>
      </section>

      {/* Test Configuration */}
      <section>
        <h3>🧪 Test Configuration</h3>
        <textarea 
          placeholder="Paste sample code to test configuration..."
          id="test-code"
        />
        <button onClick={testConfig}>Test Configuration</button>
      </section>
    </div>
  );
}
```

---

## 📊 **Pricing Based on Configuration**

### **Configuration Tiers**
```python
# pricing.py
def calculate_price(config):
    """Calculate monthly price based on configuration"""
    base_price = 0
    
    # Plan-based pricing
    plan = config.get('plan', 'free')
    if plan == 'professional':
        base_price = 29
    elif plan == 'enterprise':
        base_price = 99
    
    # Add-ons
    ai_models = config.get('ai_review', {}).get('models', [])
    if 'bedrock-claude-v3' in ai_models:
        base_price += 20  # Premium AI model
    
    team_size = config.get('team', {}).get('size', 10)
    if team_size > 50:
        base_price += (team_size - 50) * 2  # $2 per developer over 50
    
    # Enterprise features
    if config.get('enterprise', {}).get('audit_logging'):
        base_price += 10
    if config.get('enterprise', {}).get('compliance_reporting'):
        base_price += 15
    
    return base_price

# Example usage
startup_config = load_config('startup_team')
startup_price = calculate_price(startup_config)  # $29

enterprise_config = load_config('enterprise_bank')  
enterprise_price = calculate_price(enterprise_config)  # $144
```

---

## 🚀 **Easy Setup for New Clients**

### **1. Client Onboarding Script**
```bash
#!/bin/bash
# setup_new_client.sh

CLIENT_NAME=$1
PLAN=$2

echo "🚀 Setting up new client: $CLIENT_NAME"

# Create client configuration
cat > config/${CLIENT_NAME}.yml << EOF
client_name: "$CLIENT_NAME"
plan: "$PLAN"

ai_review:
  enabled: true
  models: ["bedrock-nova-micro"]
  languages: ["python", "javascript"]
  
critical_words:
  enabled: true
  threshold: 10
  
team:
  size: 10
  experience_level: "mixed"
EOF

echo "✅ Configuration created: config/${CLIENT_NAME}.yml"
echo "🔗 Setup GitHub webhooks for this client"
echo "📧 Send welcome email with setup instructions"
```

### **2. Self-Service Setup Page**
```html
<!-- setup.html -->
<div class="setup-wizard">
  <h1>🚀 Set Up Your AI Code Reviewer</h1>
  
  <div class="step">
    <h3>Step 1: Choose Your Plan</h3>
    <div class="plans">
      <div class="plan" data-plan="professional">
        <h4>Professional - $29/month</h4>
        <ul>
          <li>Unlimited repositories</li>
          <li>All programming languages</li>
          <li>Standard AI models</li>
        </ul>
      </div>
      <div class="plan" data-plan="enterprise">
        <h4>Enterprise - $99/month</h4>
        <ul>
          <li>Advanced AI models</li>
          <li>Custom configurations</li>
          <li>Priority support</li>
        </ul>
      </div>
    </div>
  </div>
  
  <div class="step">
    <h3>Step 2: Configure Settings</h3>
    <label>Programming Languages:</label>
    <input type="checkbox" value="python"> Python
    <input type="checkbox" value="javascript"> JavaScript
    <input type="checkbox" value="java"> Java
    
    <label>Team Size:</label>
    <input type="number" id="team-size" value="10">
    
    <label>Critical Words Threshold:</label>
    <input type="range" id="threshold" min="5" max="20" value="10">
  </div>
  
  <div class="step">
    <h3>Step 3: Connect GitHub</h3>
    <button onclick="connectGitHub()">🔗 Connect GitHub Account</button>
  </div>
</div>
```

**This configuration system makes your solution adaptable to any client's needs! 🎯**