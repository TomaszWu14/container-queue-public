"""Gotowe workflow n8n (`deploy/n8n/*.json`) importują się poprawnie: poprawny JSON, każde połączenie
wskazuje istniejący node, a workflow przyjmujący zdarzenia z aplikacji sprawdza podpis HMAC
(porównanie stałoczasowe) przed jakąkolwiek akcją."""
import json
import pathlib

import pytest

N8N = pathlib.Path(__file__).resolve().parents[2] / "deploy" / "n8n"
FILES = sorted(N8N.glob("*.json"))


def test_there_are_workflows():
    assert {f.name for f in FILES} >= {"kontrola-danych.json", "zdarzenie-do-teams.json"}


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_connections_point_to_existing_nodes(path):
    wf = json.loads(path.read_text(encoding="utf-8"))
    names = {n["name"] for n in wf["nodes"]}
    assert len(names) == len(wf["nodes"])                      # nazwy unikalne (połączenia idą po nazwie)
    for source, outputs in wf["connections"].items():
        assert source in names, source
        for branch in outputs["main"]:
            for link in branch:
                assert link["node"] in names, link["node"]


def test_event_workflow_verifies_signature_before_acting():
    wf = json.loads((N8N / "zdarzenie-do-teams.json").read_text(encoding="utf-8"))
    nodes = {n["name"]: n for n in wf["nodes"]}
    hook = nodes["Zdarzenie z TIMPORYE"]
    assert hook["type"] == "n8n-nodes-base.webhook" and hook["parameters"]["options"]["rawBody"] is True
    first = wf["connections"]["Zdarzenie z TIMPORYE"]["main"][0][0]["node"]
    code = nodes[first]["parameters"]["jsCode"]
    assert "timingSafeEqual" in code and "x-timporye-signature" in code and "throw new Error" in code
    assert not any("TEAMS" in json.dumps(n["parameters"]) and n["name"] == first for n in wf["nodes"])
