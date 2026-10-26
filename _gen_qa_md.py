#!/usr/bin/env python3
"""Thin wrapper — canonical script lives in the skill folder."""
import runpy

runpy.run_path(
    "/home/hzhan069/code/.cursor/skills/cpp-interview-card/scripts/gen_qa_md.py",
    run_name="__main__",
)
