import uuid
import pandas as pd
from typing import List, Dict, Set
from collections import defaultdict
import logging

from splink import Linker, SettingsCreator, DuckDBAPI
import splink.comparison_library as cl

from app.schemas.extraction import EntityMention
from app.schemas.resolution import CanonicalEntity, ResolutionStatus, MentionProvenance, ResolutionExplanation

logger = logging.getLogger(__name__)

# UNTRAINED PROTOTYPE NOTE: 
# The match_probability scores produced by Splink are currently using a default prior
# and untrained m/u probabilities. They serve as a relative similarity score rather
# than a calibrated real-world probability.
PROTOTYPE_DECISION_THRESHOLD = 0.5

def _deterministic_structured_resolve(mentions: List[EntityMention], etype: str) -> List[CanonicalEntity]:
    # Deterministic matching is safe for PHONE, VEHICLE, UPI_ACCOUNT, CASE
    # because these are structured, high-cardinality identifiers which, 
    # when fully normalized, uniquely and definitively point to a single entity.
    groups = defaultdict(list)
    for m in mentions:
        groups[m.normalized_value].append(m)
        
    results = []
    for norm_val, m_list in groups.items():
        aliases = list(set(m.text for m in m_list if m.text != norm_val))
        prov = [MentionProvenance(mention_id=m.mention_id, record_id=m.record_id) for m in m_list]
        
        explanation = ResolutionExplanation(
            decision="CONFIRMED",
            deterministic_match=True,
            decision_threshold=1.0,
            matching_features={
                "exact_identifier_match": True,
                "normalized_value": norm_val
            }
        )
        
        results.append(CanonicalEntity(
            entity_id=f"{etype[:3].upper()}-{uuid.uuid4().hex[:6]}",
            entity_type=etype,
            canonical_name=norm_val,
            aliases=aliases,
            resolution_status=ResolutionStatus.CONFIRMED,
            resolution_score=1.0, # Deterministic strength
            source_mentions=prov,
            resolution_explanation=explanation
        ))
    return results

def _extract_splink_features(m: EntityMention):
    text = m.normalized_value.lower().strip()
    parts = text.split()
    first = parts[0] if parts else ""
    last = parts[-1] if len(parts) > 1 else ""
    return {
        "unique_id": m.mention_id,
        "normalized_value": text,
        "text": m.text,
        "first_name": first,
        "last_name": last,
        "first_init": first[0] if first else "",
        "first_word": first
    }

def _probabilistic_splink_resolve(mentions: List[EntityMention], etype: str) -> List[CanonicalEntity]:
    if not mentions:
        return []
        
    if len(mentions) == 1:
        m = mentions[0]
        prov = [MentionProvenance(mention_id=m.mention_id, record_id=m.record_id)]
        return [CanonicalEntity(
            entity_id=f"{etype[:3].upper()}-{uuid.uuid4().hex[:6]}",
            entity_type=etype,
            canonical_name=m.normalized_value,
            aliases=[m.text] if m.text != m.normalized_value else [],
            resolution_status=ResolutionStatus.UNRESOLVED,
            resolution_score=0.0,
            source_mentions=prov,
            resolution_explanation=ResolutionExplanation(
                decision="UNRESOLVED",
                deterministic_match=False,
                matching_features={"reason": "singleton_mention"}
            )
        )]

    df = pd.DataFrame([_extract_splink_features(m) for m in mentions])
    
    comparisons = [
        cl.JaroWinklerAtThresholds("normalized_value", [0.85, 0.7])
    ]
    
    if etype == "PERSON":
        comparisons.append(cl.ExactMatch("last_name"))
        blocking_rules = [
            "l.normalized_value = r.normalized_value",
            "l.first_init = r.first_init and l.last_name = r.last_name"
        ]
    else:
        blocking_rules = [
            "l.normalized_value = r.normalized_value",
            "l.first_word = r.first_word"
        ]
        
    settings = SettingsCreator(
        link_type="dedupe_only",
        probability_two_random_records_match=0.1, # Prototype default prior
        blocking_rules_to_generate_predictions=blocking_rules,
        comparisons=comparisons,
        retain_matching_columns=True
    )
    
    db_api = DuckDBAPI()
    results = []
    
    try:
        linker = Linker(df, settings, db_api=db_api)
        df_predict = linker.inference.predict(threshold_match_probability=0.0).as_pandas_dataframe()
        
        edges = []
        for _, row in df_predict.iterrows():
            if row["match_probability"] > PROTOTYPE_DECISION_THRESHOLD:
                edges.append((row["unique_id_l"], row["unique_id_r"], row["match_probability"]))
                
        edges.sort(key=lambda x: x[2], reverse=True)
        
        clusters = {m.mention_id: {m.mention_id} for m in mentions}
        cluster_scores = {m.mention_id: 1.0 for m in mentions}
        
        for u, v, prob in edges:
            cu, cv = None, None
            for c_id, c_set in clusters.items():
                if u in c_set: cu = c_id
                if v in c_set: cv = c_id
            
            if cu != cv and cu is not None and cv is not None:
                valid = True
                for n1 in clusters[cu]:
                    for n2 in clusters[cv]:
                        if n1 == n2: continue
                        edge_exists = False
                        for eu, ev, eprob in edges:
                            if (eu == n1 and ev == n2) or (eu == n2 and ev == n1):
                                edge_exists = True
                                break
                        if not edge_exists:
                            valid = False
                            break
                    if not valid: break
                
                if valid:
                    clusters[cu] = clusters[cu].union(clusters[cv])
                    cluster_scores[cu] = min(cluster_scores[cu], prob)
                    del clusters[cv]

        mention_dict = {m.mention_id: m for m in mentions}
        for comp_id, m_set in clusters.items():
            m_list = [mention_dict[mid] for mid in m_set]
            canonical_name = max(set(m.normalized_value for m in m_list), key=len)
            aliases = list(set(m.text for m in m_list if m.text != canonical_name))
            prov = [MentionProvenance(mention_id=m.mention_id, record_id=m.record_id) for m in m_list]
            
            if len(m_list) > 1:
                status = ResolutionStatus.CANDIDATE
                score = cluster_scores[comp_id]
                explanation = ResolutionExplanation(
                    decision="PROTOTYPE_PROBABILISTIC_MATCH",
                    deterministic_match=False,
                    match_probability=score,
                    decision_threshold=PROTOTYPE_DECISION_THRESHOLD,
                    matching_features={
                        "model_calibrated": False,
                        "blocking_rules_applied": blocking_rules,
                        "pairwise_consistency_verified": True
                    }
                )
            else:
                status = ResolutionStatus.UNRESOLVED
                score = 0.0
                explanation = ResolutionExplanation(
                    decision="UNRESOLVED",
                    deterministic_match=False,
                    matching_features={"reason": "insufficient_similarity_or_blocked"}
                )
            
            results.append(CanonicalEntity(
                entity_id=f"{etype[:3].upper()}-{uuid.uuid4().hex[:6]}",
                entity_type=etype,
                canonical_name=canonical_name,
                aliases=aliases,
                resolution_status=status,
                resolution_score=score,
                source_mentions=prov,
                resolution_explanation=explanation
            ))
            
    except Exception as e:
        logger.warning(f"Splink resolution failed for {etype}: {e}. Falling back to unresolved.")
        for m in mentions:
            prov = [MentionProvenance(mention_id=m.mention_id, record_id=m.record_id)]
            results.append(CanonicalEntity(
                entity_id=f"{etype[:3].upper()}-{uuid.uuid4().hex[:6]}",
                entity_type=etype,
                canonical_name=m.normalized_value,
                aliases=[m.text] if m.text != m.normalized_value else [],
                resolution_status=ResolutionStatus.UNRESOLVED,
                resolution_score=0.0,
                source_mentions=prov,
                resolution_explanation=ResolutionExplanation(
                    decision="UNRESOLVED",
                    deterministic_match=False,
                    matching_features={"reason": "splink_pipeline_failure"}
                )
            ))
        
    return results

def resolve_entities(mentions: List[EntityMention]) -> List[CanonicalEntity]:
    canonical_entities = []
    grouped = defaultdict(list)
    for m in mentions:
        grouped[m.entity_type].append(m)
        
    for etype, type_mentions in grouped.items():
        if etype in ["PHONE", "VEHICLE", "UPI_ACCOUNT", "CASE"]:
            canonical_entities.extend(_deterministic_structured_resolve(type_mentions, etype))
        else:
            canonical_entities.extend(_probabilistic_splink_resolve(type_mentions, etype))
            
    return canonical_entities
