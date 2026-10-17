# Maximo Automation Script - Reference Links

## Official IBM Documentation

### Main Documentation
- **IBM Maximo Automation Script Documentation**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/
  - Comprehensive guide to Maximo automation scripting
  - Complete API reference
  - Best practices and troubleshooting

### Key Sections

#### Introduction
- **What is an Automation Script?**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/introduction/what-is-an-automation-script
- **Script Components**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/introduction/components
- **Script Design Flow**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/introduction/script-design-flow
- **Script Compilation And Caching**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/introduction/script-compilation-and-caching

#### Core Concepts
- **Service Variable**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/core-concepts/service-variable
- **MBO Constants**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/core-concepts/mbo-constants
- **Errors and Warnings In Scripts**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/core-concepts/errors-and-warnings-in-scripts
- **Library Scripts**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/core-concepts/library-scripts

#### Object Scripts
- **Object Launchpoint**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/object-scripts/object-launchpoint
- **New Object Script**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/object-scripts/new-object-script
- **Duplicate Object Scripts**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/object-scripts/duplicate-object-scripts
- **Object Relation Scripts**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/object-scripts/object-relation-scripts

#### Attribute Scripts
- **Attribute Launchpoint**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/attribute-scripts

#### Integration Scripts
- **Integration Script Points**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/integration-scripts/integration-script-points
- **Object Structure Scripts**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/integration-scripts/object-structure-scripts
- **Publish Channel Scripts**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/integration-scripts/publish-channel-scripts
- **Enterprise Service Scripts**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/integration-scripts/enterprise-service-scripts
- **Invoke Channel Scripts**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/integration-scripts/invoke-channel-scripts
- **Endpoint Scripts**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/integration-scripts/endpoint-scripts

#### REST API Scripts
- **Script Handler**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/rest-api-scripts/script-handler
- **Object Structure Action**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/rest-api-scripts/object-structure-action
- **Object Structure Query Script**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/rest-api-scripts/object-structure-query-script
- **OSLC Select Attribute**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/rest-api-scripts/oslc-select-attribute

#### Other Scripts
- **Action Launchpoint**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/other-scripts/action-launchpoint
- **Condition Launchpoint**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/other-scripts/condition-launchpoint
- **Crontask Scripts**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/other-scripts/crontask-scripts

#### Troubleshooting & Best Practices
- **Scripting Best Practices**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/bestpractice/overview/
- **Debugging a Script**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/troubleshooting/debugging-a-script
- **Testing a Script**: https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/troubleshooting/testing-a-script

## Key Concepts from Official Documentation

### Implicit Variables
The following implicit variables are available in all scripts (from [official documentation](https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/introduction/components)):

| Variable | Type | Description |
|----------|------|-------------|
| `app` | String | The name of the Maximo application which initiated the script execution |
| `user` | String | userid of the user whose action initiated the script execution |
| `mbo` | psdi.mbo.Mbo | The current MBO in the context of the script execution |
| `mboname` | String | The name of the current MBO in the context of the script execution |
| `interactive` | boolean | Indicates whether the script is executed in an interactive or UI session |
| `onadd` | boolean | Indicates whether the MBO in the script is added (new MBO) |
| `onupdate` | boolean | Indicates whether the MBO in the script is updated (existing MBO) |
| `ondelete` | boolean | Indicates whether the MBO in the script context is deleted |
| `service` | com.ibm.tivoli.maximo.script.ScriptService | The global implicit var available to all scripts |
| `errorkey` | String | Error key for MXExceptions (deprecated - use service.error() instead) |
| `errorgroup` | String | Error group for MXExceptions (deprecated - use service.error() instead) |

### Variable Binding Metadata
When binding variables to MBO attributes, you can control validation and action behavior:

| Binding Metadata | Type | Description |
|------------------|------|-------------|
| **Suppress Validation** | Boolean | Sets NOVALIDATION flag - prevents field validation routine from being called |
| **Suppress Action** | Boolean | Sets NOACTION flag - prevents field action routine from being called |
| **Suppress Access Control** | Boolean | Sets NOACCESSCHECK flag - allows attribute modification regardless of readonly status |

### Launch Points
Supported launch points in Maximo automation scripts:

1. **Object Launch Point** - MBO initialization and save point logic
2. **Attribute Launch Point** - MBO attribute value modification (validation and action logic)
3. **Action Launch Point** - Actions used by Workflow, Escalation, UI Menu, UI Buttons
4. **Condition Launch Point** - Custom conditions used by Workflow conditions, Conditional UI

## Local Documentation Resources

### Available Documentation
- **Official Documentation (Local Copy)**: `OFFICIAL_DOCUMENTATION.md` - Local copy of key IBM documentation for offline reference
- **Naming Conventions**: `NAMING_CONVENTIONS.md` - Standard naming conventions for all automation scripts
- **Patterns Reference**: `maximo_script_patterns_reference.md` - Comprehensive patterns based on IBM best practices
- **Utility Library**: `maximo_utility_library.py` - Reusable functions for common operations
- **Header Template**: `script_header_template.py` - Standard script header template
- **Usage Guide**: `UTILITY_LIBRARY_README.md` - Utility library usage examples
- **Agent Context Guide**: `AGENT_CONTEXT_GUIDE.md` - Master guide for AI agents
- **Index**: `INDEX.md` - Quick navigation guide

## Quick Reference

### Most Common Implicit Variables
```python
# Application name
app = app  # String - Current Maximo application name

# User information
user = user  # String - Current user ID

# MBO context
mbo = mbo  # psdi.mbo.Mbo - Current MBO object
mboname = mboname  # String - Current MBO name

# Interactive mode
interactive = interactive  # boolean - True if UI session, False if background

# MBO state
onadd = onadd  # boolean - True if new MBO
onupdate = onupdate  # boolean - True if existing MBO is updated
ondelete = ondelete  # boolean - True if MBO is deleted

# Service object
service = service  # ScriptService - Global service object for errors, warnings, etc.
```

### Using Service Object
```python
# Error handling (recommended over errorkey/errorgroup)
service.error('Field Name', 'error message')
service.error('Field Name', 'error message', ['param1', 'param2'])

# Warnings
service.warning('Warning message')
```

## Notes

- Always refer to the official IBM documentation for the most up-to-date information
- This folder's documentation provides generic patterns and examples based on IBM best practices
- The official documentation is the authoritative source for API changes and new features
- Local patterns are generic and can be used across any Maximo project

