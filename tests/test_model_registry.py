"""Tests for the bundled model context-window registry."""

import sys

from rich.console import Console

from codebase_token_counter.model_registry import PROVIDERS, load_model_registry
from codebase_token_counter.token_counter import create_context_window_table, main


EXPECTED_MODEL_IDS = {
    "gpt-6-astra",
    "gpt-5.6-sol",
    "gpt-5.6-terra",
    "gpt-5.6-luna",
    "claude-fable-5-1",
    "claude-opus-5",
    "claude-sonnet-5",
    "claude-haiku-4-5",
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
    "gemini-2.5-pro",
    "grok-4.6",
    "deepseek-v4-pro",
    "deepseek-v4-flash",
    "meta-llama/Llama-4-Scout-17B-16E-Instruct",
    "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
    "mistral-large-latest",
    "mistral-medium-latest",
    "devstral-latest",
    "devstral-small-latest",
}


def test_registry_contains_valid_curated_models():
    records = load_model_registry()
    model_ids = [record.model_id for record in records]

    assert set(model_ids) == EXPECTED_MODEL_IDS
    assert len(model_ids) == len(set(model_ids))
    assert {record.provider for record in records} == set(PROVIDERS)
    assert all(record.display_name.strip() for record in records)
    assert all(record.max_input_tokens > 0 for record in records)
    assert all(record.max_output_tokens > 0 for record in records)


def test_registry_representative_limits():
    records = {record.model_id: record for record in load_model_registry()}

    assert (records["gpt-6-astra"].max_input_tokens, records["gpt-6-astra"].max_output_tokens) == (922000, 128000)
    assert (records["claude-fable-5-1"].max_input_tokens, records["claude-fable-5-1"].max_output_tokens) == (1000000, 128000)
    assert (records["gemini-3.8-flash"].max_input_tokens, records["gemini-3.8-flash"].max_output_tokens) == (1048576, 65536)
    assert (records["deepseek-v4-pro"].max_input_tokens, records["deepseek-v4-pro"].max_output_tokens) == (1000000, 393216)
    assert (records["grok-4.6"].max_input_tokens, records["grok-4.6"].max_output_tokens) == (500000, 500000)
    assert records["meta-llama/Llama-4-Scout-17B-16E-Instruct"].max_input_tokens == 10000000


def test_cli_loads_registry_while_analyzing_repo_without_pricing_json(
    tmp_path, monkeypatch, capsys
):
    (tmp_path / "example.py").write_text("print('hello')", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["token-counter", ".", "--total"])

    assert not (tmp_path / "llm_pricing_data.json").exists()
    main()
    assert int(capsys.readouterr().out.strip()) > 0


def test_context_table_uses_registry_providers_and_display_names():
    records = load_model_registry()
    table, fits_entirely = create_context_window_table(1000, records)
    console = Console(record=True, width=180, color_system=None)
    console.print(table)
    rendered = console.export_text()

    for provider in PROVIDERS:
        assert provider in rendered
    for record in records:
        assert record.display_name in rendered
    assert fits_entirely == [record.display_name for record in records]
