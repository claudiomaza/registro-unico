# Registro Único

CRUD web para mantener registros de personas en una planilla central de Google Sheets. Las columnas de negocio son **Nombre, Apellido, DNI y Escolaridad**; cada registro se agrega al final y se identifica con un ID interno estable. La interfaz autenticada y el backend viven en Google Apps Script/HtmlService. GitHub Pages es solo una página de entrada estática.

## Arquitectura y acceso

- `appscript/`: exactamente `appsscript.json`, `Code.gs`, `Index.html` y `Admin.html`. Toda la lógica y validación están en el único `.gs`; cada HTML lleva sus propios estilos. No hay includes ni archivos auxiliares requeridos.
- `frontend/`: página estática sin login, secretos ni acceso a Sheets; solo enlaza al deployment estable de Apps Script.
- Apps Script está configurado para ejecutarse como quien accede (`USER_DEPLOYING`) y requiere una cuenta Google (`ANYONE`, no acceso anónimo). Cada persona autoriza scopes de Sheets e identidad de email en su propia sesión. Como esta app standalone abre una planilla por ID, el scope declarado `spreadsheets` es amplio: Google lo asocia al acceso a hojas de cálculo del usuario, no únicamente a la hoja central. Revisar este consentimiento antes de publicar.
- La lista interna de correos y roles vive en Script Properties. El primer administrador se elige mediante una Script Property privada y se inicializa al primer acceso. Roles: `admin`, `user1`, `user2`. Los dos últimos tienen los mismos permisos CRUD; solo `admin` gestiona usuarios y permisos de la planilla.
- El panel da o quita permiso individual de Editor en Sheets usando `Spreadsheet.addEditor/removeEditor`, bajo la identidad del administrador autenticado. La cuenta admin debe poder compartir la planilla. Permisos heredados de grupos/dominio pueden permanecer luego de quitar un permiso individual.

**Límite importante:** usuarios autorizados como editores pueden modificar datos directamente en Google Sheets. El backend valida las operaciones hechas desde la app, pero no puede imponer esas validaciones en los cambios directos. No cargar datos reales hasta decidir quién puede acceder a la hoja y comprobar su configuración de uso compartido.

## Configuración inicial

1. Claudio crea una planilla sintética o autorizada y conserva su ID.
2. En Apps Script, crea un proyecto independiente y copia exactamente estos cuatro archivos de `appscript/`: `appsscript.json`, `Code.gs`, `Index.html` y `Admin.html`. No hay que crear archivos `Domain.gs` o `Styles.html`: los validadores ya están dentro de `Code.gs` y el CSS en cada HTML. Esto evita el error `No se encontró el archivo HTML llamado Styles`. No autorices ni publiques desde este repositorio/agente.
3. Antes del deployment, en Apps Script > Configuración del proyecto > Propiedades del script, establecer `REGISTRO_UNICO_INITIAL_ADMIN_EMAIL` con el correo autorizado del administrador inicial. Esa configuración no se versiona. Luego iniciar sesión con esa cuenta, autorizar los scopes de Sheets e identidad y abrir `?page=admin`.
4. En el panel, vincular el ID de la planilla. Se crea `Registros` y la fila de encabezados únicamente si la pestaña no existe o está vacía; si hay datos con encabezados distintos, se detiene sin sobrescribir. También se crea la pestaña `Acceso` con enlaces en forma de botón para abrir el CRUD y Administración. Si ya existe una pestaña `Acceso` con contenido propio, renombrala antes. Si la planilla ya estaba vinculada, usá **Agregar accesos en la hoja** desde el panel Admin.
5. Publicar manualmente como Web app: ejecución como usuario que accede y acceso para usuarios con cuenta Google (no anónimo). Verificar estos ajustes en el diálogo del deployment; el manifest no demuestra que un deployment activo haya quedado configurado.
6. La landing ya apunta al deployment `/exec` informado por Claudio. Si cambia, actualizar el `href` del botón en `frontend/index.html`.
7. Para habilitar usuarios, desde Admin agregá correo/rol. El botón les concede Editor de Sheets. Para revocar se desactiva primero en la app y luego se quita el permiso individual de Sheets. El panel avisa que el acceso heredado por grupo/dominio debe revisarse aparte.

## Desarrollo y pruebas

Las pruebas offline de contrato usan la biblioteca estándar de Python:

```sh
python3 -m unittest discover -s tests -v
```

No se conectan a Google, no usan credenciales ni escriben en una planilla. Para verificar Apps Script, autenticación, permisos reales y la UI hay que usar una planilla sintética aislada y un deployment de prueba creado manualmente por Claudio; no se considera PASS hasta probar con navegador y cuentas autorizadas.

## Pages

El workflow del repo `.github/workflows/pages.yml` publica exclusivamente `Registro Único/frontend/`, nunca `appscript/`. El usuario autorizó hacer público el repositorio. La landing enlaza al deployment de Apps Script proporcionado por Claudio; no contiene login propio ni datos personales. En GitHub Free, Pages está disponible desde repos públicos. Workflow y sitio se publican por separado del backend.

## Versiones, permisos y rollback

- Pages y Apps Script se despliegan por separado. El repo no demuestra qué backend está activo.
- Antes de llevar `appscript/` al editor, comparar SHA/archivos con la versión que Claudio decida actualizar. La publicación es manual y no se hace con `clasp`.
- Para revertir Pages, volver a publicar el frontend del commit anterior. Para Apps Script, restaurar manualmente el código anterior y publicar una nueva versión desde Apps Script; no borrar el deployment existente.
- DNI es dato personal: limitar usuarios a necesidad real, proteger cuentas Google, evitar copias públicas/exportaciones y establecer retención fuera del alcance de esta primera versión.
