from flask import Blueprint, request, jsonify
from models import Run, DataQualityResult
from database import db
import uuid
import datetime

runs_bp = Blueprint("runs", __name__)

@runs_bp.route("/runs/<run_id>/dq_results", methods=["POST"])
def post_dq_results(run_id):
    data = request.json
    
    # We shouldn't necessarily enforce that Run already exists if OpenLineage is async
    # But let's assume it exists or we just insert it.
    
    # Actually the Run might not exist if OpenLineage START hasn't been processed.
    # In this mini-system, OpenLineage is synchronous via HTTP.
    
    dataset_id = data.get("dataset_id")
    dq_results = data.get("dq_results", {})
    
    try:
        for rule_name, rule_data in dq_results.items():
            dq_res = DataQualityResult(
                id=str(uuid.uuid4()),
                run_id=run_id,
                dataset_id=dataset_id,
                rule_name=rule_name,
                success=rule_data.get("success", False),
                observed_value=str(rule_data.get("observed_value", "")),
                created_at=datetime.datetime.utcnow()
            )
            db.session.add(dq_res)
            
        db.session.commit()
        return jsonify({"message": "DQ results saved", "run_id": run_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
