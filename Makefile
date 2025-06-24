format:
	ruff check ./ --fix

run_dashboard:
	uv run python launch_dashboard.py

demo_simple_sample:
	uv run python sample_script/trulens_simple_demo.py

demo_full_sample:
	uv run python sample_script/trulens_demo.py