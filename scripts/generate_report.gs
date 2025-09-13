/**
 * Genera un informe individual en Google Docs para el estudiante seleccionado.
 * Rellena una plantilla de Google Docs con los datos de las hojas de cálculo.
 *
 * Requiere reemplazar TEMPLATE_ID y FOLDER_ID con los valores adecuados.
 */
function generarInforme(estudianteId) {
  const ss = SpreadsheetApp.getActive();
  const datosSheet = ss.getSheetByName('Datos generales');
  const registroSheet = ss.getSheetByName('Registro diario');
  const actividadesSheet = ss.getSheetByName('Actividades');

  // Buscar información del estudiante
  const datos = datosSheet.getDataRange().getValues();
  const encabezado = datos.shift();
  const idx = encabezado.indexOf('N.º de orden');
  const nombreIdx = encabezado.indexOf('Nombres y apellidos');
  const estudiante = datos.find(row => row[idx] === estudianteId);
  if (!estudiante) {
    throw new Error('Estudiante no encontrado: ' + estudianteId);
  }
  const nombre = estudiante[nombreIdx];

  // Crear documento a partir de plantilla
  const template = DriveApp.getFileById('TEMPLATE_ID');
  const carpeta = DriveApp.getFolderById('FOLDER_ID');
  const docFile = template.makeCopy('Informe - ' + nombre, carpeta);
  const doc = DocumentApp.openById(docFile.getId());
  let body = doc.getBody();

  // Reemplazar marcadores en la plantilla
  body.replaceText('{{nombre}}', nombre);

  // Ejemplo: insertar promedio final
  const promedioFinal = calcularPromedioFinal(registroSheet, actividadesSheet, estudianteId);
  body.replaceText('{{promedio_final}}', promedioFinal.toString());

  doc.saveAndClose();
  return docFile.getUrl();
}

/**
 * Calcula un promedio final simple basado en el registro diario y actividades.
 * Ajustar según la lógica requerida.
 */
function calcularPromedioFinal(registroSheet, actividadesSheet, estudianteId) {
  // Ejemplo básico: retornar 0 si no hay implementación.
  return 0;
}
