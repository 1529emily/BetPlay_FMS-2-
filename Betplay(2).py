import streamlit as st
from datetime import date
from streamlit_autorefresh import st_autorefresh

# Variables coordinador
USUARIO_COORDINADOR = "admin"
CONTRASENA_COORDINADOR = "1234"

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
                st.session_state.partido_fijado = {
                    "fecha": fecha.strftime("%Y-%m-%d"),
                    "local": equipo_local.strip(),
                    "visitante": equipo_visitante.strip(),
                    "marcador_en_vivo": (0, 0),
                    "resultado_final": None,
                    "final_fijado": False,
                }
                st.success(f"🎯 Partido fijado: {equipo_local} vs {equipo_visitante} el {fecha.strftime('%Y-%m-%d')}")
            else:
                st.error("⚠️ Debes ingresar los nombres de ambos equipos.")

        if "partido_fijado" in st.session_state:
            st.markdown("---")
            st.subheader("✏️ Actualizar marcador en vivo")

            goles_local_en_vivo = st.number_input("Goles equipo local (en vivo)", min_value=0, step=1, 
                                                 value=st.session_state.partido_fijado["marcador_en_vivo"][0])
            goles_visitante_en_vivo = st.number_input("Goles equipo visitante (en vivo)", min_value=0, step=1, 
                                                     value=st.session_state.partido_fijado["marcador_en_vivo"][1])

            if st.button("Actualizar marcador en vivo"):
                st.session_state.partido_fijado["marcador_en_vivo"] = (goles_local_en_vivo, goles_visitante_en_vivo)
                st.success("✅ Marcador en vivo actualizado")

            st.markdown("---")
            st.subheader("📢 Fijar resultado final")

            if not st.session_state.partido_fijado["final_fijado"]:
                goles_local_final = st.number_input("Goles equipo local (final)", min_value=0, step=1)
                goles_visitante_final = st.number_input("Goles equipo visitante (final)", min_value=0, step=1)

                if st.button("Fijar resultado final"):
                    st.session_state.partido_fijado["resultado_final"] = (goles_local_final, goles_visitante_final)
                    st.session_state.partido_fijado["final_fijado"] = True
                    st.success("🏁 Resultado final fijado")
            else:
                st.info(f"Resultado final: {st.session_state.partido_fijado['local']} {st.session_state.partido_fijado['resultado_final'][0]} - {st.session_state.partido_fijado['resultado_final'][1]} {st.session_state.partido_fijado['visitante']}")

elif opcion == "👥 Usuarios":
    st.header("⚽ Usuarios - Registrar predicciones")
    st_autorefresh(interval=600000, key="autorefresh")

    if "partido_fijado" not in st.session_state:
        st.warning("⚠️ Aún no hay partido fijado por el coordinador.")
        st.stop()

    partido = st.session_state.partido_fijado
    equipo_local = partido["local"]
    equipo_visitante = partido["visitante"]
    fecha = partido["fecha"]

    st.info(f"Partido fijado: **{equipo_local} vs {equipo_visitante}** el {fecha}")

    if "predicciones" not in st.session_state:
        st.session_state.predicciones = []

    with st.form("form_prediccion"):
        nombre = st.text_input("Nombre del jugador").strip()
        goles_local_pred = st.number_input("Goles equipo local (predicción)", min_value=0, step=1)
        goles_visitante_pred = st.number_input("Goles equipo visitante (predicción)", min_value=0, step=1)
        submit = st.form_submit_button("Guardar predicción")

        if submit:
            if not nombre:
                st.error("Por favor, ingresa tu nombre.")
            else:
                marcador = (goles_local_pred, goles_visitante_pred)
                ya_registrado = any(p["marcador"] == marcador for p in st.session_state.predicciones)
                if ya_registrado:
                    st.error("⚠️ Esa predicción ya existe. Elige otro resultado.")
                else:
                    st.session_state.predicciones.append({
                        "nombre": nombre,
                        "marcador": marcador
                    })
                    st.success(f"✅ Predicción registrada para {nombre}")

    if st.session_state.predicciones:
        st.write("### 📋 Predicciones registradas:")
        for p in st.session_state.predicciones:
            st.write(f"- {p['nombre']}: {p['marcador'][0]} - {p['marcador'][1]}")
    else:
        st.info("No hay predicciones aún.")

    # Mostrar marcador en vivo y líder actual
    goles_local_en_vivo, goles_visitante_en_vivo = partido["marcador_en_vivo"]
    st.info(f"Marcador en vivo: **{equipo_local} {goles_local_en_vivo} - {goles_visitante_en_vivo} {equipo_visitante}**")

    if goles_local_en_vivo > goles_visitante_en_vivo:
        st.info(f"🔵 Está ganando: **{equipo_local}**")
    elif goles_visitante_en_vivo > goles_local_en_vivo:
        st.info(f"🔴 Está ganando: **{equipo_visitante}**")
    else:
        st.info("⚖️ El partido está empatado.")

    # Mostrar resultado final y ganadores sólo si ya fue fijado
    if partido["final_fijado"]:
        goles_local_final, goles_visitante_final = partido["resultado_final"]
        st.success(f"Resultado final: {equipo_local} {goles_local_final} - {goles_visitante_final} {equipo_visitante}")

        ganadores = [p["nombre"] for p in st.session_state.predicciones if p["marcador"] == partido["resultado_final"]]
        if ganadores:
            st.balloons()
            st.subheader("🏆 ¡Ganador(es)!")
            for g in ganadores:
                st.write(f"🎉 {g}")

