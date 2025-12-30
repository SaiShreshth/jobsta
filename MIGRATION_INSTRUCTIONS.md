# Database Migration Instructions

## Issue
The database schema has been updated to include new fields in the `job` table:
- `apply_url` (required)
- `deadline` (optional)
- `status` (default: 'active')
- `updated_at` (timestamp)

## Solution

Run the migration to add these columns to your database:

```bash
flask db upgrade
```

Or if using Python directly:

```bash
python -m flask db upgrade
```

## Alternative: Manual Migration

If Flask-Migrate is not working, you can run the migration manually using the script:

```bash
python scripts/run_migration.py
```

## Fallback Code

The application has been updated with defensive code that will work even if the migration hasn't been run yet. However, you should run the migration as soon as possible to enable all features:

- Job creation with apply URLs
- Deadline tracking
- Job status management (active/deleted/archived)
- Edit and delete functionality

## Verify Migration

After running the migration, verify it worked by checking:

```bash
flask db current
```

You should see: `c7d8e9f0a1b2 (head)`

