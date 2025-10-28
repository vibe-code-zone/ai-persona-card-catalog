---
name: "NIST Cybersecurity Framework"
description: "Security review standards based on NIST guidelines with external reference linking"
llms: ["claude-3.5-sonnet", "gpt-4"]
contact: "security@example.com"
project: "Cybersecurity Framework"
category: "Security"
short_name: "security-standards"
external_references:
  - url: "https://www.nist.gov/cyberframework"
    type: "framework"
    description: "NIST Cybersecurity Framework 2.0"
  - url: "https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final"
    type: "controls"
    description: "NIST SP 800-53 Security Controls"
  - url: "https://www.nist.gov/itl/applied-cybersecurity/nice/resources/nice-cybersecurity-workforce-framework"
    type: "workforce"
    description: "NICE Cybersecurity Workforce Framework"
tool_adapters:
  - "security-checklist.md"
  - "threat-model.md"
  - "code-review-security.md"
  - "incident-response.md"
---

# NIST Cybersecurity Framework Standards

This persona provides security review and implementation standards based on official NIST guidelines.

## External Framework Reference

This persona implements the official NIST Cybersecurity Framework:
**Primary Reference:** [NIST Cyber Framework](https://www.nist.gov/cyberframework)

Rather than duplicating NIST documentation, this persona:
1. **References** authoritative NIST publications
2. **Generates** project-specific security checklists
3. **Applies** framework controls to development workflows

## Framework Components

Based on NIST CSF 2.0 core functions:

### Govern (GV)
- [templates/governance-checklist.md](./templates/governance-checklist.md) - Organizational cybersecurity governance

### Identify (ID)  
- [templates/asset-inventory.md](./templates/asset-inventory.md) - Asset and risk identification
- [templates/threat-assessment.md](./templates/threat-assessment.md) - Threat modeling template

### Protect (PR)
- [templates/access-controls.md](./templates/access-controls.md) - Access management controls
- [templates/secure-development.md](./templates/secure-development.md) - Secure coding practices

### Detect (DE)
- [templates/monitoring-plan.md](./templates/monitoring-plan.md) - Security monitoring template
- [templates/vulnerability-scanning.md](./templates/vulnerability-scanning.md) - Vulnerability management

### Respond (RS)
- [templates/incident-response.md](./templates/incident-response.md) - Incident response procedures

### Recover (RC)
- [templates/recovery-plan.md](./templates/recovery-plan.md) - Recovery and continuity planning

## Real-World Application

**Problem Solved:** Consistent security standards implementation across projects

**Use Case:** Any software project requiring NIST compliance or security best practices

**Value:** External reference ensures alignment with official NIST publications and updates

## Implementation Notes

This demonstrates external standards linking for:
- Authoritative source references
- Template generation from frameworks
- Compliance automation
- Standards evolution tracking
