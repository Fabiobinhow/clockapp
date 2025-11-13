
import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv



# Carrega variáveis do arquivo .env
load_dotenv()

# Cria o app Flask
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET") or "chave_padrao_local_teste"

# Configurações do banco de dados
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", ""),
    "database": os.getenv("DB_NAME", "clockdb")
}

ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
ADMIN_PASS = os.getenv('ADMIN_PASS', 'admin123')


def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        emp_number = request.form.get('emp_number', '').strip()
        if not re.fullmatch(r"\d{7}", emp_number):
            flash('Número inválido. Deve conter exatamente 7 dígitos.', 'danger')
            return redirect(url_for('index'))
        try:
            conn = get_conn()
            cur = conn.cursor(dictionary=True)
            cur.execute('SELECT id, full_name FROM employees WHERE emp_number = %s', (emp_number,))
            emp = cur.fetchone()
            if not emp:
                flash('Funcionário não encontrado. Contate o administrador.', 'warning')
                return redirect(url_for('index'))
            cur.execute('SELECT event_type FROM logs WHERE employee_id = %s ORDER BY ts DESC LIMIT 1', (emp['id'],))
            last = cur.fetchone()
            next_event = 'in' if (not last or last['event_type'] == 'out') else 'out'
            cur.execute('INSERT INTO logs (employee_id, event_type) VALUES (%s, %s)', (emp['id'], next_event))
            conn.commit()
            flash(f"{emp['full_name']} - {'Entrada' if next_event=='in' else 'Saída'} registrada com sucesso.", 'success')
        except Error as e:
            flash('Erro no banco de dados: ' + str(e), 'danger')
        finally:
            try:
                cur.close(); conn.close()
            except:
                pass
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/admin', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        if user == ADMIN_USER and pwd == ADMIN_PASS:
            return redirect(url_for('register', auth='1'))
        else:
            flash('Credenciais inválidas.', 'danger')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    auth = request.args.get('auth')
    if auth != '1':
        flash('Acesso administrativo necessário.', 'warning')
        return redirect(url_for('admin_login'))
    try:
        conn = get_conn(); cur = conn.cursor(dictionary=True)
        if request.method == 'POST':
            full_name = request.form.get('full_name','').strip()
            emp_number = request.form.get('emp_number','').strip()
            if not full_name or not re.fullmatch(r"\d{7}", emp_number):
                flash('Nome vazio ou número inválido (7 dígitos).', 'danger')
            else:
                try:
                    cur.execute('INSERT INTO employees (full_name, emp_number) VALUES (%s,%s)', (full_name, emp_number))
                    conn.commit()
                    flash('Funcionário cadastrado.', 'success')
                except Error as e:
                    flash('Erro ao cadastrar (número pode já existir): ' + str(e), 'danger')
            return redirect(url_for('register', auth='1'))
        cur.execute('SELECT id, full_name, emp_number, created_at FROM employees ORDER BY full_name')
        employees = cur.fetchall()
    except Error as e:
        flash('Erro no banco de dados: ' + str(e), 'danger')
        employees = []
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass
    return render_template('register.html', employees=employees)

@app.route('/delete_employee/<int:emp_id>')
def delete_employee(emp_id):
    auth = request.args.get('auth')
    if auth != '1':
        flash('Acesso administrativo necessário.', 'warning')
        return redirect(url_for('admin_login'))
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute('DELETE FROM employees WHERE id = %s', (emp_id,))
        conn.commit()
        flash('Funcionário deletado (logs relacionados serão removidos via FK).', 'success')
    except Error as e:
        flash('Erro ao deletar: ' + str(e), 'danger')
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass
    return redirect(url_for('register', auth='1'))

@app.route('/logs')
def logs_view():
    auth = request.args.get('auth')
    if auth != '1':
        flash('Acesso administrativo necessário.', 'warning')
        return redirect(url_for('admin_login'))
    try:
        conn = get_conn(); cur = conn.cursor(dictionary=True)
        cur.execute('''
            SELECT l.id, e.full_name, e.emp_number, l.event_type, l.ts
            FROM logs l
            JOIN employees e ON e.id = l.employee_id
            ORDER BY l.ts DESC
        ''')
        logs = cur.fetchall()
    except Error as e:
        flash('Erro no banco: ' + str(e), 'danger')
        logs = []
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass
    return render_template('logs.html', logs=logs)

@app.route('/clear_logs')
def clear_logs():
    auth = request.args.get('auth')
    if auth != '1':
        flash('Acesso administrativo necessário.', 'warning')
        return redirect(url_for('admin_login'))
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute('TRUNCATE TABLE logs')
        conn.commit()
        flash('Tabela de logs limpa.', 'success')
    except Error as e:
        flash('Erro ao limpar logs: ' + str(e), 'danger')
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass
    return redirect(url_for('logs_view', auth='1'))

if __name__ == '__main__':
    from os import getenv
    port = int(getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
