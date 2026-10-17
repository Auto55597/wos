from fastapi import FastAPI, Header, HTTPException, Query

from config_loader import ConfigurationError, load_mapping_rules
from engine import TranslationEngine
from schema import RawPayload, UnifiedContext

app = FastAPI(title="Workspace OS Core Engine")
engine = TranslationEngine()


@app.post("/api/v1/ingest", response_model=UnifiedContext)
def ingest(
    payload: RawPayload,
    mapping_rule_id: str | None = Query(default=None),
    rule_header: str | None = Header(default=None, alias="X-Mapping-Rule"),
) -> UnifiedContext:
    try:
        rules = load_mapping_rules()
    except ConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    selected_id = mapping_rule_id or rule_header
    if selected_id is None:
        if len(rules) != 1:
            raise HTTPException(
                status_code=400,
                detail="Provide mapping_rule_id when configuration has zero or multiple rules",
            )
        selected_id = next(iter(rules))

    mapping = rules.get(selected_id)
    if mapping is None:
        raise HTTPException(status_code=404, detail="Mapping rule not found")

    return engine.transform(payload, mapping)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "engine_status": engine.status}
