# Authentication Refactoring

## Problem
The project had duplicate authentication implementations across multiple apps:
- Three separate login/register implementations across `auth_app`, `users`, and `catalog`
- Duplicated login and register templates with minor differences
- Inconsistent URL references between the templates

## Solution
1. Centralized all authentication functionality in the `auth_app`
2. Made `users` and `catalog` auth views redirect to `auth_app` (already done)
3. Simplified templates by having app-specific templates extend the centralized ones from `auth_app`
4. Updated URL references to consistently use `auth_app:*` namespaces

## Changes Made
1. Templates:
   - Updated login templates in `users` and `catalog` to extend the `auth_app` version
   - Updated register templates in `users` and `catalog` to extend the `auth_app` version
   - Added deprecation notices to the duplicated templates

2. Comments: 
   - Added explanatory comments in URL configuration

## Future Work
1. Eventually, the duplicated templates could be fully removed once all references are updated
2. Consider centralizing the static assets related to authentication in `auth_app`
3. Review and update any hardcoded URL references in JavaScript files

## Testing
To test these changes:
1. Try logging in through each app's URL:
   - `/auth/login/`
   - `/users/login/`
   - `/catalog/login/`
2. Test registration through each app's URL:
   - `/auth/register/`
   - `/users/register/`
   - `/catalog/register/`
3. Verify that regardless of the entry point, you are properly authenticated and redirected