from flask import Blueprint, jsonify
from models import LineageEdge
from database import db

lineage_bp = Blueprint("lineage", __name__)

@lineage_bp.route("/datasets/<dataset_id>/lineage", methods=["GET"])
def get_lineage(dataset_id):
    try:
        upstream_edges = LineageEdge.query.filter_by(target_dataset_id=dataset_id).all()
        downstream_edges = LineageEdge.query.filter_by(source_dataset_id=dataset_id).all()

        upstream = [
            {"source_dataset_id": edge.source_dataset_id, "run_id": edge.run_id}
            for edge in upstream_edges
        ]
        
        downstream = [
            {"target_dataset_id": edge.target_dataset_id, "run_id": edge.run_id}
            for edge in downstream_edges
        ]

        return jsonify({
            "dataset_id": dataset_id,
            "upstream": upstream,
            "downstream": downstream
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500