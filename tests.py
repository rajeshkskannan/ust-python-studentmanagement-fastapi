import requests
import sys

BASE = "http://127.0.0.1:8000"

def assert_eq(a, b, msg=""):
    if a != b:
        print("ASSERT FAIL:", a, "!=", b, msg)
        sys.exit(1)

def run_tests():
    # ensure clean state by restarting server between runs in manual workflow
    print("Creating students...")
    s1 = requests.post(f"{BASE}/students", json={"name":"Alice","age":20,"course":"Python","score":92.5}).json()
    s2 = requests.post(f"{BASE}/students", json={"name":"Bob","age":22,"course":"Data Science","score":88.0}).json()

    print("List students...")
    all_st = requests.get(f"{BASE}/students").json()
    assert_eq(len(all_st), 2)

    print("Get student by id...")
    got = requests.get(f"{BASE}/students/{s1['id']}").json()
    assert_eq(got["name"], "Alice")

    print("Update student...")
    upd = requests.put(f"{BASE}/students/{s2['id']}", json={"name":"Bobby","age":23,"course":"Data Science","score":89.0}).json()
    assert_eq(upd["name"], "Bobby")
    assert_eq(upd["score"], 89.0)

    print("Topper...")
    topper = requests.get(f"{BASE}/students/topper").json()
    assert_eq(topper["name"], "Alice")

    print("Delete student...")
    r = requests.delete(f"{BASE}/students/{s1['id']}")
    assert_eq(r.status_code, 204)

    print("Confirm deletion...")
    r = requests.get(f"{BASE}/students/{s1['id']}")
    assert_eq(r.status_code, 404)

    print("All tests passed.")

if __name__ == "__main__":
    run_tests()
