import logging
from sqlalchemy.orm import Session
from app.db.models import SourceSystem, SourceDataset

logger = logging.getLogger(__name__)

SYNTHETIC_SOURCES = [
    {
        "system_id": "SYS_CCTNS_DEMO",
        "name": "CCTNS (Synthetic/Demo)",
        "agency": "Police",
        "classification": "DEMO",
        "datasets": [
            {"dataset_id": "DS_FIR_DEMO", "description": "Synthetic FIR dataset"},
            {"dataset_id": "DS_ARREST_DEMO", "description": "Synthetic Arrest dataset"},
            {"dataset_id": "DS_UNSTRUCTURED", "description": "Demo Unstructured Dataset"}
        ]
    },
    {
        "system_id": "SYS_ECOURTS_DEMO",
        "name": "e-Courts (Synthetic/Demo)",
        "agency": "Judiciary",
        "classification": "DEMO",
        "datasets": [
            {"dataset_id": "DS_COURT_HEARING_DEMO", "description": "Synthetic Court Hearings"}
        ]
    },
    {
        "system_id": "SYS_FINANCIAL_DEMO",
        "name": "Financial / CDR (Synthetic/Demo)",
        "agency": "Telecom/Bank",
        "classification": "DEMO",
        "datasets": [
            {"dataset_id": "NETRA-DEMO-CDR", "description": "Synthetic Call Data Records"},
            {"dataset_id": "NETRA-DEMO-TXN", "description": "Synthetic Financial Transactions"},
            {"dataset_id": "NETRA-DEMO-VEHICLE", "description": "Synthetic Vehicle Records (Unmapped)"},
            {"dataset_id": "NETRA-UNKNOWN", "description": "Intentionally unmapped dataset for testing"}
        ]
    }
]

def initialize_registry(db: Session):
    """Seed the database with synthetic source systems and datasets if they don't exist."""
    for source in SYNTHETIC_SOURCES:
        sys_id = source["system_id"]
        existing_sys = db.query(SourceSystem).filter(SourceSystem.system_id == sys_id).first()
        if not existing_sys:
            new_sys = SourceSystem(
                system_id=sys_id,
                name=source["name"],
                agency=source["agency"],
                classification=source["classification"]
            )
            db.add(new_sys)
            db.commit() # Commit to ensure FK availability
            logger.info(f"Initialized source system: {sys_id}")
        
        for ds in source["datasets"]:
            ds_id = ds["dataset_id"]
            existing_ds = db.query(SourceDataset).filter(SourceDataset.dataset_id == ds_id).first()
            if not existing_ds:
                new_ds = SourceDataset(
                    dataset_id=ds_id,
                    system_id=sys_id,
                    description=ds["description"]
                )
                db.add(new_ds)
                db.commit() # Commit to ensure FK availability
                logger.info(f"Initialized dataset: {ds_id}")
    
def get_source_dataset(db: Session, dataset_id: str) -> SourceDataset:
    return db.query(SourceDataset).filter(SourceDataset.dataset_id == dataset_id).first()
