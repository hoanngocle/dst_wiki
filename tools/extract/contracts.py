from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True, order=True)
class EntityKey:
    namespace: str
    prefab_id: str


@dataclass(frozen=True, order=True)
class SourceRef:
    source_id: str
    kind: str
    path: str
    version: str
    sha256: str


@dataclass(frozen=True)
class Fact:
    kind: str
    subject: EntityKey
    payload: Dict[str, Any]
    source: SourceRef
    confidence: float
    locator: str = ""


@dataclass(frozen=True)
class FactBundle:
    schema_version: int
    sources: List[SourceRef] = field(default_factory=list)
    facts: List[Fact] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)


def _sort_key(fact: Fact):
    return (fact.subject.namespace, fact.subject.prefab_id, fact.kind, fact.locator, json.dumps(fact.payload, ensure_ascii=False, sort_keys=True))


def dump_bundle(path: Path, bundle: FactBundle) -> None:
    data = {
        "schema_version": bundle.schema_version,
        "sources": [asdict(v) for v in sorted(bundle.sources)],
        "facts": [
            {
                **asdict(v),
                "subject": asdict(v.subject),
                "source": asdict(v.source),
            }
            for v in sorted(bundle.facts, key=_sort_key)
        ],
        "errors": sorted(bundle.errors, key=lambda v: json.dumps(v, sort_keys=True)),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_bundle(path: Path) -> FactBundle:
    data = json.loads(path.read_text(encoding="utf-8"))
    sources = {v["source_id"]: SourceRef(**v) for v in data["sources"]}
    facts = []
    for value in data["facts"]:
        source_id = value["source"]["source_id"]
        facts.append(Fact(value["kind"], EntityKey(**value["subject"]), value["payload"], sources[source_id], value["confidence"], value["locator"]))
    return FactBundle(data["schema_version"], list(sources.values()), facts, data["errors"])
