import json
from runner import run_tests

if __name__ == '__main__':
    results = run_tests()
    failures = [r for r in results if not r['success']]
    if not failures:
        print('All tests passed.')
    else:
        print(f"{len(failures)} test(s) failed:")
        for f in failures:
            print('-' * 40)
            print(f"Name: {f['name']}")
            print(f"URL: {f['url']}")
            print(f"Method: {f['method']}")
            print('Details:')
            print(json.dumps(f['details'], indent=2))
