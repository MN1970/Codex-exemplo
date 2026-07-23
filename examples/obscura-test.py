#!/usr/bin/env python3
"""
Exemplo: Usar Obscura para buscar e renderizar uma página.

Este script demonstra como integrar Obscura em um fluxo de Manta.
Pode ser adaptado para skills como `ler-edital`, `mk-manta`, etc.

Uso:
    python examples/obscura-test.py <URL>

    # Exemplo:
    python examples/obscura-test.py https://news.ycombinator.com
"""

import subprocess
import json
import sys
import argparse
from pathlib import Path


def fetch_with_obscura(url: str, dump_format: str = "text", eval_script: str = None) -> dict:
    """
    Fetch de uma URL usando Obscura MCP.

    Args:
        url: URL para fetchar
        dump_format: "text", "html", "json", "links"
        eval_script: Opcional — script JavaScript para eval no DOM

    Returns:
        dict com conteúdo e metadados
    """

    cmd = [
        "/root/.local/bin/obscura",
        "fetch",
        url,
        "--dump",
        dump_format,
        "--stealth",
        "--obey-robots"
    ]

    if eval_script:
        cmd.extend(["--eval", eval_script])

    print(f"[obscura] Fetching {url} (format={dump_format})...", file=sys.stderr)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return {
                "success": False,
                "url": url,
                "error": result.stderr or "Unknown error",
                "returncode": result.returncode
            }

        return {
            "success": True,
            "url": url,
            "format": dump_format,
            "content": result.stdout,
            "chars": len(result.stdout)
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "url": url,
            "error": "Timeout (30s)",
            "returncode": -1
        }
    except Exception as e:
        return {
            "success": False,
            "url": url,
            "error": str(e),
            "returncode": -1
        }


def extract_links(html: str) -> list:
    """Extrair links de um HTML."""
    import re
    pattern = r'href=["\']([^"\']+)["\']'
    return list(set(re.findall(pattern, html)))


def main():
    parser = argparse.ArgumentParser(
        description="Obscura test — fetch URL with render/scraping"
    )
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument(
        "--format",
        choices=["text", "html", "json", "links"],
        default="text",
        help="Output format"
    )
    parser.add_argument(
        "--eval",
        help="JavaScript code to eval in DOM"
    )
    parser.add_argument(
        "--extract-links",
        action="store_true",
        help="Extract and list links from HTML"
    )

    args = parser.parse_args()

    result = fetch_with_obscura(args.url, args.format, args.eval)

    if not result["success"]:
        print(f"❌ Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Fetched {result['chars']} chars from {result['url']}")
    print()

    # Mostrar conteúdo
    if args.format == "json":
        try:
            data = json.loads(result["content"])
            print(json.dumps(data, indent=2))
        except json.JSONDecodeError:
            print(result["content"])
    elif args.extract_links and result["format"] in ["html", "text"]:
        links = extract_links(result["content"])
        print(f"Found {len(links)} links:")
        for link in sorted(links)[:20]:  # Top 20
            print(f"  {link}")
    else:
        # Limitar output para terminal
        content = result["content"]
        if len(content) > 2000:
            print(content[:2000])
            print(f"\n... ({len(content) - 2000} more chars)")
        else:
            print(content)


if __name__ == "__main__":
    main()
