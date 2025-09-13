' Genera un informe individual en Word a partir de datos de Excel.
' Requiere activar la referencia a Microsoft Word Object Library.

Sub GenerarInforme()
    Dim wsDatos As Worksheet
    Dim wsRegistro As Worksheet
    Dim wsActividades As Worksheet
    Dim estudianteId As String
    Dim fila As Range
    Dim nombre As String

    Set wsDatos = ThisWorkbook.Sheets("Datos generales")
    Set wsRegistro = ThisWorkbook.Sheets("Registro diario")
    Set wsActividades = ThisWorkbook.Sheets("Actividades")

    estudianteId = InputBox("N.º de orden del estudiante")

    For Each fila In wsDatos.Range("A2", wsDatos.Cells(wsDatos.Rows.Count, "A").End(xlUp))
        If fila.Value = estudianteId Then
            nombre = fila.Offset(0, 1).Value
            Exit For
        End If
    Next fila

    If nombre = "" Then
        MsgBox "Estudiante no encontrado", vbExclamation
        Exit Sub
    End If

    Dim wordApp As Word.Application
    Dim doc As Word.Document
    Set wordApp = New Word.Application
    wordApp.Visible = True

    Set doc = wordApp.Documents.Add
    doc.Content.InsertAfter "Informe de Desempeño del Estudiante" & vbCrLf
    doc.Content.InsertAfter "Estudiante: " & nombre & vbCrLf

    ' TODO: agregar datos del registro diario y actividades

    doc.SaveAs2 ThisWorkbook.Path & "\Informe - " & nombre & ".docx"
    doc.Close
    wordApp.Quit
End Sub
