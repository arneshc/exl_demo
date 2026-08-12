import os
import sys
import json
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from orchestrator.invoke import invoke_agent, _store, _skills_loader

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")

class OrchestratorHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[HTTP] {self.address_string()} - {format % args}", flush=True)

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            body = {}

        if path == "/agent/invoke":
            response_data = invoke_agent(body)
            status_code = 200 if response_data["status"] != "ERROR" else 500
            self._set_headers(status_code)
            self.wfile.write(json.dumps(response_data, indent=2).encode("utf-8"))

        elif path.startswith("/case/") and path.endswith("/engage"):
            parts = path.split("/")
            case_id = parts[2]
            case = _store.get_case(case_id)
            if not case:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": f"Case {case_id} not found"}).encode("utf-8"))
                return
            
            _store.update_case(case_id, {"status": "ENGAGEMENT_INITIATED"})
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "ENGAGEMENT_INITIATED", "caseId": case_id}).encode("utf-8"))

        elif path.startswith("/case/") and path.endswith("/approve"):
            parts = path.split("/")
            case_id = parts[2]
            approver_id = body.get("approverId", "REP-101")
            decision = body.get("decision", "APPROVED")
            comments = body.get("comments")

            case = _store.get_case(case_id)
            if not case:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": f"Case {case_id} not found"}).encode("utf-8"))
                return

            _store.update_case(case_id, {"status": "SENT"})
            approval_record = {
                "approvalId": f"APP-{case_id}",
                "targetId": case_id,
                "approverRole": "SERVICING_REP",
                "approverId": approver_id,
                "decision": decision,
                "comments": comments,
                "timestamp": json.dumps(case.get("updatedAt"))
            }

            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "SENT", "approvalRecord": approval_record}).encode("utf-8"))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        # Static Page Routes
        if path in ["/", "/index.html"]:
            self._serve_static_file("index.html")
            return
        elif path in ["/portfolio-view", "/portfolio.html"]:
            self._serve_static_file("portfolio.html")
            return
        elif path in ["/audit-view", "/audit.html"]:
            self._serve_static_file("audit.html")
            return

        # API Endpoints
        if path == "/queue":
            rep_id = query.get("repId", ["REP-101"])[0]
            cases_list = list(_store.cases.values())
            
            sorted_cases = sorted(
                cases_list,
                key=lambda x: (
                    0 if x.get("storyTag") == "Flight Risk" else (1 if x.get("storyTag") == "Buyer's Remorse" else (2 if x.get("storyTag") == "Low Lapse / Growth Candidate" else 3)),
                    -(x.get("retentionValueUsd") or 0)
                )
            )

            queue_cases = [
                {
                    "caseId": c.get("caseId"),
                    "policyId": c.get("policyId"),
                    "holderName": c.get("holderName"),
                    "storyTag": c.get("storyTag"),
                    "priorityRank": idx + 1,
                    "urgencyLevel": c.get("urgencyLevel", "P1-High" if c.get("storyTag") == "Flight Risk" else "P2-Medium"),
                    "retentionValueUsd": c.get("retentionValueUsd") or c.get("faceAmount"),
                    "recommendedAction": c.get("recommendedAction"),
                    "status": c.get("status")
                }
                for idx, c in enumerate(sorted_cases)
            ]
            self._set_headers(200)
            self.wfile.write(json.dumps({"cases": queue_cases}, indent=2).encode("utf-8"))

        elif path.startswith("/case/"):
            parts = path.split("/")
            case_id = parts[2]
            case = _store.get_case(case_id)
            if not case:
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": f"Case {case_id} not found"}).encode("utf-8"))
                return
            
            session = _store.get_session(case_id)
            proposal = _store.get_proposal(case_id)
            outreach = _store.get_outreach(case_id)

            response = {
                "case": case,
                "voiceSession": session,
                "proposal": proposal,
                "outreach": outreach
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(response, indent=2).encode("utf-8"))

        elif path == "/portfolio":
            res = invoke_agent({"skill": "portfolio-intelligence", "caseId": "PORTFOLIO", "payload": {}})
            self._set_headers(200)
            self.wfile.write(json.dumps(res.get("output", {}), indent=2).encode("utf-8"))

        elif path == "/audit":
            case_id = query.get("caseId", [None])[0]
            entries = _store.get_audit_log(case_id)
            self._set_headers(200)
            self.wfile.write(json.dumps({"auditEntries": entries}, indent=2).encode("utf-8"))

        elif path == "/skills":
            skills = [s.to_dict() for s in _skills_loader.get_all_skills(include_archetypes=True)]
            self._set_headers(200)
            self.wfile.write(json.dumps({"skills": skills}, indent=2).encode("utf-8"))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def _serve_static_file(self, filename):
        file_path = os.path.join(PUBLIC_DIR, filename)
        if os.path.exists(file_path):
            self._set_headers(200, "text/html; charset=utf-8")
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self._set_headers(404)
            self.wfile.write(f"File {filename} not found".encode("utf-8"))

def run_server(port=None):
    if port is None:
        if len(sys.argv) > 1 and sys.argv[1].isdigit():
            port = int(sys.argv[1])
        else:
            port = int(os.environ.get("PORT", "8000"))

    server_address = ("0.0.0.0", port)
    httpd = ThreadingHTTPServer(server_address, OrchestratorHTTPHandler)
    print(f"Orchestrator server running on 0.0.0.0:{port}...", flush=True)
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
