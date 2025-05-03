# Plan for Updating Pydantic Validators

This document outlines a plan for migrating from Pydantic V1-style validators to Pydantic V2-style validators in the Automated Product Data Scraper project.

## Background

During the implementation of Story 15, we encountered deprecation warnings related to Pydantic V1-style validators in the `config.py` file:

```
src/config.py:59: PydanticDeprecatedSince20: Pydantic V1 style `@validator` validators are deprecated. You should migrate to Pydantic V2 style `@field_validator` validators, see the migration guide for more details. Deprecated in Pydantic V2.0 to be removed in V3.0.
```

These validators are deprecated in Pydantic V2 and will be removed in V3.0. To ensure future compatibility, we need to migrate to the new validation approach.

## Current Implementation

The current implementation in `config.py` uses the deprecated `@validator` decorator:

```python
@validator("output_dir", "image_dir", pre=True)
def validate_directory(cls, v):
    # Validation logic
    return v
```

## Migration Plan

### 1. Dependency Analysis

1. **Check Pydantic Version**: Verify the current Pydantic version in use.
   ```bash
   pip show pydantic
   ```

2. **Identify All Validator Usage**: Scan the codebase for all instances of `@validator` decorators.
   ```bash
   grep -r "@validator" --include="*.py" .
   ```

### 2. Create a Test Branch

Create a dedicated branch for the migration to avoid disrupting ongoing development:

```bash
git checkout -b update-pydantic-validators
```

### 3. Update Validators

For each identified validator, update it to use the new `@field_validator` approach:

#### Before (V1 style):
```python
from pydantic import validator

class Config(BaseModel):
    output_dir: str
    image_dir: str

    @validator("output_dir", "image_dir", pre=True)
    def validate_directory(cls, v):
        # Validation logic
        return v
```

#### After (V2 style):
```python
from pydantic import field_validator, model_validator

class Config(BaseModel):
    output_dir: str
    image_dir: str

    @field_validator("output_dir", "image_dir", mode="before")
    @classmethod
    def validate_directory(cls, v):
        # Validation logic
        return v
```

Key changes:
- Import `field_validator` instead of `validator`
- Replace `pre=True` with `mode="before"`
- Add `@classmethod` decorator (required in V2)

### 4. Update Model Validators

For any model-level validators (those that operate on the entire model rather than specific fields), use the new `@model_validator` decorator:

#### Before (V1 style):
```python
@validator("*", pre=True)
def validate_all(cls, values):
    # Validation logic
    return values
```

#### After (V2 style):
```python
@model_validator(mode="before")
@classmethod
def validate_all(cls, data):
    # Validation logic
    return data
```

### 5. Testing

1. Run all existing tests to ensure the migration doesn't break functionality:
   ```bash
   python -m pytest
   ```

2. Add specific tests for the updated validators to verify they work as expected.

### 6. Documentation

1. Update any documentation that references the old validator approach.
2. Add a note to the migration in the project's changelog.

### 7. Deployment

1. Merge the changes back to the main branch after thorough testing.
2. Monitor the application after deployment to ensure no unexpected issues arise.

## Potential Risks and Mitigations

1. **Risk**: Breaking changes in validation behavior between V1 and V2.
   **Mitigation**: Thorough testing and careful review of the Pydantic migration guide.

2. **Risk**: Dependencies on specific Pydantic V1 features not covered by this plan.
   **Mitigation**: Comprehensive code review and testing.

3. **Risk**: Impact on other components that interact with validated models.
   **Mitigation**: Integration tests to verify system-wide behavior.

## Resources

- [Pydantic V2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [Field Validators Documentation](https://docs.pydantic.dev/latest/usage/validators/)
- [Model Validators Documentation](https://docs.pydantic.dev/latest/usage/model_validators/)
