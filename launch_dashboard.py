#!/usr/bin/env python3
"""
Simple TruLens Dashboard Launcher
"""

from trulens.dashboard import run_dashboard


def main():
    print("🦑 Starting TruLens Dashboard...")

    # Set database URL
    db_url = "sqlite:///default.sqlite"
    print(f"📊 Using database: {db_url}")

    try:
        # Start dashboard with explicit settings
        process = run_dashboard(port=8501, address="localhost")
        print("✅ Dashboard started successfully!")
        print("🌐 Access at: http://localhost:8501")

        # Keep the process running
        process.join()

    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("💡 Try checking if port 8501 is available")


if __name__ == "__main__":
    main()
