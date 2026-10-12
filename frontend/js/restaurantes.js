
let restaurantes = [];

document.addEventListener(
    "DOMContentLoaded",
    iniciarRestaurantes
);


// ==========================================
// INICIALIZACIÓN
// ==========================================

async function iniciarRestaurantes() {
    configurarEventos();

    try {
        const usuario = await authAPI.obtenerPerfil();
        mostrarUsuario(usuario);

    } catch (error) {
        window.location.replace("/login.html");
        return;
    }

    await cargarRestaurantes();
}


// ==========================================
// USUARIO Y NAVEGACIÓN
// ==========================================

function mostrarUsuario(usuario) {
    document.getElementById(
        "nombreUsuario"
    ).textContent = [
        usuario.nombre,
        usuario.primer_apellido
    ].filter(Boolean).join(" ");

    document.getElementById(
        "correoUsuario"
    ).textContent = usuario.correo;

    document.getElementById(
        "avatarUsuario"
    ).textContent = usuario.nombre
        ? usuario.nombre.charAt(0).toUpperCase()
        : "U";
}


function configurarEventos() {
    document.getElementById(
        "btnNuevoRestaurante"
    ).addEventListener(
        "click",
        abrirFormularioNuevo
    );

    document.getElementById(
        "btnCancelarFormulario"
    ).addEventListener(
        "click",
        cerrarFormulario
    );

    document.getElementById(
        "formRestaurante"
    ).addEventListener(
        "submit",
        guardarRestaurante
    );

    document.getElementById(
        "buscarRestaurante"
    ).addEventListener(
        "input",
        mostrarRestaurantes
    );

    document.getElementById(
        "filtroEstado"
    ).addEventListener(
        "change",
        mostrarRestaurantes
    );

    document.getElementById(
        "btnCerrarSesion"
    ).addEventListener(
        "click",
        cerrarSesion
    );

    const botonMenu = document.getElementById("btnMenu");
    const sidebar = document.getElementById("sidebar");

    botonMenu.addEventListener("click", () => {
        const abierto = sidebar.classList.toggle("open");

        botonMenu.setAttribute(
            "aria-expanded",
            String(abierto)
        );
    });
}


async function cerrarSesion() {
    const boton = document.getElementById(
        "btnCerrarSesion"
    );

    boton.disabled = true;

    try {
        await authAPI.logout();
        window.location.replace("/login.html");

    } catch (error) {
        mostrarMensaje(error.message, "error");
        boton.disabled = false;
    }
}


// ==========================================
// CONSULTAR RESTAURANTES
// ==========================================

async function cargarRestaurantes() {
    try {
        restaurantes = await api.get("/restaurantes");
        mostrarRestaurantes();

    } catch (error) {
        mostrarMensaje(
            "No se pudieron cargar los restaurantes: " +
            error.message,
            "error"
        );
    }
}


// ==========================================
// RENDERIZAR RESTAURANTES
// ==========================================

function mostrarRestaurantes() {
    const contenedor = document.getElementById(
        "contenedorRestaurantes"
    );

    const busqueda = document.getElementById(
        "buscarRestaurante"
    ).value.trim().toLowerCase();

    const estado = document.getElementById(
        "filtroEstado"
    ).value;

    const filtrados = restaurantes.filter(
        restaurante => {
            const coincideNombre =
                restaurante.nombre
                    .toLowerCase()
                    .includes(busqueda);

            const coincideEstado =
                estado === "todos" ||
                (
                    estado === "activos" &&
                    restaurante.activo
                ) ||
                (
                    estado === "inactivos" &&
                    !restaurante.activo
                );

            return coincideNombre && coincideEstado;
        }
    );

    document.getElementById(
        "contadorRestaurantes"
    ).textContent =
        `${filtrados.length} restaurante(s)`;

    contenedor.replaceChildren();

    if (filtrados.length === 0) {
        const mensaje = document.createElement("p");

        mensaje.className = "empty-state";
        mensaje.textContent =
            "No se encontraron restaurantes.";

        contenedor.appendChild(mensaje);
        return;
    }

    filtrados.forEach(restaurante => {
        const tarjeta = document.createElement("article");
        tarjeta.className = "entity-card";

        const encabezado = document.createElement("div");
        encabezado.className = "entity-card-header";

        const nombre = document.createElement("h4");
        nombre.textContent = restaurante.nombre;

        const estado = document.createElement("span");
        estado.className = restaurante.activo
            ? "status-badge status-active"
            : "status-badge status-inactive";

        estado.textContent = restaurante.activo
            ? "Activo"
            : "Inactivo";

        encabezado.append(nombre, estado);

        const tipoComida = document.createElement("p");
        tipoComida.textContent =
            restaurante.tipo_comida ||
            "Tipo de comida no especificado";

        const descripcion = document.createElement("p");
        descripcion.textContent =
            restaurante.descripcion ||
            "Sin descripción";

        const telefono = document.createElement("p");
        telefono.textContent =
            "Teléfono: " +
            (restaurante.telefono || "No registrado");

        const acciones = document.createElement("div");
        acciones.className = "entity-card-actions";

        const btnEditar = document.createElement("button");
        btnEditar.type = "button";
        btnEditar.className = "btn btn-outline";
        btnEditar.textContent = "Editar";

        btnEditar.addEventListener("click", () => {
            editarRestaurante(restaurante.id_restaurante);
        });

        const btnEstado = document.createElement("button");
        btnEstado.type = "button";
        btnEstado.className = "btn btn-outline";

        btnEstado.textContent = restaurante.activo
            ? "Desactivar"
            : "Reactivar";

        btnEstado.addEventListener("click", () => {
            cambiarEstadoRestaurante(
                restaurante.id_restaurante
            );
        });

        acciones.append(btnEditar, btnEstado);

        tarjeta.append(
            encabezado,
            tipoComida,
            descripcion,
            telefono,
            acciones
        );

        contenedor.appendChild(tarjeta);
    });
}


// ==========================================
// ABRIR FORMULARIO NUEVO
// ==========================================

function abrirFormularioNuevo() {
    const formulario = document.getElementById(
        "formRestaurante"
    );

    formulario.reset();

    document.getElementById(
        "idRestaurante"
    ).value = "";

    document.getElementById(
        "tituloFormulario"
    ).textContent = "Nuevo restaurante";

    document.getElementById(
        "btnGuardarRestaurante"
    ).textContent = "Guardar restaurante";

    mostrarFormulario();
}


// ==========================================
// EDITAR RESTAURANTE
// ==========================================

function editarRestaurante(id) {
    const restaurante = restaurantes.find(
        r => r.id_restaurante === id
    );

    if (!restaurante) return;

    document.getElementById(
        "idRestaurante"
    ).value = restaurante.id_restaurante;

    document.getElementById(
        "nombre"
    ).value = restaurante.nombre || "";

    document.getElementById(
        "tipoComida"
    ).value = restaurante.tipo_comida || "";

    document.getElementById(
        "cedulaJuridica"
    ).value = restaurante.cedula_juridica || "";

    document.getElementById(
        "telefono"
    ).value = restaurante.telefono || "";

    document.getElementById(
        "correoContacto"
    ).value = restaurante.correo_contacto || "";

    document.getElementById(
        "sitioWeb"
    ).value = restaurante.sitio_web || "";

    document.getElementById(
        "logoUrl"
    ).value = restaurante.logo_url || "";

    document.getElementById(
        "fechaFundacion"
    ).value = restaurante.fecha_fundacion
        ? restaurante.fecha_fundacion.slice(0, 10)
        : "";

    document.getElementById(
        "descripcion"
    ).value = restaurante.descripcion || "";

    document.getElementById(
        "tituloFormulario"
    ).textContent = "Editar restaurante";

    document.getElementById(
        "btnGuardarRestaurante"
    ).textContent = "Guardar cambios";

    mostrarFormulario();
}


// ==========================================
// MOSTRAR / CERRAR FORMULARIO
// ==========================================

function mostrarFormulario() {
    const panel = document.getElementById(
        "panelFormulario"
    );

    panel.hidden = false;

    panel.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


function cerrarFormulario() {
    document.getElementById(
        "panelFormulario"
    ).hidden = true;

    document.getElementById(
        "formRestaurante"
    ).reset();
}


// ==========================================
// GUARDAR RESTAURANTE
// ==========================================

async function guardarRestaurante(evento) {
    evento.preventDefault();

    const id = document.getElementById(
        "idRestaurante"
    ).value;

    const obtenerValor = (idCampo) => {
        const valor = document.getElementById(
            idCampo
        ).value.trim();

        return valor || null;
    };

    const fechaFundacion = obtenerValor(
        "fechaFundacion"
    );

    const datos = {
        nombre: obtenerValor("nombre"),
        tipo_comida: obtenerValor("tipoComida"),
        cedula_juridica: obtenerValor("cedulaJuridica"),
        telefono: obtenerValor("telefono"),
        correo_contacto: obtenerValor("correoContacto"),
        sitio_web: obtenerValor("sitioWeb"),
        logo_url: obtenerValor("logoUrl"),
        fecha_fundacion: fechaFundacion
            ? `${fechaFundacion}T00:00:00`
            : null,
        descripcion: obtenerValor("descripcion")
    };

    const boton = document.getElementById(
        "btnGuardarRestaurante"
    );

    boton.disabled = true;

    try {
        if (id) {
            await api.put(
                `/restaurantes/${id}`,
                datos
            );

            mostrarMensaje(
                "Restaurante actualizado correctamente.",
                "success"
            );

        } else {
            await api.post(
                "/restaurantes",
                datos
            );

            mostrarMensaje(
                "Restaurante registrado correctamente.",
                "success"
            );
        }

        cerrarFormulario();
        await cargarRestaurantes();

    } catch (error) {
        mostrarMensaje(error.message, "error");

    } finally {
        boton.disabled = false;
    }
}


// ==========================================
// DESACTIVAR / REACTIVAR
// ==========================================

async function cambiarEstadoRestaurante(id) {
    const restaurante = restaurantes.find(
        r => r.id_restaurante === id
    );

    if (!restaurante) return;

    const nuevoEstado = !restaurante.activo;

    const accion = nuevoEstado
        ? "reactivar"
        : "desactivar";

    const confirmado = window.confirm(
        `¿Deseas ${accion} el restaurante ` +
        `"${restaurante.nombre}"?`
    );

    if (!confirmado) return;

    try {
        await api.put(
            `/restaurantes/${id}`,
            { activo: nuevoEstado }
        );

        mostrarMensaje(
            `Restaurante ${nuevoEstado
                ? "reactivado"
                : "desactivado"} correctamente.`,
            "success"
        );

        await cargarRestaurantes();

    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}


// ==========================================
// MENSAJES
// ==========================================

function mostrarMensaje(mensaje, tipo = "error") {
    const contenedor = document.getElementById(
        "mensajeRestaurantes"
    );

    contenedor.textContent = mensaje;
    contenedor.className = `module-message ${tipo}`;

    contenedor.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });
}
