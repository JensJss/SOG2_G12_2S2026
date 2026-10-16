"""Cliente mínimo XML-RPC / HTTP para Odoo 18 (solo librería estándar).

Se usa dentro del contenedor odoo:18.0 (perfil `seed`) o desde cualquier PC con
Python 3.10+:  ODOO_URL=http://localhost:18069 python seed/seed.py
"""
import http.cookiejar
import json
import os
import time
import urllib.request
import xmlrpc.client


class Odoo:
    def __init__(self, url, db, login, password):
        self.url = url.rstrip("/")
        self.db = db
        self.login = login
        self.password = password
        self.uid = None
        self._models = None
        self._fields_cache = {}

    # ------------------------------------------------------------------ XML-RPC
    @staticmethod
    def proxy(url, endpoint):
        return xmlrpc.client.ServerProxy(f"{url.rstrip('/')}/xmlrpc/2/{endpoint}", allow_none=True)

    def connect(self):
        common = self.proxy(self.url, "common")
        self.uid = common.authenticate(self.db, self.login, self.password, {})
        if not self.uid:
            raise RuntimeError(f"No se pudo autenticar {self.login} en la base {self.db}")
        self._models = self.proxy(self.url, "object")
        return self

    def call(self, model, method, *args, **kwargs):
        return self._models.execute_kw(self.db, self.uid, self.password, model, method, list(args), kwargs)

    # helpers
    def search(self, model, domain, **kw):
        return self.call(model, "search", domain, **kw)

    def search_read(self, model, domain, fields, **kw):
        return self.call(model, "search_read", domain, fields=fields, **kw)

    def count(self, model, domain):
        return self.call(model, "search_count", domain)

    def create(self, model, vals):
        return self.call(model, "create", self.clean(model, vals))

    def write(self, model, ids, vals):
        return self.call(model, "write", ids if isinstance(ids, list) else [ids], self.clean(model, vals))

    def ref(self, xmlid, raise_if_not_found=True):
        module, name = xmlid.split(".", 1)
        rows = self.search_read("ir.model.data", [("module", "=", module), ("name", "=", name)], ["res_id"], limit=1)
        if not rows:
            if raise_if_not_found:
                raise KeyError(xmlid)
            return False
        return rows[0]["res_id"]

    def fields(self, model):
        if model not in self._fields_cache:
            self._fields_cache[model] = set(self.call(model, "fields_get", attributes=["type"]).keys())
        return self._fields_cache[model]

    def clean(self, model, vals):
        """Descarta campos que no existan en el modelo (robustez entre versiones)."""
        flds = self.fields(model)
        return {k: v for k, v in vals.items() if k in flds}

    def get_or_create(self, model, domain, vals):
        ids = self.search(model, domain, limit=1)
        if ids:
            return ids[0], False
        return self.create(model, vals), True

    # ------------------------------------------------------------------ HTTP (PDF)
    def http_session(self):
        jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
        payload = json.dumps({"jsonrpc": "2.0", "method": "call",
                              "params": {"db": self.db, "login": self.login, "password": self.password}}).encode()
        req = urllib.request.Request(f"{self.url}/web/session/authenticate", data=payload,
                                     headers={"Content-Type": "application/json"})
        with opener.open(req, timeout=60) as r:
            res = json.loads(r.read())
        if res.get("error"):
            raise RuntimeError(f"Login HTTP falló: {res['error']}")
        return opener


def wait_for_odoo(url, timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with urllib.request.urlopen(f"{url.rstrip('/')}/web/health", timeout=5) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(5)
    raise RuntimeError(f"Odoo no respondió en {url} después de {timeout}s")


def env(name, default=None):
    v = os.environ.get(name, default)
    if v is None:
        raise SystemExit(f"Falta la variable de entorno {name}")
    return v
