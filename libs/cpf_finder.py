import re
import sys
import json
import itertools
import asyncio
import aiohttp
import contextlib
from .user_agents import return_ua
from playwright.async_api import async_playwright, Page, Browser
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

PORTAL_BASE   = "https://portaldatransparencia.gov.br"
SEARCH_URL    = "https://busca.portaldatransparencia.gov.br/busca/pessoa-fisica"
STATIC_TOKEN  = "wtwLC1ItJOLhvc2n6rhY"

_API_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
    "Referer": f"{PORTAL_BASE}/pessoa-fisica/busca/lista",
    "Origin": PORTAL_BASE,
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": return_ua(),
}

_BLOCK_TYPES = {"image", "media", "font"}

_STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', {get: () => false, configurable: true});
Object.defineProperty(navigator, 'plugins', {get: () => [
    {name:'Chrome PDF Plugin', filename:'internal-pdf-viewer', description:'Portable Document Format'},
    {name:'Chrome PDF Viewer', filename:'mhjfbmdgcfjbbpaeojofohoefgiehjai', description:''},
    {name:'Native Client', filename:'internal-nacl-plugin', description:''}
]});
Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR','pt','en-US','en']});
Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
window.chrome = {runtime: {}, app: {isInstalled: false}};
"""


class CPFLiveConsult:

    def __init__(self, mask: str, workers: int, string=None):
        if re.match(r"^(\*\*\*\.\d{3}\.\d{3}-\*\*)|(\*\*\*\d{3}\d{3}\*\*)", mask.upper()):
            if workers <= 20 and workers >= 10:
                self.string = string
                formated_mask = mask.replace("*","X")
                self.mask = re.sub(r"[^0-9Xx]", "", formated_mask)
                self.workers = workers
                return

            raise ValueError("Invalid workers value.")

        raise ValueError("Invalid mask value.")

    @staticmethod
    def _calc_digit(partial: str, weight: int) -> int:
        soma = sum(int(d) * w for d, w in zip(partial, range(weight, 1, -1)))
        rest = (soma * 10) % 11
        return 0 if rest >= 10 else rest

    @staticmethod
    def _build_cpf(base9: str) -> str | None:
        if len(set(base9)) == 1:
            return None
        d1 = CPFLiveConsult._calc_digit(base9, 10)
        d2 = CPFLiveConsult._calc_digit(base9 + str(d1), 11)
        return base9 + str(d1) + str(d2)

    @staticmethod
    def fmt(cpf: str) -> str:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

    @staticmethod
    def generate_candidates(mask: str) -> list[str]:
        clean = re.sub(r"[^0-9Xx]", "", mask).upper()
        if len(clean) != 11:
            print(f"Invalid mask: '{mask}'. Use format ***.452.217-**")
            sys.exit(1)

        prefix = list(clean[:9])
        x_pos = [i for i, c in enumerate(prefix) if c == "X"]

        out = []
        for combo in itertools.product(range(10), repeat=len(x_pos)):
            base = prefix.copy()

            for pos, digit in zip(x_pos, combo):
                base[pos] = str(digit)

            cpf = CPFLiveConsult._build_cpf("".join(base))
            if cpf:
                out.append(cpf)

        return out

    @staticmethod
    def _parse_json(data: dict) -> tuple[bool, str]:
        total = data.get("totalRegistros", 0)
        records = data.get("registros", [])
        name = ""
        if records:
            raw = records[0].get("nome", "")
            name = raw.title() if raw else ""
        return (total > 0 or bool(records), name)

    async def _query_playwright(self, browser: Browser, cpf: str, sem: asyncio.Semaphore) -> tuple[bool, str]:
        async with sem:
            captured: dict = {}
            ready = asyncio.Event()

            context = await browser.new_context(
                user_agent=_API_HEADERS["User-Agent"],
                viewport={"width": 1280, "height": 800},
                locale="pt-BR",
                timezone_id="America/Sao_Paulo",
                extra_http_headers={"Accept-Language": "pt-BR,pt;q=0.9"},
            )

            await context.add_init_script(_STEALTH_JS)
            page: Page = await context.new_page()

            async def block_route(route):
                if route.request.resource_type in _BLOCK_TYPES:
                    await route.abort()
                else:
                    await route.continue_()

            await page.route("**/*", block_route)

            async def on_response(response):
                if "busca.portaldatransparencia.gov.br" in response.url and response.status == 200:
                    try:
                        data = await response.json()
                        captured["json"] = data
                        ready.set()
                    except Exception:
                        pass

            page.on("response", on_response)
            
            try:
                await page.goto(
                    f"{PORTAL_BASE}/pessoa-fisica/busca/lista?termo={cpf}&pagina=1&tamanhoPagina=10",
                    wait_until="commit",
                    timeout=15000
                )
            except asyncio.TimeoutError:
                await page.close()
                return (False, "")
            except PlaywrightTimeoutError:
                return (False, "")

            try:
                btn = await page.wait_for_selector(
                    'button[aria-label="Enviar dados do formulário de busca"]',
                    timeout=10_000,
                )
                await btn.click()
            except Exception:
                pass

            try:
                await asyncio.wait_for(ready.wait(), timeout=20.0)
            except asyncio.TimeoutError:
                pass

            await page.close()
            await context.close()

            if "json" in captured:
                return self._parse_json(captured["json"])

            return (False, "")

    async def run_playwright(self, candidates: list[str]) -> list[dict]:

        results = []
        lock = asyncio.Lock()
        sem = asyncio.Semaphore(self.workers)

        search_term = self.string.upper() if self.string else None

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            async def process(cpf):
                try:
                    formatted = self.fmt(cpf)

                    found, name = await self._query_playwright(browser, cpf, sem)

                    if not found or not name:
                        return

                    if search_term and search_term not in name.upper():
                        return

                    async with lock:
                        results.append({
                            "cpf": formatted,
                            "name": name
                        })
                        print(f"CPF: {formatted} NAME: {name}")

                except asyncio.CancelledError:
                    return
                except Exception as e:
                    print(f"[ERROR CPF {cpf}] {e}")

            tasks = [asyncio.create_task(process(cpf)) for cpf in candidates]

            try:
                await asyncio.gather(*tasks, return_exceptions=True)

            except KeyboardInterrupt:
                print("\n[!] CTRL+C detectado, cancelando tasks...")

                for t in tasks:
                    t.cancel()

                with contextlib.suppress(Exception):
                    await asyncio.gather(*tasks, return_exceptions=True)

            finally:
                with contextlib.suppress(Exception):
                    await browser.close()

        return results

    def get_results(self):
        try:
            candidates = self.generate_candidates(self.mask)
            asyncio.run(self.run_playwright(candidates))
        except KeyboardInterrupt:
            print("User Aborted.")
