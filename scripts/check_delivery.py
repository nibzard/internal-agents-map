# ABOUTME: Checks deployed status codes, bytes, MIME types, redirects, and headers of the site.
# ABOUTME: Every expectation comes from the route manifest and the files in the build root.
"""Verify deployed HTTP behavior and bytes; use --preview for Vercel protection bypass."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_ORIGIN = "https://internal-agents.com"
ALIAS_HOSTS = ("www.internal-agents.com", "internal-agents-map.vercel.app")
ERROR_PAGE = "404.html"
# Files that every deployment serves from the root of the build.
DISCOVERY_FILES = ("robots.txt", "llms.txt", "sitemap.xml", "agents.json", "data-guide.md")
# Vercel appends its feedback toolbar to protected preview HTML only.
PREVIEW_TOOLBAR = re.compile(
    rb'<script async data-explicit-opt-in="true" data-deployment-id="[^"]+"'
    rb' src="https://vercel\.live/_next-live/feedback/feedback\.js"></script>\s*$'
)
# A direct Markdown URL is plain text, because some assistant browsers refuse text/markdown.
# A page request whose Accept header asks for Markdown gets text/markdown.
MIME_TYPES = {
    ".html": "text/html",
    ".md": "text/plain",
    ".json": "application/json",
    ".xml": "application/xml",
    ".txt": "text/plain",
    ".svg": "image/svg+xml",
    ".png": "image/png",
}


@dataclass(frozen=True)
class Response:
    """One parsed HTTP response: its status, its lower-case headers, and its body."""

    status: int
    headers: dict[str, str]
    body: bytes


@dataclass(frozen=True)
class Case:
    """One request and everything the deployment must answer with."""

    path: str
    accept: str = "*/*"
    method: str = "GET"
    status: int = 200
    artifact: str | None = None
    mime: str | None = None
    location: str | None = None
    negotiated: bool = False
    canonical_link: bool = False
    alternate_link: bool = False
    noindex: bool | None = None
    immutable: bool = False
    host: str | None = None

    def describe(self) -> str:
        where = f" @{self.host}" if self.host else ""
        return f"{self.status} {self.method} {self.path} [{self.accept}]{where}"


def load_routes(path: Path) -> dict[str, dict[str, str]]:
    """Read the route manifest and give the clean path to artifact map it holds."""
    manifest = json.loads(path.read_text(encoding="utf-8"))
    version = manifest.get("schema_version")
    if version != 1:
        raise ValueError(f"Unsupported route manifest schema version: {version}")
    routes = manifest.get("routes")
    if not isinstance(routes, dict) or not routes:
        raise ValueError("The route manifest holds no routes.")
    for route, artifacts in routes.items():
        if not route.startswith("/"):
            raise ValueError(f"Route path must start at the root: {route}")
        if not isinstance(artifacts, dict) or set(artifacts) != {"html", "markdown"}:
            raise ValueError(f"Route {route} must name one HTML and one Markdown artifact.")
        for name in artifacts.values():
            if not isinstance(name, str) or not name.startswith("/"):
                raise ValueError(f"Route {route} names an artifact outside the root: {name}")
    return routes


def artifact_name(path: str) -> str:
    """Give the file name in the build root that a manifest artifact path refers to."""
    return path.lstrip("/")


def entry_routes(routes: dict[str, dict[str, str]]) -> list[str]:
    """The clean paths of the implementation pages, in a stable order."""
    return sorted(route for route in routes if route.startswith("/agents/"))


def legacy_paths(route: str) -> list[str]:
    """The paths that must answer one canonical route with a permanent redirect."""
    if route == "/":
        return ["/index.html"]
    return [route + ".html", route + "/"]


def mime_for(name: str) -> str:
    """The media type that the deployment must declare for a published file."""
    return MIME_TYPES.get(Path(name).suffix, "application/octet-stream")


def route_cases(routes: dict[str, dict[str, str]]) -> list[Case]:
    """Every route answers HTML by default and Markdown when a client asks for it."""
    cases: list[Case] = []
    for route, artifacts in sorted(routes.items()):
        cases.append(
            Case(
                path=route,
                accept="text/html",
                artifact=artifact_name(artifacts["html"]),
                mime="text/html",
                negotiated=True,
                alternate_link=True,
                noindex=False,
            )
        )
        cases.append(
            Case(
                path=route,
                accept="text/markdown",
                artifact=artifact_name(artifacts["markdown"]),
                mime="text/markdown",
                negotiated=True,
                canonical_link=True,
            )
        )
        cases.append(
            Case(
                path=artifacts["markdown"],
                artifact=artifact_name(artifacts["markdown"]),
                mime=mime_for(artifacts["markdown"]),
                canonical_link=True,
            )
        )
    return cases


def export_cases(routes: dict[str, dict[str, str]]) -> list[Case]:
    """The record JSON files stay out of search; the catalog exports stay indexable."""
    cases = [Case(path="/" + name, artifact=name, mime=mime_for(name)) for name in DISCOVERY_FILES]
    cases.append(
        Case(
            path="/agents/index.json",
            artifact="agents/index.json",
            mime="application/json",
            noindex=True,
        )
    )
    for route in entry_routes(routes):
        name = artifact_name(route) + ".json"
        cases.append(
            Case(path=route + ".json", artifact=name, mime="application/json", noindex=True)
        )
    return cases


def redirect_cases(routes: dict[str, dict[str, str]]) -> list[Case]:
    """A legacy path and a trailing slash reach the canonical path with a permanent redirect."""
    cases: list[Case] = []
    for route in sorted(routes):
        for path in legacy_paths(route):
            cases.append(Case(path=path, accept="text/html", status=308, location=route))
    return cases


def alias_cases(routes: dict[str, dict[str, str]]) -> list[Case]:
    """An alias host sends the visitor to the canonical origin and keeps the path."""
    sample = ["/", *entry_routes(routes)[:1]]
    return [
        Case(path=path, accept="text/html", status=308, location=CANONICAL_ORIGIN + path, host=host)
        for host in ALIAS_HOSTS
        for path in sample
    ]


def error_cases() -> list[Case]:
    """A path with no document is a real 404 that search engines must not index.

    The host redirects every `.html` request to its extensionless path before it
    looks for a document, so an unknown `.html` path answers 308 and then 404.
    """
    return [
        Case(path=path, accept="text/html", status=404, artifact=ERROR_PAGE, mime="text/html")
        for path in ("/agents/does-not-exist", "/missing-page", "/missing/nested/page")
    ] + [
        Case(
            path="/missing/nested/page.html",
            accept="text/html",
            status=308,
            location="/missing/nested/page",
        ),
        Case(path="/agents/does-not-exist.json", accept="*/*", status=404),
        Case(path="/agents/does-not-exist.md", accept="text/markdown", status=404),
    ]


def asset_cases(root: Path) -> list[Case]:
    """A bundled asset keeps its own type and cache policy and never becomes a page."""
    bundled = sorted(path.name for path in (root / "_astro").glob("*") if path.is_file())
    return [
        Case(path="/_astro/" + name, artifact="_astro/" + name, immutable=True) for name in bundled
    ]


def logo_cases(root: Path) -> list[Case]:
    """A published company logo answers with its image content type."""
    logos = sorted(path.name for path in (root / "logos").glob("*") if path.is_file())
    return [
        Case(path="/logos/" + name, artifact="logos/" + name, mime=mime_for(name)) for name in logos
    ]


def head_cases(routes: dict[str, dict[str, str]]) -> list[Case]:
    """HEAD answers the same status and headers as GET, with no body."""
    sample = ["/", *entry_routes(routes)[:2]]
    cases = [
        Case(path=path, accept="text/html", method="HEAD", mime="text/html", negotiated=True)
        for path in sample
    ]
    cases.append(Case(path="/agents.json", method="HEAD", mime="application/json"))
    return cases


def warm_cases(routes: dict[str, dict[str, str]]) -> list[Case]:
    """Ask for both representations of one path in turn to find a contaminated cache."""
    paths = ["/", *entry_routes(routes)[:3]]
    cases: list[Case] = []
    for _ in range(2):
        for path in paths:
            artifacts = routes[path]
            cases.append(
                Case(
                    path=path,
                    accept="text/html",
                    artifact=artifact_name(artifacts["html"]),
                    mime="text/html",
                    negotiated=True,
                )
            )
            cases.append(
                Case(
                    path=path,
                    accept="text/markdown",
                    artifact=artifact_name(artifacts["markdown"]),
                    mime="text/markdown",
                    negotiated=True,
                )
            )
    return cases


def build_cases(routes: dict[str, dict[str, str]], root: Path, preview: bool) -> list[Case]:
    """Collect every parallel case. Alias hosts only exist on the production domain."""
    cases = [
        *route_cases(routes),
        *export_cases(routes),
        *redirect_cases(routes),
        *error_cases(),
        *asset_cases(root),
        *logo_cases(root),
        *head_cases(routes),
    ]
    if not preview:
        cases.extend(alias_cases(routes))
    return cases


def parse_headers(dump: str) -> tuple[int, dict[str, str]]:
    """Read the last header block of a response, after any informational or hop block."""
    blocks = [block for block in dump.replace("\r\n", "\n").strip().split("\n\n") if block.strip()]
    if not blocks:
        raise ValueError("The response carries no headers.")
    lines = blocks[-1].splitlines()
    status = int(lines[0].split()[1])
    headers = {
        key.strip().lower(): value.strip()
        for key, value in (line.split(":", 1) for line in lines[1:] if ":" in line)
    }
    return status, headers


def expected_body(case: Case, root: Path) -> bytes | None:
    """The bytes of the build artifact that a response must repeat, when there is one."""
    return (root / case.artifact).read_bytes() if case.artifact else None


def origin_of(base: str) -> str:
    """The scheme and host of a deployment address, with no path. The scheme is https."""
    parts = urlsplit(base if "//" in base else "//" + base, scheme="https")
    return f"{parts.scheme}://{parts.netloc}"


def requested_url(case: Case, origin: str) -> str:
    """The address one case asks for: its own alias host, or the deployment that runs."""
    return (f"https://{case.host}" if case.host else origin.rstrip("/")) + case.path


def head_body(dump: bytes, payload: bytes) -> bytes:
    """The body of a HEAD response. curl writes the header block into the payload file."""
    return payload[len(dump) :] if payload.startswith(dump) else payload


def check_response(
    case: Case, response: Response, root: Path, origin: str = CANONICAL_ORIGIN
) -> list[str]:
    """Name every contract that one response breaks. `origin` is the deployment asked."""
    problems: list[str] = []
    if response.status != case.status:
        problems.append(f"HTTP {response.status}, wanted {case.status}")
        return problems
    content_type = response.headers.get("content-type", "")
    if case.mime and not content_type.startswith(case.mime):
        problems.append(f"Content-Type {content_type!r}, wanted {case.mime}")
    if case.location is not None:
        location = response.headers.get("location", "")
        # A relative target and the origin that was asked mean the same place.
        target = requested_url(case, origin)
        wanted = urljoin(target, case.location)
        if urljoin(target, location) != wanted:
            problems.append(f"Location {location!r}, wanted {wanted}")
    if case.artifact and case.method != "HEAD":
        wanted = expected_body(case, root)
        if response.body != wanted:
            problems.append(f"Body differs from {case.artifact}")
    if case.method == "HEAD" and response.body:
        problems.append("HEAD returned a body")
    if case.negotiated and "accept" not in response.headers.get("vary", "").lower():
        problems.append("Missing Vary: Accept")
    if case.alternate_link and 'rel="alternate"' not in response.headers.get("link", ""):
        problems.append("Missing alternate Link header")
    if case.canonical_link and 'rel="canonical"' not in response.headers.get("link", ""):
        problems.append("Missing canonical Link header")
    robots = response.headers.get("x-robots-tag", "").lower()
    if case.noindex is True and "noindex" not in robots:
        problems.append("Missing X-Robots-Tag: noindex")
    if case.noindex is False and "noindex" in robots:
        problems.append("Unwanted X-Robots-Tag: noindex")
    cache = response.headers.get("cache-control", "")
    if case.immutable:
        if "immutable" not in cache or "31536000" not in cache:
            problems.append(f"Cache-Control {cache!r} is not an immutable asset policy")
        if "text/markdown" in content_type:
            problems.append("A bundled asset must not be served as Markdown")
    elif case.status != 308 and "must-revalidate" not in cache:
        problems.append(f"Cache-Control {cache!r} does not revalidate")
    return problems


def request(case: Case, base: str, preview: bool, resolve_ip: str | None) -> Response:
    """Ask the deployment for one case and give back the parsed response."""
    with tempfile.TemporaryDirectory() as folder:
        headers, body = Path(folder) / "headers", Path(folder) / "body"
        curl = [
            "-sS",
            "--max-time",
            "30",
            "-H",
            "Accept: " + case.accept,
            "-D",
            str(headers),
            "-o",
            str(body),
        ]
        if case.method == "HEAD":
            curl.append("--head")
        if case.host:
            command = ["curl", f"https://{case.host}{case.path}", *curl]
        elif preview:
            command = [
                "vercel",
                "curl",
                case.path,
                "--deployment",
                base,
                "--scope",
                "nen-labs",
                "--",
                *curl,
            ]
        else:
            command = ["curl", base.rstrip("/") + case.path, *curl]
            if resolve_ip:
                command.extend(["--resolve", f"{urlsplit(base).hostname}:443:{resolve_ip}"])
        result = subprocess.run(command, capture_output=True, text=True, timeout=50)
        if result.returncode:
            raise AssertionError(f"Request failed: {case.describe()}: {result.stderr}")
        dump = headers.read_bytes()
        status, values = parse_headers(dump.decode(errors="replace"))
        received = body.read_bytes()
        if case.method == "HEAD":
            received = head_body(dump, received)
        if preview and case.artifact and case.artifact.endswith(".html"):
            received = PREVIEW_TOOLBAR.sub(b"", received)
        return Response(status, values, received)


def check(
    base: str,
    preview: bool,
    resolve_ip: str | None = None,
    root: str = "dist",
    routes_path: Path = ROOT / "routing-manifest.json",
) -> None:
    artifact = ROOT / root
    routes = load_routes(routes_path)
    cases = build_cases(routes, artifact, preview)
    origin = origin_of(base)

    def verify(case: Case) -> str:
        problems = check_response(case, request(case, base, preview, resolve_ip), artifact, origin)
        if problems:
            raise AssertionError(case.describe() + ": " + "; ".join(problems))
        return case.describe()

    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(verify, cases):
            print(result)
    # Alternate representations of the same paths in turn to catch cache contamination.
    warming = warm_cases(routes)
    for case in warming:
        print(verify(case))
    print(f"Passed {len(cases) + len(warming)} deployed response checks for {base}.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base")
    parser.add_argument("--preview", action="store_true")
    parser.add_argument(
        "--resolve-ip", help="Use a verified public DNS address while local DNS propagates."
    )
    parser.add_argument(
        "--root", default="dist", help="Directory that holds the built artifact to compare with."
    )
    args = parser.parse_args()
    check(args.base, args.preview, args.resolve_ip, args.root)


if __name__ == "__main__":
    main()
