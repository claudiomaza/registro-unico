# AGENT.md — Registro Único

## Fuente de verdad y límites

- Repositorio: `https://github.com/claudiomaza/registro-unico`.
- Carpeta canónica: `Registro Único/` (espacio y tilde incluidos).
- `main` es la rama integrada. Mantener una sola rama de desarrollo local, `dev`; no crear ramas feature adicionales ni publicar Apps Script desde el agente.
- `appscript/` es fuente manual del backend y ambas pantallas HtmlService. No crear, actualizar ni desplegar Apps Script como agente.
- `frontend/` es fuente de la página de entrada estática; workflow raíz `.github/workflows/pages.yml` publica solo esta carpeta. Despliegue Pages separado. Repo público por autorización expresa de Claudio (2026-11-26); no agregar datos reales, IDs de hojas ni credenciales. Landing permanece inactiva hasta configurar la URL real de Apps Script.
- No leer ni escribir datos reales, no ejecutar migraciones y no cambiar permisos de planillas reales en desarrollo. Usar fixtures/sheets sintéticas aisladas.

## Diseño vigente

- Producto: CRUD de registros en filas, atributos en columnas: Nombre, Apellido, DNI, Escolaridad. Las filas nuevas van al final; ID estable y timestamps/actor son metadatos adicionales del sistema.
- Una única Google Sheet central. Apps Script corre como la persona que accede (`USER_DEPLOYING`); Google la autentica al abrir HtmlService y pide consentimiento OAuth de Apps Script.
- `Session.getActiveUser().getEmail()` debe resolver una identidad; si está vacío, fail closed. Cada operación pública vuelve a comprobar usuario activo y rol en backend. No usar email enviado desde navegador como identidad.
- ACL de app en `PropertiesService.getScriptProperties()`, no en una hoja editable por usuarios. Primer admin lo configura Claudio fuera del repo mediante la Script Property `REGISTRO_UNICO_INITIAL_ADMIN_EMAIL=<correo del administrador bootstrap>`; nunca incluir ese correo en archivos públicos.
- Roles literales: `admin`, `user1`, `user2`. `user1` y `user2` comparten permisos CRUD; solo admin administra usuarios y ACL de Sheets. Confirmar diferencias funcionales antes de crear permisos diferenciados.
- Panel: `appscript/Admin.html`, accesible por `?page=admin`; HTML por sí solo no autoriza nada.
- Admin enlaza hoja desde el panel. Configuración guarda el spreadsheet ID en Script Properties y crea `Registros` + encabezados solo cuando la pestaña no existe/vacía. No sobrescribe encabezados o datos existentes; si difieren, aborta. Crea además `Acceso` con hipervínculos estilizados a CRUD y Admin, usando el URL del web app; si la pestaña `Acceso` existente no tiene el marcador del proyecto, aborta sin modificarla. Para una hoja previamente vinculada, Admin puede invocar `apiAdminInstallAccessLinks` desde el botón **Agregar accesos en la hoja**.
- Crear/actualizar/borrar pasa por `LockService.getScriptLock()`. Edición de Sheets por fuera de la app no adquiere ese lock.
- `Spreadsheet.addEditor/removeEditor` otorga/quita permiso individual bajo la identidad del admin, con scopes de Sheets. La baja desactiva la app y quita el permiso individual; avisar que accesos por grupo/dominio pueden subsistir aunque la operación individual haya sido exitosa. Si Google deniega la revocación, reportar permiso directo pendiente.
- La elección de ejecución implica que los editores pueden modificar directamente los datos en Sheets. La validación del CRUD no controla esos cambios.
- Pages es una landing estática que enlaza al `/exec` estable de Apps Script. Sin OAuth Client ID en Pages, sin recopilación de credenciales. No es un cliente API.

## Contrato y seguridad

Funciones cliente/servidor públicas: `apiBootstrap`, `apiListRecords`, `apiSaveRecord`, `apiDeleteRecord`, `apiAdminListUsers`, `apiAdminConfigureSpreadsheet`, `apiAdminSaveUser`. Todas deben autorizar en servidor. Helpers internos terminan en `_`.

- Nunca confiar en campos `email`, `role`, `isAdmin` del navegador.
- Validar longitudes/formato en servidor; guardar entradas como texto para conservar ceros y evitar fórmulas; construir DOM con `textContent`, no insertar datos del Sheet como HTML.
- Impedir que el último admin activo o el admin de bootstrap se desactive/demote; evitar que un admin se quite a sí mismo.
- En alta, dar permiso Sheets y persistir usuario; en baja, marcar inactivo antes de retirar ACL. Registrar/loguear solo metadatos seguros, nunca DNI.
- `appsscript.json` declara scopes mínimos necesarios para Sheets e identidad. El uso de openById y add/remove editor requiere scope `spreadsheets`, amplio para las hojas de cálculo accesibles por cada usuario, no limitado automáticamente al ID configurado. Explicar y revisar esto antes de consentimiento. No usar DriveApp ni pedir `drive` scope amplio.
- DNI son datos sensibles. Pruebas solo sintéticas. No habilitar acceso general, publicar un Sheet, cambiar permisos heredados o exportar datos.

## Pruebas y criterios

- Offline: `python3 -m unittest discover -s tests -v`; valida contrato estático y no equivale a ejecutar Apps Script.
- TDD: antes de cambiar comportamiento, agregar prueba que falla, confirmar RED, implementar, confirmar GREEN y ejecutar suite.
- Para integración real, Claudio debe crear planilla sintética y deployment de prueba manual; usar cuentas de prueba. QA navegador móvil/escritorio y roles: no admin, admin, desconocido, correo no disponible, sesión revocada; alta, revocación directa, permisos heredados, CRUD, duplicado DNI, concurrencia y red.
- Apps Script runtime, OAuth, edición real, ACL Google, integración Pages→HtmlService y QA visual: `BLOCKED/NO VERIFICADO` hasta evidencia del deployment. Nunca inferir PASS desde source tests.
- Integración: revisar diff y verificar SHA; los cambios aprobados se integran en `main` desde la única rama local `dev`. No publicar Apps Script. Pages deploy solo desde `Registro Único/frontend/` mediante el workflow de `main`.

## Configuración/rollback manual

- Deployment activo: verificar en Apps Script editor que ejecuta como quien accede y que el acceso requiere cuenta Google. El manifest no prueba estado activo.
- La URL `/exec` estable se configura manualmente en `frontend/index.html` tras recibirla de Claudio; hasta entonces el botón está deshabilitado. Cambiarla requiere validar el destino. Nunca actualizar deployment con agente.
- Spreadsheet ID vive en Script Properties. Reconfiguración/cambio de hoja se hace con procedimiento manual y respaldo/confirmación; no resetear ni migrar datos.
- Rollback de HtmlService: restaurar fuentes previas y publicar nueva versión manualmente. Rollback Pages: workflow de frontend del SHA anterior.
