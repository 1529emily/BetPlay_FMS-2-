import streamlit as st
from datetime import date
from streamlit_autorefresh import st_autorefresh
import json
import os

# Configuración básica del coordinador
USUARIO_COORDINADOR = "admin"
CONTRASENA_COORDINADOR = "1234"

PARTIDO_FILE = "partido.json"
PREDICCIONES_FILE = "predicciones.json"

# Funciones para cargar y guardar datos
def guardar_partido(partido):
    with open(PARTIDO_FILE, "w") as f:
        json.dump(partido, f)

def cargar_partido():
    if os.path.exists(PARTIDO_FILE):
        with open(PARTIDO_FILE, "r") as f:
            return json.load(f)
    return None

def guardar_predicciones(predicciones):
    with open(PREDICCIONES_FILE, "w") as f:
        json.dump(predicciones, f)

def cargar_predicciones():
    if os.path.exists(PREDICCIONES_FILE):
        with open(PREDICCIONES_FILE, "r") as f:
            return json.load(f)
    return []

st.title("Bienvenido a Betplay FMS ⚽")
st.write("Esta aplicación permite registrar predicciones de partidos y ver quién gana según el marcador real.")

opcion = st.sidebar.selectbox("Selecciona una opción:", ["🧑‍💼 Coordinador", "👥 Usuarios"])

if opcion == "🧑‍💼 Coordinador":
    st.header("Panel del Coordinador - Fijar partido")

    if "logueado" not in st.session_state:
        st.session_state.logueado = False

    if not st.session_state.logueado:
        usuario = st.text_input("Usuario")
        contrasena = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if usuario == USUARIO_COORDINADOR and contrasena == CONTRASENA_COORDINADOR:
                st.session_state.logueado = True
                st.success("✅ Acceso concedido")
            else:
                st.error("❌ Usuario o contraseña incorrectos.")
    else:
        st.success("👤 Usuario coordinador logueado")

        # Fijar partido
        fecha = st.date_input("📅 Fecha del partido", value=date.today())
        equipo_local = st.text_input("🏠 Nombre del equipo local")
        equipo_visitante = st.text_input("🛫 Nombre del equipo visitante")

        if st.button("Fijar partido"):
            if equipo_local and equipo_visitante:
                partido = {
                    "fecha": fecha.strftime("%Y-%m-%d"),
                    "local": equipo_local.strip(),
                    "visitante": equipo_visitante.strip(),
                    "marcador_en_vivo": [0, 0],
                    "resultado_final": None,
                    "final_fijado": False,
                }
                guardar_partido(partido)
                st.success(f"🎯 Partido fijado: {equipo_local} vs {equipo_visitante} el {fecha.strftime('%Y-%m-%d')}")
            else:
                st.error("⚠️ Debes ingresar los nombres de ambos equipos.")

        partido = cargar_partido()
        if partido:
            st.markdown("---")
            st.subheader("✏️ Actualizar marcador en vivo")

            goles_local_en_vivo = st.number_input("Goles equipo local (en vivo)", min_value=0, step=1,
                                                  value=partido["marcador_en_vivo"][0])
            goles_visitante_en_vivo = st.number_input("Goles equipo visitante (en vivo)", min_value=0, step=1,
                                                       value=partido["marcador_en_vivo"][1])

            if st.button("Actualizar marcador en vivo"):
                partido["marcador_en_vivo"] = [goles_local_en_vivo, goles_visitante_en_vivo]
                guardar_partido(partido)
                st.success("✅ Marcador en vivo actualizado")

            st.markdown("---")
            st.subheader("📢 Fijar resultado final")

            if not partido["final_fijado"]:
                goles_local_final = st.number_input("Goles equipo local (final)", min_value=0, step=1)
                goles_visitante_final = st.number_input("Goles equipo visitante (final)", min_value=0, step=1)

                if st.button("Fijar resultado final"):
                    partido["resultado_final"] = [goles_local_final, goles_visitante_final]
                    partido["final_fijado"] = True
                    guardar_partido(partido)
                    st.success("🏁 Resultado final fijado")
            else:
                st.info(f"Resultado final: {partido['local']} {partido['resultado_final'][0]} - {partido['resultado_final'][1]} {partido['visitante']}")

elif opcion == "👥 Usuarios":
    st.header("⚽ Usuarios - Registrar predicciones")
    st_autorefresh(interval=600000, key="autorefresh")

    partido = cargar_partido()
    if not partido:
        st.warning("⚠️ Aún no hay partido fijado por el coordinador.")
        st.stop()

    equipo_local = partido["local"]
    equipo_visitante = partido["visitante"]
    fecha = partido["fecha"]

    st.info(f"Partido fijado: **{equipo_local} vs {equipo_visitante}** el {fecha}")

    predicciones = cargar_predicciones()

    if partido["final_fijado"]:
        goles_local_final, goles_visitante_final = partido["resultado_final"]
        st.success(f"Resultado final: {equipo_local} {goles_local_final} - {goles_visitante_final} {equipo_visitante}")

        ganadores = [p["nombre"] for p in predicciones if p["marcador"] == [goles_local_final, goles_visitante_final]]
        if ganadores:
            st.balloons()
            st.subheader("🏆 ¡Ganador(es)!")
            for g in ganadores:
                st.write(f"🎉 {g}")
        guardar_predicciones([])  # Limpiar predicciones después del partido
        st.stop()

    # FORMULARIO NUEVO
    with st.form("form_prediccion"):
        nombre = st.text_input("Nombre del jugador").strip()
        goles_local_pred = st.number_input("Goles equipo local (predicción)", min_value=0, step=1, key="pred_local")
        goles_visitante_pred = st.number_input("Goles equipo visitante (predicción)", min_value=0, step=1, key="pred_vis")
        submit = st.form_submit_button("Guardar predicción")

        if submit:
            if not nombre:
                st.error("Por favor, ingresa tu nombre.")
            else:
                marcador = [goles_local_pred, goles_visitante_pred]
                ya_registrado = any(p["marcador"] == marcador for p in predicciones)
                if ya_registrado:
                    st.error("⚠️ Esa predicción ya existe. Elige otro resultado.")
                else:
                    predicciones.append({
                        "nombre": nombre,
                        "marcador": marcador
                    })
                    guardar_predicciones(predicciones)
                    st.success(f"✅ Predicción registrada para {nombre}")

    # LISTAR PREDICCIONES
    if predicciones:
        st.write("### 📋 Predicciones registradas:")
        for i, p in enumerate(predicciones):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"- {p['nombre']}: {p['marcador'][0]} - {p['marcador'][1]}")
            with col2:
                if st.button("✏️ Editar nombre", key=f"editar_{i}"):
                    with st.form(f"form_edit_{i}"):
                        nuevo_nombre = st.text_input("Editar nombre", value=p["nombre"], key=f"edit_nombre_{i}")
                        actualizar = st.form_submit_button("Actualizar")

                        if actualizar:
                            predicciones[i]["nombre"] = nuevo_nombre
                            guardar_predicciones(predicciones)
                            st.success("✏️ Nombre actualizado correctamente")
                            st.stop()
    else:
        st.info("No hay predicciones aún.")

    # Mostrar marcador en vivo
    goles_local_en_vivo, goles_visitante_en_vivo = partido["marcador_en_vivo"]
    st.info(f"Marcador en vivo: **{equipo_local} {goles_local_en_vivo} - {goles_visitante_en_vivo} {equipo_visitante}**")

    if goles_local_en_vivo > goles_visitante_en_vivo:
        st.info(f"🔵 Está ganando: **{equipo_local}**")
    elif goles_visitante_en_vivo > goles_local_en_vivo:
        st.info(f"🔴 Está ganando: **{equipo_visitante}**")
    else:
        st.info("⚖️ El partido está empatado.")


