import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code = (ROOT / 'appscript' / 'Code.gs').read_text()
        cls.admin = (ROOT / 'appscript' / 'Admin.html').read_text()
        cls.manifest = json.loads((ROOT / 'appscript' / 'appsscript.json').read_text())

    def test_htmlservice_package_is_self_contained(self):
        appscript = ROOT / 'appscript'
        self.assertFalse((appscript / 'Domain.gs').exists())
        self.assertFalse((appscript / 'Styles.html').exists())
        self.assertTrue((appscript / 'Code.gs').is_file())
        self.assertEqual(sorted(p.name for p in appscript.iterdir()), ['Admin.html', 'Code.gs', 'Index.html', 'appsscript.json'])
        self.assertEqual(sorted(p.name for p in appscript.glob('*.gs')), ['Code.gs'])
        for name in ('Index.html', 'Admin.html'):
            html = (appscript / name).read_text()
            self.assertIn('<style>', html)
            self.assertNotIn("include('Styles')", html)
        for helper in ('normalizeEmail_', 'validateEmail_', 'validateRole_', 'validateRecord_'):
            self.assertIn('function ' + helper, self.code)
        for name in ('Index.html', 'Admin.html'):
            self.assertNotIn('include(', (appscript / name).read_text())

    def test_web_app_runs_as_accessing_user_and_requires_google_account(self):
        self.assertEqual(self.manifest['webapp']['executeAs'], 'USER_DEPLOYING')
        self.assertEqual(self.manifest['webapp']['access'], 'ANYONE')

    def test_initial_admin_is_exact_and_roles_are_allowlisted(self):
        self.assertIn("initialAdminKey: 'REGISTRO_UNICO_INITIAL_ADMIN_EMAIL'", self.code)
        self.assertRegex(self.code, r"\['admin',\s*'user1',\s*'user2'\]")

    def test_every_data_operation_checks_active_app_user(self):
        for fn in ('apiListRecords', 'apiSaveRecord', 'apiDeleteRecord'):
            body = re.search(r'function\s+' + fn + r'\([^)]*\)\s*\{([\s\S]*?)\n\}', self.code)
            self.assertIsNotNone(body, fn)
            self.assertIn('requireUser_()', body.group(1), fn)

    def test_admin_endpoints_check_admin_and_use_sheet_permissions(self):
        for fn in ('apiAdminListUsers', 'apiAdminConfigureSpreadsheet', 'apiAdminSaveUser', 'apiAdminInstallAccessLinks'):
            body = re.search(r'function\s+' + fn + r'\([^)]*\)\s*\{([\s\S]*?)\n\}', self.code)
            self.assertIsNotNone(body, fn)
            self.assertIn('requireAdmin_()', body.group(1), fn)
        self.assertIn('ss.addEditor(email)', self.code)
        self.assertIn('ss.removeEditor(email)', self.code)

    def test_bootstrap_admin_cannot_be_demoted(self):
        self.assertIn("email === initialAdmin && (!active || role !== 'admin')", self.code)
        self.assertIn("typeof input.active !== 'boolean'", self.code)

    def test_acl_is_not_kept_in_user_editable_sheet(self):
        self.assertIn('PropertiesService.getScriptProperties()', self.code)
        self.assertNotIn("getSheetByName('Usuarios')", self.code)

    def test_pages_links_to_configured_apps_script_without_collecting_credentials(self):
        page = (ROOT / 'frontend' / 'index.html').read_text().lower()
        self.assertIn('https://script.google.com/macros/s/akfycbxzpfntrgqwvhe69szf600kxxwqyktfp1k3c9-jt7phw70yp9_oexunlsgvcd6f7rr3jq/exec', page)
        self.assertIn('abrir aplicación', page)
        self.assertNotIn('disabled aria-disabled="true"', page)
        self.assertNotIn('REEMPLAZAR_CON_ID', page)
        self.assertNotIn('google.accounts', page)
        self.assertNotIn('type="password"', page)

    def test_required_docs_and_root_pages_workflow_exist(self):
        for name in ('README.md', 'AGENT.md', 'SPEC.md'):
            self.assertTrue((ROOT / name).is_file(), name)
        self.assertTrue((ROOT.parent / '.github' / 'workflows' / 'pages.yml').is_file())

    def test_admin_setup_adds_sheet_access_links_for_crud_and_admin(self):
        self.assertIn("var webAppUrl = ScriptApp.getService().getUrl();", self.code)
        self.assertIn("ensureAccessSheet_(ss, webAppUrl);", self.code)
        helper = re.search(r'function\s+ensureAccessSheet_\([^)]*\)\s*\{([\s\S]*?)\n\}', self.code)
        self.assertIsNotNone(helper)
        self.assertIn("getSheetByName('Acceso')", helper.group(1))
        self.assertIn("setLinkUrl(webAppUrl)", helper.group(1))
        self.assertIn("setLinkUrl(webAppUrl + '?page=admin')", helper.group(1))
        self.assertIn('apiAdminInstallAccessLinks', self.admin)
        self.assertIn('Agregar accesos en la hoja', self.admin)

    def test_record_columns_and_reversible_changes_are_accounted_for(self):
        self.assertIn("'ID', 'Nombre', 'Apellido', 'DNI', 'Escolaridad'", self.code)
        self.assertIn('sheet.getRange(newRow, 1, 1, APP_.headers.length).setValues(', self.code)
        self.assertIn("setNumberFormat('@')", self.code)
        self.assertIn('cellText_(record.dni)', self.code)
        self.assertIn('sheet.deleteRow(', self.code)
        self.assertIn('sheet.getRange(targetRow', self.code)

if __name__ == '__main__':
    unittest.main(verbosity=2)
