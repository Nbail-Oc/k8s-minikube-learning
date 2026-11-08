import subprocess
import json
import time

def get_next_memory_limit(current_limit_str):
    if "64" in current_limit_str:
        return "128Mi"
    else:
        return "256Mi"

def main():
    while True:
        proc = subprocess.run(
            [".\\k8sgpt.exe", "analyze", "-o", "json"],
            capture_output=True,
            text=True
        )
        raw_output = proc.stdout
        json_start = raw_output.find("{")

        if json_start != -1:
            try:
                data = json.loads(raw_output[json_start:])
                for item in data.get("results", []):
                    for err in item.get("error", []):
                        if "OOMKilled" in err.get("Text", ""):
                            parent = item.get("parentObject", "")
                            dep = parent.split("/")[-1] if "/" in parent else "memory-demo"

                            limit_proc = subprocess.run(
                                [
                                    "kubectl", "get", "deployment", dep,
                                    "-o", "jsonpath={.spec.template.spec.containers[0].resources.limits.memory}"
                                ],
                                capture_output=True,
                                text=True
                            )
                            cur_limit = limit_proc.stdout.strip() or "64Mi"
                            new_limit = get_next_memory_limit(cur_limit)

                            print(f"k8sgpt detected OOMKilled on {dep} -> bumped memory limit {cur_limit} -> {new_limit}")

                            patch_json = json.dumps([
                                {"op": "replace", "path": "/spec/template/spec/containers/0/resources/limits/memory", "value": new_limit},
                                {"op": "replace", "path": "/spec/template/spec/containers/0/resources/requests/memory", "value": new_limit}
                            ])

                            subprocess.run(
                                ["kubectl", "patch", "deployment", dep, "--type=json", "-p", patch_json],
                                capture_output=True,
                                text=True
                            )

                            if new_limit == "256Mi":
                                return
            except Exception:
                pass

        time.sleep(10)

if __name__ == "__main__":
    main()
