# AGENTS.md - OpenCode Skills Project

## Project Overview

This is an OpenCode skills repository containing:
- **docx skill**: Word document creation, editing, and analysis
- **pdf skill**: PDF manipulation (extraction, form filling, merging)
- **pptx skill**: PowerPoint presentation handling
- **mcp-builder skill**: MCP (Model Context Protocol) server development
- **skill-creator skill**: Creating and evaluating OpenCode skills
- **theme-factory skill**: Document/presentation theming
- **ui-ux-pro-max skill**: UI/UX design intelligence

## Build/Lint/Test Commands

This project is primarily a skills repository with Python scripts and markdown documentation. There are no traditional build commands.

### Python Scripts

```bash
# Validate DOCX files
python scripts/office/validate.py document.docx

# Unpack DOCX for raw XML editing
python scripts/office/unpack.py document.docx output_dir/

# Repack edited DOCX
python scripts/office/pack.py input_dir/ output.docx

# Convert document formats
python scripts/office/soffice.py --headless --convert-to docx input.doc

# Extract PDF form fields
python scripts/extract_form_field_info.py input.pdf

# Fill PDF form fields
python scripts/fill_fillable_fields.py input.pdf output.pdf data.json
```

### Running Tests

There are no formal test suites in this project. Python scripts can be validated by:
1. Running them with sample inputs
2. Validating output against known good results
3. Using Python's built-in syntax checking: `python -m py_compile script.py`

### Linting

For Python code in this project, use basic syntax and style checks:
```bash
# Syntax check
python -m py_compile script.py

# Check imports
python -c "import script_name"
```

## Code Style Guidelines

### Language

All code and documentation comments must use **Simplified Chinese (简体中文)** as per global rules.

### Python Style

Follow PEP 8 with these project-specific conventions:

**Imports**
- Standard library imports first
- Third-party imports second
- Local imports last
- Blank line between groups
```python
import json
import sys
from typing import List, Optional

import pypdf

from .local_module import something
```

**Formatting**
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use blank lines sparingly to separate logical sections
- No trailing whitespace

**Type Annotations**
- Use type hints for function parameters and return values
- Prefer built-in types (List, Dict, Optional) over typing module equivalents
```python
def process_document(path: str) -> dict[str, Any]:
    ...
```

**Naming Conventions**
- Functions/variables: snake_case
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE
- Private functions: prefix with underscore

**Error Handling**
- Use specific exception types
- Include meaningful error messages
- Log errors appropriately

### JavaScript/TypeScript Style

For Node.js scripts (docx generation):

**Imports**
```javascript
const { Document, Packer } = require('docx');
```

**Formatting**
- Use 2 spaces for indentation
- Use single quotes for strings
- Add semicolons

### Markdown Documentation (SKILL.md)

Skills follow this structure:

```markdown
---
name: skill-name
description: "Description of when to use this skill..."
license: Proprietary
---

# Skill Title

## Overview
...

## Quick Reference
| Task | Approach |
|------|----------|
| ... | ... |

## Detailed Sections
...
```

**Formatting**
- Use ATX-style headers (# ## ###)
- Use fenced code blocks with language identifiers
- Tables for reference information
- Maximum line width: 100 characters in code blocks

### File Organization

```
skills/
  skill-name/
    SKILL.md          # Main skill definition
    LICENSE.txt       # License terms
    scripts/          # Python scripts
      __init__.py
      main_script.py
    reference/        # Additional documentation
```

## Working with Skills

### Trigger Patterns

Each skill has trigger patterns in its frontmatter. When users mention relevant keywords, the skill should be invoked. Example triggers:
- docx: ".docx", "Word doc", "document", "report"
- pdf: ".pdf", "PDF", "extract"
- pptx: ".pptx", "presentation", "slides"

### Skill Invocation

When a skill matches user request:
1. Announce: "Using [skill] to [purpose]"
2. Load the skill content
3. Follow skill-specific guidance in SKILL.md

## Important Notes

### Document Dimensions

When creating DOCX files with docx-js, always set page size explicitly:
```javascript
properties: {
  page: {
    size: { width: 12240, height: 15840 }, // US Letter in DXA
    margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } // 1 inch
  }
}
```

### XML Validation

After editing DOCX XML directly, always validate:
```bash
python scripts/office/validate.py document.docx
```

### Dependencies

Key Python dependencies used:
- pypdf: PDF manipulation
- openpyxl: Excel handling (when needed)

Key Node.js dependencies:
- docx: DOCX generation (docx-js package)

## Validation Checklist

Before considering work complete:
1. [ ] Python scripts pass syntax check
2. [ ] All imports resolve correctly
3. [ ] DOCX files validate after XML edits
4. [ ] Code comments are in Chinese
5. [ ] Error messages are in Chinese
