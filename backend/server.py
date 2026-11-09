import threading

from flask import Flask, jsonify, request

from compiler import compile_source, RequestError

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024     # Sec 9.4: request size limit

MAX_CONCURRENT = 2                               # Sec 9.7: concurrency limit
_slots = threading.BoundedSemaphore(MAX_CONCURRENT)

def _error(status, code, message):
    return jsonify({"success": False, "error": code, "message": message}), status

@app.errorhandler(413)
def too_large(_):
    return _error(413, "invalid_request", "Request body is too large.")

@app.post("/api/compile")
def compile_endpoint():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error(400, "invalid_request", "Body must be a JSON object.")

    if not _slots.acquire(blocking=False):
        return _error(503, "busy", "Server is busy. Try again shortly.")
    try:
        result = compile_source(data.get("source"), data.get("optimization"))
    except RequestError as e:
        return _error(400, "invalid_request", str(e))
    except Exception:
        app.logger.exception("compile failed unexpectedly")   # details stay in server log
        return _error(500, "internal_error", "Internal server error.")
    finally:
        _slots.release()

    return jsonify(result), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)