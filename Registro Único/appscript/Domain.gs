/** Pure validation helpers shared by the app and offline contract tests. */
function normalizeEmail_(value) {
  return String(value || '').trim().toLowerCase();
}

function validateEmail_(value) {
  var email = normalizeEmail_(value);
  if (email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new Error('Ingresá un correo válido.');
  }
  return email;
}

function validateRole_(value) {
  var role = String(value || '').trim();
  if (['admin', 'user1', 'user2'].indexOf(role) < 0) {
    throw new Error('El rol no es válido.');
  }
  return role;
}

function validateRecord_(input) {
  if (!input || typeof input !== 'object') throw new Error('Datos de registro inválidos.');
  var record = {
    nombre: String(input.nombre || '').trim(),
    apellido: String(input.apellido || '').trim(),
    dni: String(input.dni || '').trim(),
    escolaridad: String(input.escolaridad || '').trim()
  };
  var labels = { nombre: 'Nombre', apellido: 'Apellido', dni: 'DNI', escolaridad: 'Escolaridad' };
  Object.keys(record).forEach(function (key) {
    if (!record[key]) throw new Error('Completá el campo ' + labels[key] + '.');
    if (record[key].length > (key === 'escolaridad' ? 160 : 80)) {
      throw new Error('El campo ' + labels[key] + ' supera el largo permitido.');
    }
  });
  return record;
}
