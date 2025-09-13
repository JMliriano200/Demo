import json
from flask import Flask, render_template, request
import markdown2

app = Flask(__name__)

SCALE = {"E": 10, "B": 7, "S": 4, "I": 1}

with open('data/students.json') as f:
    STUDENTS = json.load(f)

@app.route('/')
def index():
    return render_template('form.html', students=STUDENTS, scale=SCALE)

@app.route('/report', methods=['POST'])
def report():
    student = request.form['student']
    participation = request.form['participation']
    attitude = request.form['attitude']
    activity = request.form['activity']

    score_participation = SCALE[participation]
    score_attitude = SCALE[attitude]
    score_activity = SCALE[activity]
    average = (score_participation + score_attitude + score_activity) / 3
    condition = 'Aprobado' if average >= 7.6 else 'Recuperación'

    md = render_template(
        'student_report_template.md',
        nombre=student,
        periodo='2024',
        dia='1',
        participacion=participation,
        actitud=attitude,
        puntaje=f'{score_participation + score_attitude:.2f}',
        total_participacion=f'{score_participation:.2f}',
        total_actitud=f'{score_attitude:.2f}',
        unidad='Demostración',
        competencia='Demostración',
        indicador='Demostración',
        nivel=activity,
        puntaje_actividad=f'{score_activity:.2f}',
        promedio_competencia=f'{score_activity:.2f}',
        promedio_final=f'{average:.2f}',
        condicion=condition,
        observaciones=''
    )
    html = markdown2.markdown(md)
    return render_template('report.html', report=html)


if __name__ == '__main__':
    app.run(debug=True)
