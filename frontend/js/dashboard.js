
document.addEventListener(
    "DOMContentLoaded",
    iniciarDashboard
);


// ==========================================
// INICIALIZACIÓN
// ==========================================

async function iniciarDashboard() {
    configurarMenu();
    configurarCerrarSesion();

    // Primero verificamos la sesión.
    try {
        const usuario = await authAPI.obtenerPerfil();

        mostrarUsuario(usuario);

    } catch (error) {
        // Si la sesión no es válida, no mostramos
        // información privada del dashboard.
        window.location.replace("/login.html");
        return;
    }

    // La sesión es válida: cargamos los datos.
    await cargarEstadisticas();
}


// ==========================================
// MOSTRAR INFORMACIÓN DEL USUARIO
// ==========================================

function mostrarUsuario(usuario) {
    const nombreCompleto = [
        usuario.nombre,
        usuario.primer_apellido
    ].filter(Boolean).join(" ");

    document.getElementById(
        "nombreUsuario"
    ).textContent = nombreCompleto;

    document.getElementById(
        "correoUsuario"
    ).textContent = usuario.correo;

    document.getElementById(
        "avatarUsuario"
    ).textContent = usuario.nombre
        ? usuario.nombre.charAt(0).toUpperCase()
        : "U";

    document.getElementById(
        "saludoUsuario"
    ).textContent = `¡Bienvenido, ${usuario.nombre}!`;
}


// ==========================================
// CARGAR ESTADÍSTICAS
// ==========================================

async function cargarEstadisticas() {
    try {
        const [
            restaurantes,
            locales,
            empleados,
            asignaciones
        ] = await Promise.all([
            api.get("/restaurantes"),
            api.get("/locales"),
            api.get("/empleados?activo=true"),
            api.get("/asignaciones?activo=true")
        ]);

        const localesActivos = locales.filter(
            local => local.activo === true
        );

        document.getElementById(
            "totalRestaurantes"
        ).textContent = restaurantes.length;

        document.getElementById(
            "totalLocales"
        ).textContent = localesActivos.length;

        document.getElementById(
            "totalEmpleados"
        ).textContent = empleados.length;

        document.getElementById(
            "totalAsignaciones"
        ).textContent = asignaciones.length;

        mostrarRestaurantes(restaurantes);

    } catch (error) {
        mostrarErrorDashboard(
            "No se pudieron cargar las estadísticas: " +
            error.message
        );
    }
}


// ==========================================
// MOSTRAR RESTAURANTES
// ==========================================

function mostrarRestaurantes(restaurantes) {
    const contenedor = document.getElementById(
        "listaRestaurantes"
    );

    contenedor.replaceChildren();

    if (restaurantes.length === 0) {
        const mensaje = document.createElement("p");

        mensaje.className = "empty-state";
        mensaje.textContent =
            "Todavía no tienes restaurantes registrados.";

        contenedor.appendChild(mensaje);
        return;
    }

    restaurantes.forEach(restaurante => {
        const elemento = document.createElement("article");
        elemento.className = "restaurant-item";

        const informacion = document.createElement("div");

        const nombre = document.createElement("p");
        nombre.className = "restaurant-name";
        nombre.textContent = restaurante.nombre;

        const descripcion = document.createElement("p");
        descripcion.className = "restaurant-description";
        descripcion.textContent =
            restaurante.tipo_comida ||
            restaurante.descripcion ||
            "Restaurante registrado";

        informacion.append(nombre, descripcion);

        const estado = document.createElement("span");

        estado.className = restaurante.activo
            ? "status-badge status-active"
            : "status-badge status-inactive";

        estado.textContent = restaurante.activo
            ? "Activo"
            : "Inactivo";

        elemento.append(informacion, estado);
        contenedor.appendChild(elemento);
    });
}


// ==========================================
// MOSTRAR ERRORES
// ==========================================

function mostrarErrorDashboard(mensaje) {
    const contenedor = document.getElementById(
        "mensajeDashboard"
    );

    contenedor.textContent = mensaje;
    contenedor.className =
        "dashboard-message error";
}


// ==========================================
// CERRAR SESIÓN
// ==========================================

function configurarCerrarSesion() {
    const boton = document.getElementById(
        "btnCerrarSesion"
    );

    boton.addEventListener(
        "click",
        async () => {
            boton.disabled = true;
            boton.textContent = "Cerrando sesión...";

            try {
                await authAPI.logout();

                window.location.replace(
                    "/login.html"
                );

            } catch (error) {
                mostrarErrorDashboard(
                    "No se pudo cerrar sesión: " +
                    error.message
                );

                boton.disabled = false;
                boton.textContent = "Cerrar sesión";
            }
        }
    );
}


// ==========================================
// MENÚ RESPONSIVE
// ==========================================

function configurarMenu() {
    const boton = document.getElementById(
        "btnMenu"
    );

    const sidebar = document.getElementById(
        "sidebar"
    );

    boton.addEventListener("click", () => {
        const abierto = sidebar.classList.toggle(
            "open"
        );

        boton.setAttribute(
            "aria-expanded",
            String(abierto)
        );

        boton.setAttribute(
            "aria-label",
            abierto ? "Cerrar menú" : "Abrir menú"
        );
    });
}
