
document.addEventListener(
    "DOMContentLoaded",
    () => {
        configurarLogin();
        configurarRegistro();
    }
);


// ==========================================
// MOSTRAR MENSAJES
// ==========================================

function mostrarMensaje(mensaje, tipo = "error") {
    const contenedor = document.getElementById(
        "mensajeAuth"
    );

    if (!contenedor) return;

    contenedor.textContent = mensaje;
    contenedor.className = `auth-message ${tipo}`;
}


// ==========================================
// INICIO DE SESIÓN
// ==========================================

function configurarLogin() {
    const formulario = document.getElementById(
        "formLogin"
    );

    if (!formulario) return;

    formulario.addEventListener(
        "submit",
        async (evento) => {
            evento.preventDefault();

            const boton = formulario.querySelector(
                'button[type="submit"]'
            );

            const datos = {
                correo: document.getElementById(
                    "correo"
                ).value.trim(),

                clave: document.getElementById(
                    "clave"
                ).value
            };

            boton.disabled = true;
            boton.textContent = "Iniciando sesión...";

            try {
                await authAPI.login(datos);

                mostrarMensaje(
                    "Inicio de sesión exitoso.",
                    "success"
                );

                window.location.replace(
                    "/dashboard.html"
                );

            } catch (error) {
                mostrarMensaje(error.message);

            } finally {
                boton.disabled = false;
                boton.textContent = "Iniciar sesión";
            }
        }
    );
}


// ==========================================
// REGISTRO DE USUARIOS
// ==========================================

function configurarRegistro() {
    const formulario = document.getElementById(
        "formRegistro"
    );

    if (!formulario) return;

    formulario.addEventListener(
        "submit",
        async (evento) => {
            evento.preventDefault();

            const clave = document.getElementById(
                "clave"
            ).value;

            const confirmarClave = document.getElementById(
                "confirmarClave"
            ).value;

            if (clave !== confirmarClave) {
                mostrarMensaje(
                    "Las contraseñas no coinciden."
                );
                return;
            }

            const fechaNacimiento =
                document.getElementById(
                    "fechaNacimiento"
                ).value;

            const datos = {
                nombre: document.getElementById(
                    "nombre"
                ).value.trim(),

                primer_apellido: document.getElementById(
                    "primerApellido"
                ).value.trim(),

                segundo_apellido:
                    document.getElementById(
                        "segundoApellido"
                    ).value.trim() || null,

                correo: document.getElementById(
                    "correo"
                ).value.trim(),

                telefono: document.getElementById(
                    "telefono"
                ).value.trim() || null,

                fecha_nacimiento: fechaNacimiento
                    ? `${fechaNacimiento}T00:00:00`
                    : null,

                clave
            };

            const boton = formulario.querySelector(
                'button[type="submit"]'
            );

            boton.disabled = true;
            boton.textContent = "Creando cuenta...";

            try {
                await authAPI.registrar(datos);

                mostrarMensaje(
                    "Cuenta creada correctamente. Redirigiendo...",
                    "success"
                );

                window.location.replace(
                    "/login.html?registro=exitoso"
                );

            } catch (error) {
                mostrarMensaje(error.message);

            } finally {
                boton.disabled = false;
                boton.textContent = "Crear cuenta";
            }
        }
    );
}
