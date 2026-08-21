from typing import List, Dict, Tuple
from app.models import Evidence, AIAsset, AssetStatus, Specificity, SourceType

UNCLASSIFIED_PROVIDER = "unclassified"
UNCLASSIFIED_AI_TYPE = "unclassified"

def correlate_evidence(evidence_items: List[Evidence]) -> List[AIAsset]:
    """Correlates list of Evidence records into aggregated AIAssets."""
    groups: Dict[Tuple[str, str, str], List[Evidence]] = {}
    unclassified_keys: set[Tuple[str, str, str]] = set()

    # 1. Group by application + provider + ai_type.
    # Evidence missing provider and/or ai_type is grouped under an
    # "unclassified" placeholder per application, rather than dropped,
    # so it still surfaces to reviewers as a PENDING_REVIEW asset.
    for ev in evidence_items:
        if not ev.application:
            continue

        provider = ev.provider if ev.provider else UNCLASSIFIED_PROVIDER
        ai_type = ev.ai_type if ev.ai_type else UNCLASSIFIED_AI_TYPE

        key = (ev.application, provider, ai_type)
        if key not in groups:
            groups[key] = []
        groups[key].append(ev)

        if not ev.provider or not ev.ai_type:
            unclassified_keys.add(key)

    assets: List[AIAsset] = []

    for (app, provider, ai_type), items in groups.items():
        # Calculate arithmetic confidence average rounded to 2 decimals
        conf_weights = [item.confidence_weight for item in items]
        avg_confidence = round(sum(conf_weights) / len(conf_weights), 2) if conf_weights else 0.0

        # Determine asset model value
        models = {item.model for item in items if item.model is not None}
        resolved_model = list(models)[0] if len(models) == 1 else None

        is_unclassified = (app, provider, ai_type) in unclassified_keys

        if is_unclassified:
            # Provider/ai_type could not be determined for at least one
            # evidence item in this group — cannot be DISCOVERED regardless
            # of confidence, source diversity, or specificity.
            status = AssetStatus.PENDING_REVIEW
            confidence_rationale = (
                "Pending review: evidence could not be fully classified "
                "(missing provider and/or ai_type), so discovery gates were not evaluated."
            )
        else:
            # Evaluate discovery gates
            c1 = avg_confidence >= 0.6

            source_types = {item.source_type for item in items if item.source_type != SourceType.CALL_RELATIONSHIP}
            c2 = len(source_types) >= 3

            c3 = any(item.specificity == Specificity.HIGH for item in items)

            failures = []
            if not c1:
                failures.append(f"insufficient confidence ({avg_confidence} < 0.6)")
            if not c2:
                failures.append(f"insufficient independent source types (found {len(source_types)}, requires 3)")
            if not c3:
                failures.append("no high-specificity evidence")

            if not failures:
                status = AssetStatus.DISCOVERED
                sorted_source_types = sorted(list(source_types))
                confidence_rationale = (
                    f"Discovered: Confidence of {avg_confidence} is >= 0.6, "
                    f"spans {len(source_types)} distinct source types ({', '.join(sorted_source_types)}), "
                    f"and contains high-specificity evidence."
                )
            else:
                status = AssetStatus.PENDING_REVIEW
                confidence_rationale = f"Pending review due to: {', '.join(failures)}."

        evidence_ids = [item.id for item in items]

        assets.append(
            AIAsset(
                application=app,
                provider=provider,
                ai_type=ai_type,
                model=resolved_model,
                status=status,
                confidence=avg_confidence,
                confidence_rationale=confidence_rationale,
                evidence_ids=evidence_ids
            )
        )

    return assets