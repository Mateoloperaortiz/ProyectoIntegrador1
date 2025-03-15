# Model Refactoring Plan

## Problem
The codebase has several model duplication issues:

1. **UUID Primary Key Duplication:**
   - Core app defines a `UUIDModel` abstract base class in `core/models.py`
   - Multiple models implement their own UUID fields instead of inheriting from this base class

2. **Timestamp Field Duplication:**
   - Core app defines a `TimeStampedModel` with `created_at` and `updated_at` fields
   - These fields are reimplemented in multiple models instead of using inheritance

3. **User Reference Inconsistencies:**
   - Inconsistent user field references across models:
     - Some models reference settings.AUTH_USER_MODEL (best practice)
     - Others reference 'users.CustomUser' directly (creates tight coupling)

## Solution

1. Refactor models to inherit from appropriate core abstract base classes:
   - Replace custom UUID fields with inheritance from `core.models.UUIDModel`
   - Replace timestamp fields with inheritance from `core.models.TimeStampedModel`
   - Standardize user references to use `settings.AUTH_USER_MODEL`

2. Create base migration scripts to handle these changes safely

## Implementation

### 1. Catalog Models Refactoring

```python
# catalog/models.py
from core.models import UUIDModel, TimeStampedModel

class AITool(UUIDModel, TimeStampedModel):
    # Remove id field, inherit from UUIDModel
    # Remove timestamp fields, inherit from TimeStampedModel
    name = models.CharField(max_length=255)
    # Other fields remain the same

class Rating(UUIDModel, TimeStampedModel):
    # Remove id field, inherit from UUIDModel
    # Remove created_at field, inherit from TimeStampedModel
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  
        on_delete=models.CASCADE,
        related_name='ai_ratings'
    )
    # Other fields remain the same
```

### 2. Interaction Models Refactoring

```python
# interaction/models.py
from core.models import UUIDModel, TimeStampedModel

class Conversation(UUIDModel, TimeStampedModel):
    # Remove id field, inherit from UUIDModel
    # Remove created_at and updated_at fields, inherit from TimeStampedModel
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use settings.AUTH_USER_MODEL instead of 'users.CustomUser'
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='interaction_conversations'
    )
    # Other fields remain the same

class Message(models.Model):
    # Not inheriting from UUIDModel since it doesn't have a UUID primary key
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    content = models.TextField()
    is_user = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=timezone.now)

class FavoritePrompt(UUIDModel, TimeStampedModel):
    # Remove id field, inherit from UUIDModel
    # Remove created_at field, inherit from TimeStampedModel
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Other fields remain the same

class SharedChat(UUIDModel, TimeStampedModel):
    # Remove id field, inherit from UUIDModel
    # Remove created_at field, inherit from TimeStampedModel
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_chats')
    # Other fields remain the same
```

## Benefits of Refactoring

1. **Reduced Code Duplication:**
   - Core functionality shared through inheritance
   - Easier to maintain (one implementation of common fields)
   - Reduced risk of inconsistencies across models

2. **Better Organization:**
   - Common code is in the appropriate place (core app)
   - Models follow the DRY principle

3. **Improved Maintainability:**
   - Changes to base classes automatically propagate to all derived models
   - New models will inherit consistent behavior

4. **Future Enhancements:**
   - Adding features like soft delete, audit trails, or versioning becomes easier
   - Admin UI can be more consistent

## Implementation Steps

1. Create comprehensive migrations to handle the refactoring
2. Test thoroughly to ensure data integrity is maintained
3. Update any code that relies on the refactored models

## Risks and Mitigation

1. **Data Integrity:**
   - Risk: Migrations might affect existing data
   - Mitigation: Test all migrations thoroughly in development before applying to production

2. **Breaking Changes:**
   - Risk: Refactoring might break code that relies on specific model attributes
   - Mitigation: Comprehensive test coverage to catch issues early

3. **Timing:**
   - Risk: Large model changes can be disruptive
   - Mitigation: Plan the rollout carefully, potentially splitting into smaller changes