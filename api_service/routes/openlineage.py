from flask import Blueprint, request, jsonify
from models import Run, Dataset, LineageEdge
from database import db
from datetime import datetime
import uuid

openlineage_bp = Blueprint("openlineage", __name__)

@openlineage_bp.route("/openlineage/events", methods=["POST"])
@openlineage_bp.route("/api/v1/lineage", methods=["POST"])
def receive_openlineage():
    try:
        event = request.get_json(silent=True) or {}

        event_type = event.get("eventType", "UNKNOWN")
        job = event.get("job", {})
        run_data = event.get("run", {})
        inputs = event.get("inputs", [])
        outputs = event.get("outputs", [])

        run_id = run_data.get("runId")
        if not run_id:
            # Try getting it from custom payload if standard one is missing
            run_id = event.get("run_id", str(uuid.uuid4()))

        job_name = job.get("name", "unknown_job")

        # Create or update Run
        run = Run.query.filter_by(id=run_id).first()
        if not run:
            run = Run(id=run_id, job_name=job_name, status=event_type)
            if event_type == "START":
                run.start_time = datetime.utcnow()
            db.session.add(run)
        else:
            run.status = event_type
            if event_type in ("COMPLETE", "FAIL"):
                run.end_time = datetime.utcnow()

        db.session.commit()

        # Helper to ensure dataset exists
        def ensure_dataset(dataset_name):
            ds = Dataset.query.filter_by(name=dataset_name).first()
            if not ds:
                ds = Dataset(id=str(uuid.uuid4()), name=dataset_name, uri=f"openlineage://{dataset_name}")
                db.session.add(ds)
                db.session.commit()
            return ds.id

        # We will parse inputs and outputs
        # Often inputs are present in START, outputs in COMPLETE
        
        # We need a cross product of inputs -> outputs to form edges
        input_ids = [ensure_dataset(i["name"]) for i in inputs]
        output_ids = [ensure_dataset(o["name"]) for o in outputs]
        
        # If we have both inputs and outputs in the event (or we accumulate them),
        # we can form edges. A simple way for this task:
        for in_id in input_ids:
            for out_id in output_ids:
                # check if edge already exists
                edge = LineageEdge.query.filter_by(run_id=run_id, source_dataset_id=in_id, target_dataset_id=out_id).first()
                if not edge:
                    edge = LineageEdge(
                        id=str(uuid.uuid4()),
                        source_dataset_id=in_id,
                        target_dataset_id=out_id,
                        run_id=run_id,
                        edge_type="INPUT_TO_OUTPUT"
                    )
                    db.session.add(edge)
                    
        db.session.commit()

        return jsonify({"status": "event processed", "run_id": run_id}), 200

    except Exception as e:
        db.session.rollback()
        print("Error processing OpenLineage event:", str(e))
        return jsonify({"error": str(e)}), 500