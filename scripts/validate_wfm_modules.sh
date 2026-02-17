#!/bin/bash
# Quick validation script for NSP Workflow Manager modules

echo "================================================"
echo "NSP Workflow Manager Modules - Validation Suite"
echo "================================================"
echo ""

# Check if ansible is installed
if ! command -v ansible &> /dev/null; then
    echo "❌ ERROR: Ansible is not installed"
    echo "   Install with: pip install ansible"
    exit 1
fi
echo "✅ Ansible is installed: $(ansible --version | head -1)"

# Check if nokia.nsp collection is installed
if ! ansible-galaxy collection list | grep -q "nokia.nsp"; then
    echo "❌ ERROR: nokia.nsp collection is not installed"
    echo "   Install with: ansible-galaxy collection install nokia.nsp"
    exit 1
fi
echo "✅ nokia.nsp collection is installed"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"

# Check if workflow_manager module exists
if [ ! -f "plugins/modules/workflow_manager.py" ]; then
    echo "❌ ERROR: workflow_manager.py not found"
    echo "   Expected location: plugins/modules/workflow_manager.py"
    exit 1
fi
echo "✅ workflow_manager.py found"

# Check if workflow_execute module exists
if [ ! -f "plugins/modules/workflow_execute.py" ]; then
    echo "❌ ERROR: workflow_execute.py not found"
    echo "   Expected location: plugins/modules/workflow_execute.py"
    exit 1
fi
echo "✅ workflow_execute.py found"

# Validate Python syntax
echo ""
echo "Validating Python syntax..."
python3 -m py_compile plugins/modules/workflow_manager.py 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ workflow_manager.py syntax is valid"
else
    echo "❌ workflow_manager.py has syntax errors"
    exit 1
fi

python3 -m py_compile plugins/modules/workflow_execute.py 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ workflow_execute.py syntax is valid"
else
    echo "❌ workflow_execute.py has syntax errors"
    exit 1
fi

# Check documentation files
echo ""
echo "Checking documentation..."
docs=(
    "docs/WFM_CICD_GUIDE.md"
    "docs/WFM_MODULES_README.md"
    "docs/WFM_IMPLEMENTATION_SUMMARY.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "✅ $doc found"
    else
        echo "❌ $doc not found"
    fi
done

# Check example playbook
if [ -f "tests/playbooks/workflow_manager_examples.yml" ]; then
    echo "✅ workflow_manager_examples.yml found"
    
    # Validate YAML syntax
    python3 -c "import yaml; yaml.safe_load(open('tests/playbooks/workflow_manager_examples.yml'))" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ workflow_manager_examples.yml is valid YAML"
    else
        echo "⚠️  workflow_manager_examples.yml may have YAML syntax issues"
    fi
else
    echo "❌ workflow_manager_examples.yml not found"
fi

# Module documentation check
echo ""
echo "Checking module documentation strings..."
if grep -q "DOCUMENTATION = r'''" plugins/modules/workflow_manager.py; then
    echo "✅ workflow_manager.py has DOCUMENTATION"
else
    echo "❌ workflow_manager.py missing DOCUMENTATION"
fi

if grep -q "EXAMPLES = r'''" plugins/modules/workflow_manager.py; then
    echo "✅ workflow_manager.py has EXAMPLES"
else
    echo "❌ workflow_manager.py missing EXAMPLES"
fi

if grep -q "RETURN = r'''" plugins/modules/workflow_manager.py; then
    echo "✅ workflow_manager.py has RETURN"
else
    echo "❌ workflow_manager.py missing RETURN"
fi

# Summary
echo ""
echo "================================================"
echo "Validation Complete!"
echo "================================================"
echo ""
echo "Next Steps:"
echo "1. Review documentation: docs/WFM_MODULES_README.md"
echo "2. Try examples: ansible-playbook tests/playbooks/workflow_manager_examples.yml"
echo "3. Read CI/CD guide: docs/WFM_CICD_GUIDE.md"
echo ""
echo "To test modules with your NSP:"
echo "  1. Configure inventory with NSP connection details"
echo "  2. Run: ansible-playbook tests/playbooks/workflow_manager_examples.yml -i inventory.yml"
echo ""
