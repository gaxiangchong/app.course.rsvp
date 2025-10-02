#!/usr/bin/env python3
"""
Migration script to add meal/pay options to Event and RSVP tables.

Adds to event table:
  - meal_option_enabled BOOLEAN DEFAULT 0
  - meal_option_remarks TEXT NULL
  - pay_at_venue_enabled BOOLEAN DEFAULT 0

Adds to rsvp table:
  - meal_opt_in BOOLEAN DEFAULT 0
"""

import os
import sys
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Ensure we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db  # noqa: E402


def column_exists(conn, table: str, column: str) -> bool:
    result = conn.execute(text(
        """
        SELECT COUNT(*) as count
        FROM pragma_table_info(:table)
        WHERE name = :column
        """
    ), {"table": table, "column": column})
    return result.fetchone()[0] > 0


def migrate_event_meal_pay_options() -> bool:
    print("🔄 Starting migration: add meal/pay options to Event and RSVP tables...")
    try:
        with app.app_context():
            with db.engine.connect() as conn:
                # EVENT: meal_option_enabled
                if not column_exists(conn, 'event', 'meal_option_enabled'):
                    print("📝 Adding column event.meal_option_enabled ...")
                    conn.execute(text("ALTER TABLE event ADD COLUMN meal_option_enabled BOOLEAN DEFAULT 0"))
                else:
                    print("✅ event.meal_option_enabled already exists")

                # EVENT: meal_option_remarks
                if not column_exists(conn, 'event', 'meal_option_remarks'):
                    print("📝 Adding column event.meal_option_remarks ...")
                    conn.execute(text("ALTER TABLE event ADD COLUMN meal_option_remarks TEXT"))
                else:
                    print("✅ event.meal_option_remarks already exists")

                # EVENT: pay_at_venue_enabled
                if not column_exists(conn, 'event', 'pay_at_venue_enabled'):
                    print("📝 Adding column event.pay_at_venue_enabled ...")
                    conn.execute(text("ALTER TABLE event ADD COLUMN pay_at_venue_enabled BOOLEAN DEFAULT 0"))
                else:
                    print("✅ event.pay_at_venue_enabled already exists")

                # RSVP: meal_opt_in
                if not column_exists(conn, 'rsvp', 'meal_opt_in'):
                    print("📝 Adding column rsvp.meal_opt_in ...")
                    conn.execute(text("ALTER TABLE rsvp ADD COLUMN meal_opt_in BOOLEAN DEFAULT 0"))
                else:
                    print("✅ rsvp.meal_opt_in already exists")

                conn.commit()
                print("🎉 Migration completed successfully!")
                return True
    except SQLAlchemyError as e:
        print(f"❌ Database error during migration: {e}")
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
    return False


if __name__ == "__main__":
    print("=" * 50)
    print("🍽️  Event/RSVP Meal & Pay Options Migration")
    print("=" * 50)
    success = migrate_event_meal_pay_options()
    if success:
        print("\nNext steps:")
#1) Restart your Flask app
#2) Re-test updating events and submitting RSVPs")
    else:
        print("\nMigration failed. Please review the error and try again.")
    print("=" * 50)


