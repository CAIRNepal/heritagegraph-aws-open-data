#!/usr/bin/env python3
"""
Test public access on an S3 bucket WITHOUT any AWS credentials
(i.e. exactly what an anonymous visitor would see).

Usage:
    pip install requests
    python test_s3_public.py path/to/file.ttl
    python test_s3_public.py path/to/file.ttl --origin https://heritagegraph.cair-nepal.org
"""
import argparse
import sys
import uuid
import xml.etree.ElementTree as ET

import requests

BUCKET = "cair-nepal-heritage-graph"


def detect_region(bucket: str) -> str:
    r = requests.head(f"https://{bucket}.s3.amazonaws.com", timeout=10)
    return r.headers.get("x-amz-bucket-region", "us-east-1")


def check(name: str, ok: bool, detail: str) -> bool:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    return ok


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("key", nargs="?", default=None,
                   help="Object key in the bucket, e.g. data/graph.ttl "
                        "(optional: auto-picked from the listing if omitted)")
    p.add_argument("--bucket", default=BUCKET)
    p.add_argument("--origin", default="https://example.com",
                   help="Origin to use for the CORS checks")
    args = p.parse_args()

    region = detect_region(args.bucket)
    base = f"https://{args.bucket}.s3.{region}.amazonaws.com"

    if not args.key:
        r = requests.get(f"{base}/?list-type=2&max-keys=50", timeout=15)
        if r.status_code != 200:
            sys.exit(f"No key given and listing failed (HTTP {r.status_code}). "
                     f"Pass a key: python {sys.argv[0]} path/to/file")
        ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
        keys = [k.text for k in ET.fromstring(r.content).findall(".//s3:Contents/s3:Key", ns)
                if not k.text.endswith("/")]
        if not keys:
            sys.exit("Bucket listing works but the bucket has no objects to test.")
        args.key = keys[0]
        print(f"No key given, using first object from listing: {args.key}")

    url = f"{base}/{args.key.lstrip('/')}"
    print(f"Bucket region: {region}\nObject URL:    {url}\n")

    results = []

    # 1. Anonymous read of the object -> should be 200
    r = requests.get(url, timeout=15)
    results.append(check(
        "Public GET object", r.status_code == 200,
        f"HTTP {r.status_code}, {len(r.content)} bytes, "
        f"Content-Type={r.headers.get('Content-Type')}"))

    # 2. Anonymous bucket listing -> should be allowed (200) with the list policy
    r = requests.get(f"{base}/?list-type=2", timeout=15)
    results.append(check(
        "Public bucket listing", r.status_code == 200,
        f"HTTP {r.status_code}"))

    # 3. Anonymous upload -> should be denied (403)
    test_key = f"public-access-test-{uuid.uuid4().hex}.txt"
    r = requests.put(f"{base}/{test_key}", data=b"test", timeout=15)
    results.append(check(
        "Anonymous upload blocked", r.status_code == 403,
        f"HTTP {r.status_code}" + (" (ANYONE CAN WRITE!)" if r.status_code == 200 else "")))

    # 4. CORS on a simple GET
    r = requests.get(url, headers={"Origin": args.origin}, timeout=15)
    acao = r.headers.get("Access-Control-Allow-Origin")
    results.append(check(
        "CORS GET header", acao in ("*", args.origin),
        f"Access-Control-Allow-Origin={acao!r} for Origin {args.origin}"))

    # 5. CORS preflight (what browsers send before fetch() with custom headers)
    r = requests.options(url, headers={
        "Origin": args.origin,
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "content-type",
    }, timeout=15)
    results.append(check(
        "CORS preflight", r.status_code == 200,
        f"HTTP {r.status_code}, Allow-Methods="
        f"{r.headers.get('Access-Control-Allow-Methods')!r}"))

    passed = sum(results)
    print(f"\n{passed}/{len(results)} checks passed")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
