from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, make_response
from weasyprint import HTML
import os
from datetime import datetime
from datetime import date
from database import Database
from PIL import Image
from datetime import timedelta

import MySQLdb
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io
import base64

app = Flask(__name__)
app.secret_key = 'clave_secreta_mantenimiento_2024'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Crear carpeta de uploads si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = Database()

#Funcion para comprimir imágenes

def comprimir_imagen(imagen_file, calidad=80, ancho_max=1600):
    """
    Comprime una imagen manteniendo una calidad aceptable
    """
    try:
        # Abrir la imagen
        img = Image.open(imagen_file)
        
        # Convertir a RGB si es necesario (para JPEG)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Redimensionar si es muy ancha
        if img.width > ancho_max:
            ratio = ancho_max / img.width
            nuevo_alto = int(img.height * ratio)
            img = img.resize((ancho_max, nuevo_alto), Image.Resampling.LANCZOS)
        
        # Guardar comprimida
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=calidad, optimize=True)
        output.seek(0)
        
        return output
        
    except Exception as e:
        print(f"Error al comprimir imagen: {e}")
        # Si hay error, devolver el archivo original
        imagen_file.seek(0)
        return imagen_file

# Función para procesar y guardar fotos
def guardar_foto(file, mantenimiento_id, tipo, index):
    if file and file.filename:
        # Verificar tipo de archivo
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            print(f"Tipo de archivo no permitido: {file_ext}")
            return None
        
        # Crear nombre único con índice
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{mantenimiento_id}_{tipo}_{timestamp}_{index}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            # Usar la función de compresión mejorada
            imagen_comprimida = comprimir_imagen(file, calidad=80, ancho_max=1600)
            
            # Guardar la imagen comprimida
            with open(filepath, 'wb') as f:
                f.write(imagen_comprimida.read())
            
            print(f"Foto guardada: {filename} - Tamaño: {os.path.getsize(filepath) / 1024 / 1024:.2f} MB")
            return filename
            
        except Exception as e:
            print(f"Error procesando imagen: {e}")
            # Fallback: intentar guardar sin compresión si hay error
            try:
                file.stream.seek(0)  # Resetear el stream
                file.save(filepath)
                print(f"Foto guardada (sin compresión): {filename}")
                return filename
            except Exception as e2:
                print(f"Error también al guardar sin compresión: {e2}")
                return None
    return None

# ==================== RUTAS DE AUTENTICACIÓN ====================
# Configuración de base de datos optimizada


# Manejo de errores de BD
@app.errorhandler(MySQLdb.Error)
def handle_db_error(error):
    flash('Error de base de datos. Por favor intenta nuevamente.', 'error')
    return redirect(url_for('dashboard'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el proceso de login"""
    # Si ya está autenticado, redirigir al dashboard
    if session.get('autenticado'):
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        rol = request.form['rol']
        
        # Verificar credenciales en la base de datos
        user = db.execute_query(
            "SELECT * FROM usuarios WHERE usuario = %s AND password = %s AND rol = %s", 
            (usuario, password, rol)
        )
        
        if user:
            # Login exitoso - crear sesión
            session['user_id'] = user[0]['id']
            session['usuario'] = user[0]['usuario']
            session['rol'] = user[0]['rol']
            session['nombre'] = user[0]['nombre']
            session['autenticado'] = True
            
            
            flash(f'Bienvenido {user[0]["nombre"]}', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario, contraseña o rol incorrectos', 'error')
            # Permanecer en la página de login para mostrar el error
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cierra la sesión del usuario"""
    session.clear()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('login'))

# Middleware para verificar autenticación
@app.before_request
def require_login():
    # Rutas que no requieren autenticación
    allowed_routes = ['login', 'static', 'logout']
    
    if request.endpoint not in allowed_routes and not session.get('autenticado'):
        return redirect(url_for('login'))

# ==================== RUTAS PRINCIPALES ====================

from datetime import date

@app.route('/')
def dashboard():
    """Dashboard principal"""
    # Obtener datos para el dashboard
    equipos = db.execute_query("SELECT * FROM equipos") or []
    mantenimientos_recientes = db.execute_query("""
        SELECT m.*, e.nombre as equipo_nombre 
        FROM mantenimientos m 
        JOIN equipos e ON m.equipo_id = e.id 
        ORDER BY m.fecha, m.hora DESC LIMIT 5
    """) or []
    
    # Obtener próximos 5 mantenimientos del cronograma (ordenados por proximo_mtto ascendente)
    proximos_mantenimientos = db.execute_query("""
        SELECT c.*, e.nombre as equipo_nombre 
        FROM cronograma c 
        JOIN equipos e ON c.equipo_id = e.id 
        WHERE c.proximo_mtto IS NOT NULL
        ORDER BY c.proximo_mtto ASC 
        LIMIT 5
    """) or []
    
    # Calcular estadísticas
    total_equipos = len(equipos)
    
    # Mantenimientos este mes
    mtto_mes = db.execute_query("""
        SELECT COUNT(*) as total 
        FROM mantenimientos 
        WHERE MONTH(fecha) = MONTH(CURRENT_DATE()) 
        AND YEAR(fecha) = YEAR(CURRENT_DATE())
    """) or [{'total': 0}]
    
    # Pendientes
    pendientes = db.execute_query("""
        SELECT COUNT(*) as total 
        FROM mantenimientos 
        WHERE estado = 'pendiente'
    """) or [{'total': 0}]
    
    # Próximos mantenimientos (en los próximos 7 días)
    proximos = db.execute_query("""
        SELECT COUNT(*) as total 
        FROM cronograma 
        WHERE proximo_mtto BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
    """) or [{'total': 0}]
    
    return render_template('dashboard.html', 
                         equipos=equipos, 
                         mantenimientos=mantenimientos_recientes,
                         proximos_mantenimientos=proximos_mantenimientos,
                         total_equipos=total_equipos,
                         mtto_mes=mtto_mes[0]['total'] if mtto_mes else 0,
                         pendientes=pendientes[0]['total'] if pendientes else 0,
                         proximos=proximos[0]['total'] if proximos else 0,
                         hoy=date.today())  # <-- Agregar esta línea

@app.route('/equipos')
def ver_equipos():
    """Lista de equipos"""
    equipos = db.execute_query("SELECT * FROM equipos") or []
    
    # Calcular estadísticas
    equipos_activos = len([e for e in equipos if e.get('estado') == 'activo'])
    equipos_mantenimiento = len([e for e in equipos if e.get('estado') == 'mantenimiento'])
    
    return render_template('equipos.html', 
                         equipos=equipos,
                         equipos_activos=equipos_activos,
                         equipos_mantenimiento=equipos_mantenimiento)

@app.route('/equipos/nuevo', methods=['GET', 'POST'])
def nuevo_equipo():
    """Agregar un nuevo equipo"""
    if request.method == 'POST':
        try:
            # Recoger datos del formulario
            nombre = request.form.get('nombre')
            fabricante = request.form.get('fabricante')
            contacto_fabricante = request.form.get('contacto_fabricante')
            ubicacion = request.form.get('ubicacion')
            fecha_compra = request.form.get('fecha_compra')
            potencia = request.form.get('potencia')
            voltaje = request.form.get('voltaje')
            tipo_alimentacion = request.form.get('tipo_alimentacion')
            potencia_motor = request.form.get('potencia_motor')
            relacion_motoreductor = request.form.get('relacion_motoreductor')
            diametro_polea = request.form.get('diametro_polea')
            
            # Query para insertar
            query = """
                INSERT INTO equipos (nombre, fabricante, contacto_fabricante, ubicacion, fecha_compra, 
                                    potencia, voltaje, tipo_alimentacion, potencia_motor, 
                                    relacion_motoreductor, diametro_polea)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (nombre, fabricante, contacto_fabricante, ubicacion, fecha_compra, 
                     potencia, voltaje, tipo_alimentacion, potencia_motor, 
                     relacion_motoreductor, diametro_polea)
            
            db.execute_query(query, params)
            
            # Redirigir a la lista de equipos con mensaje de éxito
            return redirect('/equipos?success=Equipo agregado correctamente')
            
        except Exception as e:
            # En caso de error, redirigir con mensaje de error
            return redirect('/equipos?error=Error al agregar el equipo: ' + str(e))
    
    # Si es GET, mostrar el formulario (aunque el modal se maneja en el frontend)
    return redirect('/equipos')

@app.route('/equipos/editar/<int:id>', methods=['POST'])
def editar_equipo(id):
    """Editar un equipo existente"""
    try:
        # Recoger datos del formulario
        nombre = request.form.get('nombre')
        fabricante = request.form.get('fabricante')
        contacto_fabricante = request.form.get('contacto_fabricante')
        ubicacion = request.form.get('ubicacion')
        fecha_compra = request.form.get('fecha_compra')
        potencia = request.form.get('potencia')
        voltaje = request.form.get('voltaje')
        tipo_alimentacion = request.form.get('tipo_alimentacion')
        potencia_motor = request.form.get('potencia_motor')
        relacion_motoreductor = request.form.get('relacion_motoreductor')
        diametro_polea = request.form.get('diametro_polea')
        
        # Query para actualizar
        query = """
            UPDATE equipos 
            SET nombre = %s, fabricante = %s, contacto_fabricante = %s, ubicacion = %s, 
                fecha_compra = %s, potencia = %s, voltaje = %s, tipo_alimentacion = %s, 
                potencia_motor = %s, relacion_motoreductor = %s, diametro_polea = %s
            WHERE id = %s
        """
        params = (nombre, fabricante, contacto_fabricante, ubicacion, fecha_compra, 
                 potencia, voltaje, tipo_alimentacion, potencia_motor, 
                 relacion_motoreductor, diametro_polea, id)
        
        db.execute_query(query, params)
        
        return redirect('/equipos?success=Equipo actualizado correctamente')
        
    except Exception as e:
        return redirect('/equipos?error=Error al actualizar el equipo: ' + str(e))

@app.route('/equipos/eliminar/<int:id>', methods=['POST'])
def eliminar_equipo(id):
    try:
        # 1. Primero eliminar fotos_mantenimiento relacionadas con mantenimientos de este equipo
        db.execute_query("""
            DELETE fm FROM fotos_mantenimiento fm 
            JOIN mantenimientos m ON fm.mantenimiento_id = m.id 
            WHERE m.equipo_id = %s
        """, (id,))
        
        # 2. Eliminar fotos_mantenimiento relacionadas con cronogramas de este equipo
        db.execute_query("""
            DELETE fm FROM fotos_mantenimiento fm 
            JOIN mantenimientos m ON fm.mantenimiento_id = m.id 
            JOIN cronograma c ON m.cronograma_id = c.id 
            WHERE c.equipo_id = %s
        """, (id,))
        
        # 3. Eliminar mantenimientos directos del equipo
        db.execute_query("DELETE FROM mantenimientos WHERE equipo_id = %s", (id,))
        
        # 4. Eliminar mantenimientos que referencian cronogramas de este equipo
        db.execute_query("""
            DELETE m FROM mantenimientos m 
            JOIN cronograma c ON m.cronograma_id = c.id 
            WHERE c.equipo_id = %s
        """, (id,))
        
        # 5. Eliminar los cronogramas del equipo
        db.execute_query("DELETE FROM cronograma WHERE equipo_id = %s", (id,))
        
        # 6. Finalmente eliminar el equipo
        db.execute_query("DELETE FROM equipos WHERE id = %s", (id,))
        
        return redirect('/equipos?success=Equipo y todos sus datos asociados eliminados correctamente')
        
    except Exception as e:
        return redirect('/equipos?error=Error al eliminar: ' + str(e))

@app.route('/api/equipos/<int:id>')
def obtener_equipo(id):
    """Obtener datos de un equipo específico para edición"""
    try:
        equipo = db.execute_query("SELECT * FROM equipos WHERE id = %s", (id,))
        
        if equipo:
            return jsonify(equipo[0])
        else:
            return jsonify({'error': 'Equipo no encontrado'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/equipos/<int:equipo_id>/detalle-completo')
def api_equipo_detalle_completo(equipo_id):
    try:
        # Obtener datos del equipo
        equipo = db.execute_query("""
            SELECT * FROM equipos WHERE id = %s
        """, (equipo_id,))
        
        if not equipo:
            return jsonify({'error': 'Equipo no encontrado'}), 404
        
        equipo_data = equipo[0]

        # Obtener estadísticas de mantenimientos - CON MANEJO DE NULL
        estadisticas_query = db.execute_query("""
            SELECT 
                COUNT(*) as total_mantenimientos,
                COALESCE(SUM(CASE WHEN tipo = 'correctivo' THEN 1 ELSE 0 END), 0) as correctivos,
                COALESCE(SUM(CASE WHEN tipo = 'preventivo' THEN 1 ELSE 0 END), 0) as preventivos_realizados
            FROM mantenimientos 
            WHERE equipo_id = %s
        """, (equipo_id,))
        
        # Manejar caso cuando no hay mantenimientos
        if estadisticas_query and len(estadisticas_query) > 0:
            estadisticas = estadisticas_query[0]
            # Asegurar que los valores no sean None
            estadisticas['correctivos'] = estadisticas['correctivos'] or 0
            estadisticas['preventivos_realizados'] = estadisticas['preventivos_realizados'] or 0
        else:
            estadisticas = {
                'total_mantenimientos': 0,
                'correctivos': 0,
                'preventivos_realizados': 0
            }

        # Obtener cantidad de preventivos programados (desde cronograma)
        preventivos_programados_query = db.execute_query("""
            SELECT COUNT(*) as total
            FROM cronograma 
            WHERE equipo_id = %s AND tipo = 'preventivo'
        """, (equipo_id,))

        preventivos_programados = preventivos_programados_query[0]['total'] if preventivos_programados_query and len(preventivos_programados_query) > 0 else 0

        # Calcular porcentaje de cumplimiento - CON VERIFICACIÓN DE CERO
        porcentaje_cumplimiento = 0
        if preventivos_programados > 0 and estadisticas['preventivos_realizados'] > 0:
            porcentaje_cumplimiento = round((estadisticas['preventivos_realizados'] / preventivos_programados) * 100, 2)

        # Obtener mantenimientos recientes (últimos 5)
        mantenimientos_recientes = db.execute_query("""
            SELECT id, fecha, tipo, descripcion, estado
            FROM mantenimientos 
            WHERE equipo_id = %s 
            ORDER BY fecha DESC 
            LIMIT 5
        """, (equipo_id,)) or []

        return jsonify({
            'equipo': equipo_data,
            'estadisticas': {
                'correctivos': estadisticas['correctivos'],
                'preventivos_realizados': estadisticas['preventivos_realizados'],
                'preventivos_programados': preventivos_programados,
                'porcentaje_cumplimiento': porcentaje_cumplimiento
            },
            'mantenimientos_recientes': mantenimientos_recientes
        })
        
    except Exception as e:
        print(f"Error en API equipo detalle: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500


@app.route('/mantenimientos')
def ver_mantenimientos():
    """Lista de mantenimientos con paginación y filtros"""
    # Obtener parámetros de filtro
    equipo_id = request.args.get('equipo_id', '')
    tipo = request.args.get('tipo', '')
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    pagina = request.args.get('pagina', 1, type=int)
    
    # Convertir equipo_id a int si no está vacío
    equipo_id_int = int(equipo_id) if equipo_id and equipo_id.isdigit() else None
    
    mantenimientos_por_pagina = 10
    offset = (pagina - 1) * mantenimientos_por_pagina

    # Construir consulta base con filtros
    query_base = """
        SELECT m.*, e.nombre as equipo_nombre 
        FROM mantenimientos m 
        JOIN equipos e ON m.equipo_id = e.id 
    """
    count_query = "SELECT COUNT(*) as total FROM mantenimientos m JOIN equipos e ON m.equipo_id = e.id"
    
    where_conditions = []
    params = []
    
    if equipo_id_int:
        where_conditions.append("m.equipo_id = %s")
        params.append(equipo_id_int)
    if tipo:
        where_conditions.append("m.tipo = %s")
        params.append(tipo)
    if fecha_desde:
        where_conditions.append("m.fecha >= %s")
        params.append(fecha_desde)
    if fecha_hasta:
        where_conditions.append("m.fecha <= %s")
        params.append(fecha_hasta)
    
    if where_conditions:
        where_clause = " WHERE " + " AND ".join(where_conditions)
    else:
        where_clause = ""
    
    # Consulta para los mantenimientos (con límite y offset)
    query = query_base + where_clause + " ORDER BY m.fecha DESC, m.hora DESC LIMIT %s OFFSET %s"
    params.extend([mantenimientos_por_pagina, offset])
    mantenimientos = db.execute_query(query, params) or []
    
    # Consulta para el total (sin límite/offset)
    count_result = db.execute_query(count_query + where_clause, params[:-2] if where_conditions else [])
    if count_result and len(count_result) > 0:
        total_resultados = count_result[0]['total']
    else:
        total_resultados = 0
        
    total_paginas = (total_resultados + mantenimientos_por_pagina - 1) // mantenimientos_por_pagina

    equipos = db.execute_query("SELECT id, nombre FROM equipos") or []
    
    return render_template('mantenimientos.html', 
                         mantenimientos=mantenimientos, 
                         equipos=equipos,
                         pagina_actual=pagina,
                         total_paginas=total_paginas,
                         total_resultados=total_resultados,
                         filtros_actuales={
                             'equipo_id': equipo_id, 
                             'tipo': tipo,
                             'fecha_desde': fecha_desde,
                             'fecha_hasta': fecha_hasta
                         })

@app.route('/api/mantenimientos/<int:mantenimiento_id>')
def api_mantenimiento(mantenimiento_id):
    """API para obtener datos de un mantenimiento específico incluyendo fotos"""
    # Obtener las fotos del mantenimiento desde la tabla fotos_mantenimiento
    query_fotos = "SELECT * FROM fotos_mantenimiento WHERE mantenimiento_id = %s"
    fotos = db.execute_query(query_fotos, [mantenimiento_id]) or []
    
    return jsonify({
        'id': mantenimiento_id,
        'fotos': fotos
    })

@app.route('/mantenimientos/pdf')
def generar_pdf_mantenimientos():
    """Genera un PDF con el historial de mantenimientos (con filtros)"""
    try:
        # Obtener parámetros de filtro
        equipo_id = request.args.get('equipo_id', type=int)
        tipo = request.args.get('tipo', type=str)
        fecha_desde = request.args.get('fecha_desde', type=str)
        fecha_hasta = request.args.get('fecha_hasta', type=str)
        
        # Construir consulta base
        query = """
            SELECT m.*, e.nombre as equipo_nombre 
            FROM mantenimientos m 
            JOIN equipos e ON m.equipo_id = e.id 
        """
        params = []
        
        # Aplicar filtros si existen
        where_conditions = []
        if equipo_id:
            where_conditions.append("m.equipo_id = %s")
            params.append(equipo_id)
        if tipo:
            where_conditions.append("m.tipo = %s")
            params.append(tipo)
        if fecha_desde:
            where_conditions.append("m.fecha >= %s")
            params.append(fecha_desde)
        if fecha_hasta:
            where_conditions.append("m.fecha <= %s")
            params.append(fecha_hasta)
        
        if where_conditions:
            query += " WHERE " + " AND ".join(where_conditions)
        
        query += " ORDER BY m.fecha DESC, m.hora DESC"
        
        # Obtener mantenimientos filtrados
        mantenimientos = db.execute_query(query, params) or []
        
        # Obtener las fotos para cada mantenimiento
        for mtto in mantenimientos:
            fotos = db.execute_query("""
                SELECT ruta_archivo 
                FROM fotos_mantenimiento 
                WHERE mantenimiento_id = %s
            """, (mtto['id'],)) or []
            mtto['fotos'] = fotos
        
        # Determinar título del reporte según filtros
        titulo_reporte = "Reporte de Mantenimientos"
        filtros_aplicados = []
        
        if equipo_id:
            equipo = db.execute_query("SELECT nombre FROM equipos WHERE id = %s", (equipo_id,))
            equipo_nombre = equipo[0]['nombre'] if equipo else f"Equipo #{equipo_id}"
            filtros_aplicados.append(f"Equipo: {equipo_nombre}")
        if tipo:
            filtros_aplicados.append(f"Tipo: {tipo}")
        if fecha_desde:
            filtros_aplicados.append(f"Desde: {fecha_desde}")
        if fecha_hasta:
            filtros_aplicados.append(f"Hasta: {fecha_hasta}")
            
        if filtros_aplicados:
            titulo_reporte += " - " + ", ".join(filtros_aplicados)
        
        # Renderizar el HTML para el PDF
        html = render_template('pdf_mantenimientos.html', 
                             mantenimientos=mantenimientos,
                             titulo_reporte=titulo_reporte,
                             fecha_generacion=datetime.now().strftime("%d/%m/%Y %H:%M"))
        
        # Generar PDF con WeasyPrint
        pdf = HTML(string=html).write_pdf()

        # Crear respuesta
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=reporte_mantenimientos.pdf'
        
        return response
        
    except Exception as e:
        flash(f'Error generando PDF: {str(e)}', 'error')
        return redirect(url_for('ver_mantenimientos'))

@app.route('/cronograma/pdf')
def generar_pdf_cronograma():
    """Genera un PDF con el cronograma de mantenimientos (con filtros)"""
    try:
        # Obtener parámetros de filtro
        equipo_id = request.args.get('equipo_id', type=int)
        tipo = request.args.get('tipo', type=str)
        fecha_desde = request.args.get('fecha_desde', type=str)
        fecha_hasta = request.args.get('fecha_hasta', type=str)
        
        # Construir consulta base - EXCLUIR PREDICTIVOS
        query = """
            SELECT c.*, e.nombre as equipo_nombre 
            FROM cronograma c 
            JOIN equipos e ON c.equipo_id = e.id 
            WHERE c.tipo IN ('preventivo', 'correctivo')
        """
        params = []
        
        # Aplicar filtros adicionales si existen
        where_conditions = []
        if equipo_id:
            where_conditions.append("c.equipo_id = %s")
            params.append(equipo_id)
        if tipo and tipo in ['preventivo', 'correctivo']:
            where_conditions.append("c.tipo = %s")
            params.append(tipo)
        if fecha_desde:
            where_conditions.append("c.proximo_mtto >= %s")
            params.append(fecha_desde)
        if fecha_hasta:
            where_conditions.append("c.proximo_mtto <= %s")
            params.append(fecha_hasta)
        
        if where_conditions:
            query += " AND " + " AND ".join(where_conditions)
        
        # Ordenar por equipo y fecha próxima
        query += " ORDER BY e.nombre, c.proximo_mtto ASC"
        
        # Obtener cronogramas filtrados
        cronogramas = db.execute_query(query, params) or []
        
        # Determinar rango de fechas para calendario
        hoy = date.today()
        if fecha_desde and fecha_hasta:
            # Usar rango de filtros
            start_date = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            end_date = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        else:
            # Usar mes actual por defecto
            start_date = hoy.replace(day=1)
            next_month = start_date.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)
        
        # Precalcular calendarios para cada mes
        MESES_ESPANOL = {
            'January': 'Enero',
            'February': 'Febrero', 
            'March': 'Marzo',
            'April': 'Abril',
            'May': 'Mayo',
            'June': 'Junio',
            'July': 'Julio',
            'August': 'Agosto',
            'September': 'Septiembre',
            'October': 'Octubre',
            'November': 'Noviembre',
            'December': 'Diciembre'
        }
        
        # Precalcular calendarios para cada mes
        calendarios_mensuales = []
        current_month_start = start_date.replace(day=1)
        
        while current_month_start <= end_date:
            # Calcular último día del mes
            next_month = current_month_start.replace(day=28) + timedelta(days=4)
            current_month_end = next_month - timedelta(days=next_month.day)
            
            # Generar semanas para este mes
            semanas = generar_calendario_mensual(current_month_start, current_month_end, cronogramas, hoy)
            
            # Obtener nombre del mes en español
            mes_ingles = current_month_start.strftime('%B')
            mes_espanol = MESES_ESPANOL.get(mes_ingles, mes_ingles)
            
            calendarios_mensuales.append({
                'mes_nombre': f"{mes_espanol} {current_month_start.year}",
                'semanas': semanas,
                'first_day': current_month_start,
                'last_day': current_month_end
            })
            
            # Siguiente mes
            current_month_start = (current_month_end + timedelta(days=1)).replace(day=1)
        
        # Determinar título del reporte según filtros
        titulo_reporte = "Cronograma de Mantenimiento"
        filtros_aplicados = []
        
        if equipo_id:
            equipo = db.execute_query("SELECT nombre FROM equipos WHERE id = %s", (equipo_id,))
            equipo_nombre = equipo[0]['nombre'] if equipo else f"Equipo #{equipo_id}"
            filtros_aplicados.append(f"Equipo: {equipo_nombre}")
        if tipo:
            filtros_aplicados.append(f"Tipo: {tipo}")
        if fecha_desde:
            filtros_aplicados.append(f"Desde: {fecha_desde}")
        if fecha_hasta:
            filtros_aplicados.append(f"Hasta: {fecha_hasta}")
            
        if filtros_aplicados:
            titulo_reporte += " - " + ", ".join(filtros_aplicados)
        
        # Renderizar el HTML para el PDF
        html = render_template('pdf_cronograma.html', 
                             cronogramas=cronogramas,
                             titulo_reporte=titulo_reporte,
                             fecha_generacion=datetime.now().strftime("%d/%m/%Y %H:%M"),
                             calendarios_mensuales=calendarios_mensuales,
                             hoy=hoy)
        
        # Generar PDF con WeasyPrint
        pdf = HTML(string=html).write_pdf()
        
        # Crear respuesta
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=cronograma_mantenimiento.pdf'
        
        return response
        
    except Exception as e:
        print(f'Error generando PDF: {str(e)}')
        import traceback
        traceback.print_exc()
        return redirect(url_for('cronograma'))

def generar_calendario_mensual(first_day, last_day, cronogramas, hoy):
    """Genera la estructura del calendario para un mes específico"""
    # Encontrar el primer día a mostrar (domingo de la primera semana)
    start_date = first_day - timedelta(days=(first_day.weekday() + 1) % 7)
    
    semanas = []
    current_date = start_date
    
    # Generar 6 semanas
    for week in range(6):
        semana = []
        for day in range(7):
            # Encontrar eventos para este día
            day_events = []
            for cronograma in cronogramas:
                if cronograma['proximo_mtto'] and cronograma['proximo_mtto'] == current_date:
                    day_events.append(cronograma)
            
            semana.append({
                'fecha': current_date,
                'es_mes_actual': first_day <= current_date <= last_day,
                'eventos': day_events[:2],  # Máximo 2 eventos mostrados
                'total_eventos': len(day_events),
                'hay_mas_eventos': len(day_events) > 2
            })
            
            current_date += timedelta(days=1)
        
        semanas.append(semana)
        
        # Si hemos pasado el último día, salir
        if current_date > last_day:
            break
    
    return semanas

@app.route('/reportar', methods=['GET', 'POST'])
def reportar_mantenimiento():
    """Formulario para reportar mantenimiento"""
    if request.method == 'POST':
        # Obtener datos del formulario
        equipo_id = request.form['equipo_id']
        fecha = request.form['fecha']
        hora_actual = datetime.now().time().strftime('%H:%M:%S')
        tipo = request.form['tipo']
        descripcion = request.form['descripcion']
        cronograma_id = request.form.get('cronograma_id') or None
        
        # Insertar mantenimiento
        mantenimiento_id = db.execute_query("""
            INSERT INTO mantenimientos (equipo_id, fecha, tipo, descripcion, hora, cronograma_id) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (equipo_id, fecha, tipo, descripcion, hora_actual, cronograma_id))
        
        if mantenimiento_id:
            # Si se seleccionó un cronograma, actualizarlo
            if cronograma_id and cronograma_id != '':
                # Actualizar último mantenimiento en el cronograma
                db.execute_query("""
                    UPDATE cronograma 
                    SET ultimo_mtto = %s 
                    WHERE id = %s
                """, (fecha, cronograma_id))
                
                # Calcular próximo mantenimiento si hay frecuencia
                cronograma = db.execute_query("""
                    SELECT frecuencia FROM cronograma WHERE id = %s
                """, (cronograma_id,))
                
                if cronograma and cronograma[0]['frecuencia']:
                    db.execute_query("""
                        UPDATE cronograma 
                        SET proximo_mtto = DATE_ADD(%s, INTERVAL %s DAY)
                        WHERE id = %s
                    """, (fecha, cronograma[0]['frecuencia'], cronograma_id))
            
            # Procesar fotos - CON INDENTACIÓN CORRECTA
            fotos_antes = request.files.getlist('fotos_antes')
            fotos_despues = request.files.getlist('fotos_despues')
            
            # Guardar fotos "antes" con índice para nombres únicos
            for index, foto in enumerate(fotos_antes):
                if foto.filename:
                    filename = guardar_foto(foto, mantenimiento_id, 'antes', index)
                    if filename:
                        db.execute_query("""
                            INSERT INTO fotos_mantenimiento (mantenimiento_id, ruta_archivo, tipo) 
                            VALUES (%s, %s, %s)
                        """, (mantenimiento_id, filename, 'antes'))
            
            # Guardar fotos "después" con índice para nombres únicos
            for index, foto in enumerate(fotos_despues):
                if foto.filename:
                    filename = guardar_foto(foto, mantenimiento_id, 'despues', index)
                    if filename:
                        db.execute_query("""
                            INSERT INTO fotos_mantenimiento (mantenimiento_id, ruta_archivo, tipo) 
                            VALUES (%s, %s, %s)
                        """, (mantenimiento_id, filename, 'despues'))
            
            # ESTAS LÍNEAS DEBEN ESTAR AQUÍ - FUERA DE LOS BUCLES
            flash('Mantenimiento reportado exitosamente!', 'success')
            return redirect(url_for('ver_mantenimientos'))
        else:
            flash('Error al guardar el mantenimiento', 'error')
    
    # Si es GET, mostrar formulario (ESTE CÓDIGO DEBE ESTAR FUERA DEL BLOQUE POST)
    equipos = db.execute_query("SELECT id, nombre FROM equipos") or []

    # Obtener cronograma_id si viene por parámetro
    cronograma_id = request.args.get('cronograma_id')
    cronograma_seleccionado = None

    # Obtener TODOS los cronogramas activos (sin filtrar por equipo)
    cronogramas = db.execute_query("""
        SELECT c.*, e.nombre as equipo_nombre 
        FROM cronograma c 
        JOIN equipos e ON c.equipo_id = e.id 
        WHERE c.proximo_mtto IS NOT NULL
        ORDER BY c.proximo_mtto ASC 
        LIMIT 50
    """) or []

    # Si viene un cronograma específico, obtener sus datos
    if cronograma_id:
        cronograma_seleccionado = db.execute_query("""
            SELECT c.*, e.nombre as equipo_nombre 
            FROM cronograma c 
            JOIN equipos e ON c.equipo_id = e.id 
            WHERE c.id = %s
        """, (cronograma_id,))
        
        if cronograma_seleccionado:
            cronograma_seleccionado = cronograma_seleccionado[0]

    return render_template('reportar.html', 
                         equipos=equipos, 
                         cronogramas=cronogramas,
                         cronograma_seleccionado=cronograma_seleccionado)


@app.route('/cronograma')
def cronograma():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Obtener parámetros de filtro
    equipo_id = request.args.get('equipo_id', '')
    tipo = request.args.get('tipo', '')
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    pagina = request.args.get('pagina', 1, type=int)
    
    # Convertir equipo_id a int si no está vacío
    equipo_id_int = int(equipo_id) if equipo_id and equipo_id.isdigit() else None
    
    elementos_por_pagina = 10
    offset = (pagina - 1) * elementos_por_pagina

    # Construir consulta base con filtros
    query_base = """
        SELECT c.*, e.nombre as equipo_nombre 
        FROM cronograma c 
        JOIN equipos e ON c.equipo_id = e.id 
    """
    count_query = "SELECT COUNT(*) as total FROM cronograma c JOIN equipos e ON c.equipo_id = e.id"
    
    where_conditions = []
    params = []
    
    if equipo_id_int:
        where_conditions.append("c.equipo_id = %s")
        params.append(equipo_id_int)
    if tipo:
        where_conditions.append("c.tipo = %s")
        params.append(tipo)
    if fecha_desde:
        where_conditions.append("c.proximo_mtto >= %s")
        params.append(fecha_desde)
    if fecha_hasta:
        where_conditions.append("c.proximo_mtto <= %s")
        params.append(fecha_hasta)
    
    if where_conditions:
        where_clause = " WHERE " + " AND ".join(where_conditions)
    else:
        where_clause = ""
    
    # Consulta para los cronogramas (con límite y offset)
    query = query_base + where_clause + " ORDER BY c.proximo_mtto ASC LIMIT %s OFFSET %s"
    params.extend([elementos_por_pagina, offset])
    cronogramas = db.execute_query(query, params) or []
    
    # Consulta para el total (sin límite/offset)
    count_result = db.execute_query(count_query + where_clause, params[:-2] if where_conditions else [])
    if count_result and len(count_result) > 0:
        total_resultados = count_result[0]['total']
    else:
        total_resultados = 0
        
    total_paginas = (total_resultados + elementos_por_pagina - 1) // elementos_por_pagina

    # Obtener todos los equipos para el filtro
    equipos = db.execute_query("SELECT id, nombre FROM equipos") or []
    
    return render_template('cronograma.html',
                         cronogramas=cronogramas,
                         equipos=equipos,
                         pagina_actual=pagina,
                         total_paginas=total_paginas,
                         total_resultados=total_resultados,
                         filtros_actuales={
                             'equipo_id': equipo_id, 
                             'tipo': tipo,
                             'fecha_desde': fecha_desde,
                             'fecha_hasta': fecha_hasta
                         },
                         hoy=date.today())
@app.route('/crear_cronograma', methods=['POST'])
def crear_cronograma():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        equipo_id = request.form['equipo_id']
        tipo = request.form['tipo']
        subcategoria = request.form.get('subcategoria', '')
        frecuencia = request.form['frecuencia']
        
        print(f"Datos recibidos: equipo_id={equipo_id}, tipo={tipo}, subcategoria={subcategoria}, frecuencia={frecuencia}")
        
        # Validar que la frecuencia sea un número positivo
        if not frecuencia.isdigit() or int(frecuencia) <= 0:
            flash('La frecuencia debe ser un número positivo', 'error')
            return redirect(url_for('cronograma'))
        
        # Calcular próximo mantenimiento (hoy + frecuencia días)
        proximo_mtto = date.today() + timedelta(days=int(frecuencia))
        
        # Insertar en la base de datos usando execute_query
        query = """
            INSERT INTO cronograma (equipo_id, tipo, subcategoria, frecuencia, ultimo_mtto, proximo_mtto)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (equipo_id, tipo, subcategoria, frecuencia, None, proximo_mtto)
        
        print(f"Ejecutando query: {query}")
        print(f"Con parámetros: {params}")
        
        # Usar execute_query que ya tienes implementado
        result = db.execute_query(query, params)
        print(f"Resultado: {result}")
        
        if result is not None:
            flash('Cronograma creado exitosamente', 'success')
        else:
            flash('Error al crear cronograma: no se pudo insertar', 'error')
        
        return redirect(url_for('cronograma'))
        
    except Exception as e:
        print(f"ERROR en crear_cronograma: {str(e)}")
        flash(f'Error al crear cronograma: {str(e)}', 'error')
        return redirect(url_for('cronograma'))

@app.route('/cronograma/<int:id>/editar', methods=['POST'])
def editar_cronograma(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        equipo_id = request.form['equipo_id']
        tipo = request.form['tipo']
        subcategoria = request.form.get('subcategoria', '')
        frecuencia = request.form['frecuencia']
        
        print(f"Editando cronograma {id}: equipo_id={equipo_id}, tipo={tipo}, subcategoria={subcategoria}, frecuencia={frecuencia}")
        
        # Obtener el cronograma actual para preservar las fechas
        cronograma_actual = db.execute_query(
            "SELECT ultimo_mtto, proximo_mtto FROM cronograma WHERE id = %s", 
            [id]
        )
        
        if not cronograma_actual:
            flash('Cronograma no encontrado', 'error')
            return redirect(url_for('cronograma'))
        
        ultimo_mtto = cronograma_actual[0]['ultimo_mtto']
        proximo_mtto = cronograma_actual[0]['proximo_mtto']
        
        # Si hay último mantenimiento, recalcular próximo
        if ultimo_mtto:
            proximo_mtto = ultimo_mtto + timedelta(days=int(frecuencia))
        
        # Actualizar en la base de datos
        query = """
            UPDATE cronograma 
            SET equipo_id = %s, tipo = %s, subcategoria = %s, frecuencia = %s, proximo_mtto = %s
            WHERE id = %s
        """
        params = (equipo_id, tipo, subcategoria, frecuencia, proximo_mtto, id)
        
        result = db.execute_query(query, params)
        print(f"Resultado edición: {result}")
        
        if result is not None:
            flash('Cronograma actualizado exitosamente', 'success')
        else:
            flash('Error al actualizar cronograma', 'error')
        
        return redirect(url_for('cronograma'))
        
    except Exception as e:
        print(f"ERROR en editar_cronograma: {str(e)}")
        flash(f'Error al actualizar cronograma: {str(e)}', 'error')
        return redirect(url_for('cronograma'))

@app.route('/cronograma/<int:id>/eliminar', methods=['DELETE'])
def eliminar_cronograma(id):
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # Primero eliminar las fotos asociadas a los mantenimientos del cronograma
        db.execute_query("""
            DELETE FROM fotos_mantenimiento 
            WHERE mantenimiento_id IN (
                SELECT id FROM mantenimientos WHERE cronograma_id = %s
            )
        """, [id])
        
        # Luego eliminar los repuestos asociados a los mantenimientos del cronograma
        db.execute_query("""
            DELETE FROM repuestos 
            WHERE mantenimiento_id IN (
                SELECT id FROM mantenimientos WHERE cronograma_id = %s
            )
        """, [id])
        
        # Luego eliminar los mantenimientos asociados al cronograma
        db.execute_query("DELETE FROM mantenimientos WHERE cronograma_id = %s", [id])
        
        # Finalmente eliminar el cronograma
        result = db.execute_query("DELETE FROM cronograma WHERE id = %s", [id])
        
        if result is not None:
            return jsonify({'message': 'Cronograma eliminado exitosamente'}), 200
        else:
            return jsonify({'error': 'Error al eliminar cronograma'}), 500
        
    except Exception as e:
        print(f"ERROR en eliminar_cronograma: {str(e)}")
        return jsonify({'error': f'Error al eliminar cronograma: {str(e)}'}), 500

@app.route('/api/cronograma/<int:id>')
def obtener_cronograma(id):
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        print(f"Buscando cronograma con ID: {id}")  # Debug
        
        cronograma = db.execute_query(
            "SELECT * FROM cronograma WHERE id = %s", 
            [id]
        )
        
        print(f"Resultado de la consulta: {cronograma}")  # Debug
        
        if not cronograma:
            print(f"Cronograma con ID {id} no encontrado")  # Debug
            return jsonify({'error': 'Cronograma no encontrado'}), 404
        
        # Convertir dates a string para JSON
        cronograma_data = cronograma[0]
        if cronograma_data.get('ultimo_mtto'):
            cronograma_data['ultimo_mtto'] = cronograma_data['ultimo_mtto'].strftime('%Y-%m-%d')
        if cronograma_data.get('proximo_mtto'):
            cronograma_data['proximo_mtto'] = cronograma_data['proximo_mtto'].strftime('%Y-%m-%d')
        
        return jsonify(cronograma_data)
        
    except Exception as e:
        print(f"ERROR en obtener_cronograma: {str(e)}")
        return jsonify({'error': str(e)}), 500
# ==================== RUTAS API PARA POSTMAN ====================

@app.route('/api/equipos', methods=['GET'])
def api_equipos():
    """Devuelve todos los equipos en JSON"""
    equipos = db.execute_query("SELECT * FROM equipos") or []
    return jsonify({'equipos': equipos, 'total': len(equipos)})

@app.route('/api/equipos/<int:equipo_id>', methods=['GET'])
def api_equipo_detalle(equipo_id):
    """Devuelve un equipo específico con sus mantenimientos"""
    equipo = db.execute_query("SELECT * FROM equipos WHERE id = %s", (equipo_id,))
    if not equipo:
        return jsonify({'error': 'Equipo no encontrado'}), 404
    
    mantenimientos = db.execute_query("""
        SELECT m.* 
        FROM mantenimientos m 
        WHERE m.equipo_id = %s 
        ORDER BY m.fecha DESC
    """, (equipo_id,)) or []
    
    return jsonify({
        'equipo': equipo[0],
        'mantenimientos': mantenimientos
    })

@app.route('/api/mantenimientos', methods=['GET', 'POST'])
def api_mantenimientos():
    """GET: Lista todos los mantenimientos | POST: Crea nuevo mantenimiento"""
    
    if request.method == 'GET':
        mantenimientos = db.execute_query("""
            SELECT m.*, e.nombre as equipo_nombre 
            FROM mantenimientos m 
            JOIN equipos e ON m.equipo_id = e.id 
            ORDER BY m.fecha DESC
        """) or []
        return jsonify({'mantenimientos': mantenimientos})
    
    elif request.method == 'POST':
        # Crear nuevo mantenimiento desde JSON
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Datos JSON requeridos'}), 400
        
        required_fields = ['equipo_id', 'fecha', 'tipo', 'descripcion']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        # Insertar mantenimiento
        mantenimiento_id = db.execute_query("""
            INSERT INTO mantenimientos (equipo_id, fecha, tipo, descripcion) 
            VALUES (%s, %s, %s, %s)
        """, (data['equipo_id'], data['fecha'], data['tipo'], data['descripcion']))
        
        if mantenimiento_id:
            return jsonify({
                'message': 'Mantenimiento creado exitosamente',
                'mantenimiento_id': mantenimiento_id
            }), 201
        else:
            return jsonify({'error': 'Error al crear mantenimiento'}), 500

@app.route('/api/mantenimientos/<int:mantenimiento_id>', methods=['GET'])
def api_mantenimiento_detalle(mantenimiento_id):
    """Devuelve un mantenimiento específico con sus fotos y repuestos"""
    try:
        # Consulta sin la columna hora para evitar problemas
        mantenimiento = db.execute_query("""
            SELECT m.id, m.equipo_id, m.fecha, m.tipo, m.descripcion, m.estado, 
                   e.nombre as equipo_nombre 
            FROM mantenimientos m 
            JOIN equipos e ON m.equipo_id = e.id 
            WHERE m.id = %s
        """, (mantenimiento_id,))
        
        if not mantenimiento:
            return jsonify({'error': 'Mantenimiento no encontrado'}), 404
        
        # Solo obtener fotos si la tabla existe
        fotos = []
        try:
            # Verificar si la tabla existe
            table_exists = db.execute_query("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'fotos_mantenimiento'
            """)
            
            if table_exists:
                fotos = db.execute_query("""
                    SELECT ruta_archivo, tipo
                    FROM fotos_mantenimiento
                    WHERE mantenimiento_id = %s
                """, (mantenimiento_id,)) or []
        except Exception as e:
            print(f"Error obteniendo fotos: {e}")
        
        repuestos = db.execute_query("""
            SELECT * FROM repuestos 
            WHERE mantenimiento_id = %s
        """, (mantenimiento_id,)) or []
        
        return jsonify({
            'mantenimiento': mantenimiento[0],
            'fotos': fotos,
            'repuestos': repuestos
        })
        
    except Exception as e:
        print(f"Error en API mantenimiento detalle: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/mantenimientos/<int:mantenimiento_id>/detalle', methods=['GET'])
def api_mantenimiento_detalle_completo(mantenimiento_id):
    """Devuelve un mantenimiento específico con todos sus detalles, fotos y repuestos"""
    try:
        # Consulta principal del mantenimiento
        mantenimiento = db.execute_query("""
            SELECT m.id, m.equipo_id, m.fecha, m.tipo, m.descripcion, m.estado, 
                   m.hora, m.cronograma_id, e.nombre as equipo_nombre 
            FROM mantenimientos m 
            JOIN equipos e ON m.equipo_id = e.id 
            WHERE m.id = %s
        """, (mantenimiento_id,))
        
        if not mantenimiento:
            return jsonify({'error': 'Mantenimiento no encontrado'}), 404
        
        mantenimiento_data = mantenimiento[0]
        
        # Obtener fotos
        fotos = []
        try:
            fotos = db.execute_query("""
                SELECT id, ruta_archivo, tipo
                FROM fotos_mantenimiento
                WHERE mantenimiento_id = %s
            """, (mantenimiento_id,)) or []
        except Exception as e:
            print(f"Error obteniendo fotos: {e}")
        
        # Obtener repuestos
        repuestos = []
        try:
            repuestos = db.execute_query("""
                SELECT id, nombre, cantidad
                FROM repuestos
                WHERE mantenimiento_id = %s
            """, (mantenimiento_id,)) or []
        except Exception as e:
            print(f"Error obteniendo repuestos: {e}")
        
        # Obtener información del cronograma si existe
        cronograma_info = None
        if mantenimiento_data.get('cronograma_id'):
            try:
                cronograma = db.execute_query("""
                    SELECT tipo, subcategoria, frecuencia
                    FROM cronograma
                    WHERE id = %s
                """, (mantenimiento_data['cronograma_id'],))
                if cronograma:
                    cronograma_info = cronograma[0]
            except Exception as e:
                print(f"Error obteniendo cronograma: {e}")
        
        return jsonify({
            'id': mantenimiento_data['id'],
            'equipo_id': mantenimiento_data['equipo_id'],
            'equipo_nombre': mantenimiento_data['equipo_nombre'],
            'fecha': mantenimiento_data['fecha'].strftime('%Y-%m-%d') if mantenimiento_data['fecha'] else None,
            'hora': str(mantenimiento_data['hora']) if mantenimiento_data['hora'] else None,
            'tipo': mantenimiento_data['tipo'],
            'descripcion': mantenimiento_data['descripcion'],
            'estado': mantenimiento_data['estado'],
            'cronograma_id': mantenimiento_data['cronograma_id'],
            'cronograma_info': cronograma_info,
            'fotos': fotos,
            'repuestos': repuestos
        })
        
    except Exception as e:
        print(f"Error en API mantenimiento detalle completo: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/mantenimiento/<int:mantenimiento_id>/pdf')
def generar_pdf_mantenimiento(mantenimiento_id):
    try:
        # Obtener datos completos del mantenimiento
        mantenimiento = db.execute_query("""
            SELECT m.id, m.equipo_id, m.fecha, m.tipo, m.descripcion, m.estado, 
                   m.hora, m.cronograma_id, e.nombre as equipo_nombre,
                   e.fabricante, e.ubicacion, e.fecha_compra
            FROM mantenimientos m 
            JOIN equipos e ON m.equipo_id = e.id 
            WHERE m.id = %s
        """, (mantenimiento_id,))

        if not mantenimiento:
            return "Mantenimiento no encontrado", 404

        mantenimiento_data = mantenimiento[0]

        # Obtener fotos
        fotos = db.execute_query("""
            SELECT ruta_archivo, tipo
            FROM fotos_mantenimiento
            WHERE mantenimiento_id = %s
        """, (mantenimiento_id,)) or []

        # Obtener repuestos
        repuestos = db.execute_query("""
            SELECT nombre, cantidad
            FROM repuestos
            WHERE mantenimiento_id = %s
        """, (mantenimiento_id,)) or []

        # Obtener información del cronograma
        cronograma_info = None
        if mantenimiento_data.get('cronograma_id'):
            cronograma = db.execute_query("""
                SELECT tipo, subcategoria, frecuencia
                FROM cronograma
                WHERE id = %s
            """, (mantenimiento_data['cronograma_id'],))
            if cronograma:
                cronograma_info = cronograma[0]

        # Generar gráficas
        grafica_estadisticas = generar_grafica_estadisticas(mantenimiento_data)
        grafica_tiempos = generar_grafica_tiempos(mantenimiento_data)

        # Renderizar template HTML
        html = render_template('reporte_pdf.html',
                            mantenimiento=mantenimiento_data,
                            fotos=fotos,
                            repuestos=repuestos,
                            cronograma_info=cronograma_info,
                            grafica_estadisticas=grafica_estadisticas,
                            grafica_tiempos=grafica_tiempos,
                            fecha_reporte=datetime.now().strftime('%d/%m/%Y %H:%M'))

        # Configuración de PDFKit
        try:
            options = {
                'page-size': 'A4',
                'margin-top': '1.0cm',
                'margin-right': '1.0cm',
                'margin-bottom': '1.0cm',
                'margin-left': '1.0cm',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None
            }
            
            pdf = HTML(string=html).write_pdf()
        except Exception as e:
            print(f"Error con PDFKit PATH: {e}")
            # Opción 2: Ruta específica de wkhtmltopdf
            posibles_rutas = [
                'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe',
                'C:/wkhtmltopdf/bin/wkhtmltopdf.exe',
                'wkhtmltopdf.exe'
            ]
            
            for ruta in posibles_rutas:
                if os.path.exists(ruta):
                    options = {
                        'page-size': 'A4',
                        'margin-top': '1.0cm',
                        'margin-right': '1.0cm',
                        'margin-bottom': '1.0cm',
                        'margin-left': '1.0cm',
                        'encoding': "UTF-8",
                        'no-outline': None,
                        'enable-local-file-access': None
                    }
                    pdf = HTML(string=html).write_pdf()
                    break
            else:
                raise Exception("No se encontró wkhtmltopdf instalado")

        # Crear respuesta
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=reporte_mantenimiento_{mantenimiento_id}.pdf'
        return response

    except Exception as e:
        print(f"Error generando PDF: {e}")
        return f"Error al generar el PDF: {str(e)}", 500

def generar_grafica_estadisticas(mantenimiento):
    """Genera gráfica de estadísticas del mantenimiento"""
    try:
        # Datos de ejemplo para la gráfica
        labels = ['Preventivo', 'Correctivo', 'Predictivo']
        sizes = [0, 0, 0]
        
        # Contar por tipo
        if mantenimiento['tipo'] == 'preventivo':
            sizes[0] = 1
        elif mantenimiento['tipo'] == 'correctivo':
            sizes[1] = 1
        else:
            sizes[2] = 1

        fig, ax = plt.subplots(figsize=(6, 4))
        colors = ['#4CAF50', '#F44336', '#2196F3']
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        ax.set_title('Distribución por Tipo de Mantenimiento')

        # Convertir a base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return image_base64
    except Exception as e:
        print(f"Error generando gráfica de estadísticas: {e}")
        return None

def generar_grafica_tiempos(mantenimiento):
    """Genera gráfica de línea de tiempo"""
    try:
        fig, ax = plt.subplots(figsize=(8, 3))
        
        # Datos de ejemplo
        eventos = ['Programado', 'Inicio', 'Finalización']
        tiempos = [0, 0.3, 1.0]  # Tiempos relativos
        
        ax.plot(tiempos, [1, 1, 1], 'o-', linewidth=2, markersize=8)
        ax.set_yticks([1])
        ax.set_yticklabels(['Proceso'])
        ax.set_xticks(tiempos)
        ax.set_xticklabels(eventos)
        ax.set_title('Línea de Tiempo del Mantenimiento')
        ax.grid(True, alpha=0.3)
        
        # Convertir a base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return image_base64
    except Exception as e:
        print(f"Error generando gráfica de tiempos: {e}")
        return None


@app.route('/api/test-connection', methods=['GET'])
def test_connection():
    """Endpoint para probar conexión a la base de datos"""
    try:
        result = db.execute_query("SELECT 1 as test")
        if result:
            return jsonify({
                'status': 'success',
                'message': 'Conexión a la base de datos exitosa',
                'database': 'gestion_mantenimiento'
            })
        else:
            return jsonify({'error': 'Error en la consulta de prueba'}), 500
    except Exception as e:
        return jsonify({'error': f'Error de conexión: {str(e)}'}), 500

# Manejo de error para archivos demasiado grandes
@app.errorhandler(413)
def too_large(e):
    flash('El tamaño total de las imágenes es demasiado grande. Por favor, reduzca el tamaño o la cantidad de fotos.', 'error')
    return redirect(request.url)

# ==================== FIN RUTAS API ====================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)