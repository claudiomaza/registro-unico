# Registro Único — Implementación integrada

**Estado:** fuentes y pruebas integradas en `main`; Pages publica únicamente la landing estática. No equivale a deployment de Apps Script.

**Arquitectura:** la aplicación vive bajo `Registro Único/`: `appscript/` contiene exactamente `appsscript.json`, un `Code.gs`, `Index.html` y `Admin.html`. Los validadores se definen en `Code.gs`; estilos embebidos en cada vista HTML; no hay includes ni archivos auxiliares. `frontend/` contiene la landing Pages; README, AGENT y SPEC documentan el proyecto. Apps Script corre como el usuario Google que accede. Roles viven en Script Properties; endpoints revalidan ACL. Admin concede/revoca permiso individual de editor en Sheets. Pages solo enlaza al `/exec`.

**Pruebas:** `python3 -m unittest discover -s 'Registro Único/tests' -v`; análisis de sintaxis Apps Script/HTML y parseo del manifest. Estas verificaciones no prueban OAuth ni runtime Google real.

**Despliegue:** Apps Script lo publica manualmente Claudio; no usar clasp ni publicar desde el agente. El workflow de Pages se ejecuta desde `main` y publica solo `Registro Único/frontend/`. Mantener `main` integrado y una única rama local `dev`; evitar ramas feature adicionales.

**Pendiente:** validar Apps Script, OAuth, ACL, planilla aislada y navegador tras el deployment manual.
