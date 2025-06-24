format:
	ruff check ./ --fix

run_dashboard:
	python launch_dashboard.py

demo_simple_sample:
	python sample_script/trulens_simple_demo.py

demo_full_sample:
	python sample_script/trulens_demo.py