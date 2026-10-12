
let locales = [];
let restaurantesLocales = [];

document.addEventListener(
    "DOMContentLoaded",
    iniciarLocales
);


// ==========================================
// INICIALIZACIÓN
// ==========================================

async function iniciarLocales() {
    configurarEventosLocales();

    try {
        const usuario = await authAPI.obtenerPerfil();
        mostrarUsuarioLocales(usuario);
    } catch (error) {
        window.location.replace("/login.html");
        return;
    }

    await cargarDatosLocales();
}


// ==========================================
// USUARIO Y NAVEGACIÓN
// ==========================================

function mostrarUsuarioLocales(usuario) {
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


function configurarEventosLocales() {
    document.getElementById(
        "btnNuevoLocal"
    ).addEventListener(
        "click",
        abrirFormularioNuevoLocal
    );

    document.getElementById(
        "btnCancelarFormulario"
    ).addEventListener(
        "click",
        cerrarFormularioLocal
    );

    document.getElementById(
        "formLocal"
    ).addEventListener(
        "submit",
        guardarLocal
    );

    [
        "buscarLocal",
        "filtroRestaurante",
        "filtroEstado"
    ].forEach(id => {
        const elemento = document.getElementById(id);

        elemento.addEventListener(
            id === "buscarLocal" ? "input" : "change",
            mostrarLocales
        );
    });

    document.getElementById(
        "btnCerrarSesion"
    ).addEventListener(
        "click",
        cerrarSesionLocales
    );

    const botonMenu = document.getElementById("btnMenu");
    const sidebar = document.getElementById("sidebar");

    botonMenu.addEventListener("click", () => {
        const abierto = sidebar.classList.toggle("open");

        botonMenu.setAttribute(
            "aria-expanded",
            String(abierto)
        );

        botonMenu.setAttribute(
            "aria-label",
            abierto ? "Cerrar menú" : "Abrir menú"
        );
    });
}


async function cerrarSesionLocales() {
    const boton = document.getElementById(
        "btnCerrarSesion"
    );

    boton.disabled = true;

    try {
        await authAPI.logout();
        window.location.replace("/login.html");
    } catch (error) {
        mostrarMensajeLocales(error.message, "error");
        boton.disabled = false;
    }
}


// ==========================================
// CARGAR RESTAURANTES Y LOCALES
// ==========================================

async function cargarDatosLocales() {
    try {
        const [restaurantes, listaLocales] =
            await Promise.all([
                api.get("/restaurantes"),
                api.get("/locales")
            ]);

        restaurantesLocales = restaurantes;
        locales = listaLocales;

        llenarSelectRestaurantes();
        mostrarLocales();

    } catch (error) {
        mostrarMensajeLocales(
            "No se pudieron cargar los datos: " +
            error.message,
            "error"
        );
    }
}


// ==========================================
// SELECTORES DE RESTAURANTES
// ==========================================

function llenarSelectRestaurantes() {
    const selectorFormulario = document.getElementById(
        "idRestaurante"
    );

    const selectorFiltro = document.getElementById(
        "filtroRestaurante"
    );

    const valorFormulario = selectorFormulario.value;
    const valorFiltro = selectorFiltro.value;

    selectorFormulario.replaceChildren();
    selectorFiltro.replaceChildren();

    const opcionInicial = new Option(
        "Selecciona un restaurante",
        ""
    );

    selectorFormulario.add(opcionInicial);

    selectorFiltro.add(
        new Option("Todos los restaurantes", "todos")
    );

    restaurantesLocales.forEach(restaurante => {
        const nombre = restaurante.activo
            ? restaurante.nombre
            : `${restaurante.nombre} (inactivo)`;

        selectorFormulario.add(
            new Option(
                nombre,
                String(restaurante.id_restaurante)
            )
        );

        selectorFiltro.add(
            new Option(
                nombre,
                String(restaurante.id_restaurante)
            )
        );
    });

    if (Array.from(selectorFormulario.options).some(
        opcion => opcion.value === valorFormulario
    )) {
        selectorFormulario.value = valorFormulario;
    }

    if (Array.from(selectorFiltro.options).some(
        opcion => opcion.value === valorFiltro
    )) {
        selectorFiltro.value = valorFiltro;
    }
}


function obtenerNombreRestaurante(idRestaurante) {
    const restaurante = restaurantesLocales.find(
        r => r.id_restaurante === idRestaurante
    );

    return restaurante
        ? restaurante.nombre
        : "Restaurante no disponible";
}


// ==========================================
// MOSTRAR LOCALES
// ==========================================

function mostrarLocales() {
    const contenedor = document.getElementById(
        "contenedorLocales"
    );

    const busqueda = document.getElementById(
        "buscarLocal"
    ).value.trim().toLowerCase();

    const filtroRestaurante = document.getElementById(
        "filtroRestaurante"
    ).value;

    const filtroEstado = document.getElementById(
        "filtroEstado"
    ).value;

    const filtrados = locales.filter(local => {
        const texto = [
            local.nombre,
            local.provincia,
            local.canton,
            local.distrito,
            local.direccion
        ].filter(Boolean).join(" ").toLowerCase();

        const coincideBusqueda = texto.includes(busqueda);

        const coincideRestaurante =
            filtroRestaurante === "todos" ||
            local.id_restaurante === Number(filtroRestaurante);

        const coincideEstado =
            filtroEstado === "todos" ||
            (filtroEstado === "activos" && local.activo) ||
            (filtroEstado === "inactivos" && !local.activo);

        return coincideBusqueda &&
            coincideRestaurante &&
            coincideEstado;
    });

    document.getElementById(
        "contadorLocales"
    ).textContent = `${filtrados.length} local(es)`;

    contenedor.replaceChildren();

    if (filtrados.length === 0) {
        const mensaje = document.createElement("p");
        mensaje.className = "empty-state";
        mensaje.textContent = "No se encontraron locales.";

        contenedor.appendChild(mensaje);
        return;
    }

    filtrados.forEach(local => {
        const tarjeta = document.createElement("article");
        tarjeta.className = "entity-card";

        const encabezado = document.createElement("div");
        encabezado.className = "entity-card-header";

        const nombre = document.createElement("h4");
        nombre.textContent = local.nombre;

        const estado = document.createElement("span");
        estado.className = local.activo
            ? "status-badge status-active"
            : "status-badge status-inactive";

        estado.textContent = local.activo
            ? "Activo"
            : "Inactivo";

        encabezado.append(nombre, estado);

        const restaurante = document.createElement("p");
        restaurante.textContent =
            "Restaurante: " +
            obtenerNombreRestaurante(local.id_restaurante);

        const ubicacion = document.createElement("p");
        ubicacion.textContent = [
            local.distrito,
            local.canton,
            local.provincia
        ].filter(Boolean).join(", ");

        const direccion = document.createElement("p");
        direccion.textContent =
            "Dirección: " + (local.direccion || "No registrada");

        const capacidad = document.createElement("p");
        capacidad.textContent =
            "Capacidad: " +
            (local.capacidad_clientes ?? "No registrada");

        const horario = document.createElement("p");
        horario.textContent =
            "Horario: " +
            (local.horario_apertura || "Sin definir") +
            " - " +
            (local.horario_cierre || "Sin definir");

        const acciones = document.createElement("div");
        acciones.className = "entity-card-actions";

        const botonEditar = document.createElement("button");
        botonEditar.type = "button";
        botonEditar.className = "btn btn-outline";
        botonEditar.textContent = "Editar";

        botonEditar.addEventListener("click", () => {
            editarLocal(local.id_local);
        });

        const botonEstado = document.createElement("button");
        botonEstado.type = "button";
        botonEstado.className = "btn btn-outline";

        botonEstado.textContent = local.activo
            ? "Desactivar"
            : "Reactivar";

        botonEstado.addEventListener("click", () => {
            cambiarEstadoLocal(local.id_local);
        });

        acciones.append(botonEditar, botonEstado);

        tarjeta.append(
            encabezado,
            restaurante,
            ubicacion,
            direccion,
            capacidad,
            horario,
            acciones
        );

        contenedor.appendChild(tarjeta);
    });
}


// ==========================================
// FORMULARIO NUEVO
// ==========================================

function abrirFormularioNuevoLocal() {
    const formulario = document.getElementById(
        "formLocal"
    );

    formulario.reset();

    document.getElementById("idLocal").value = "";

    document.getElementById(
        "idRestaurante"
    ).disabled = false;

    // Para nuevos locales solo se permiten
    // restaurantes activos.
    const selector = document.getElementById(
        "idRestaurante"
    );

    Array.from(selector.options).forEach(opcion => {
        if (!opcion.value) return;

        const restaurante = restaurantesLocales.find(
            r => r.id_restaurante === Number(opcion.value)
        );

        opcion.disabled = !restaurante?.activo;
    });

    document.getElementById(
        "tituloFormulario"
    ).textContent = "Nuevo local";

    document.getElementById(
        "btnGuardarLocal"
    ).textContent = "Guardar local";

    mostrarFormularioLocal();
}


// ==========================================
// EDITAR LOCAL
// ==========================================

function editarLocal(id) {
    const local = locales.find(
        l => l.id_local === id
    );

    if (!local) return;

    const asignar = (campo, valor) => {
        document.getElementById(campo).value =
            valor ?? "";
    };

    asignar("idLocal", local.id_local);
    asignar("idRestaurante", local.id_restaurante);
    asignar("nombre", local.nombre);
    asignar("provincia", local.provincia);
    asignar("canton", local.canton);
    asignar("distrito", local.distrito);
    asignar("direccion", local.direccion);
    asignar("telefono", local.telefono);
    asignar("correoContacto", local.correo_contacto);
    asignar("capacidadClientes", local.capacidad_clientes);
    asignar("horarioApertura", local.horario_apertura);
    asignar("horarioCierre", local.horario_cierre);
    asignar("imagenUrl", local.imagen_url);
    asignar("descripcion", local.descripcion);

    asignar(
        "fechaApertura",
        local.fecha_apertura
            ? local.fecha_apertura.slice(0, 10)
            : ""
    );

    // No permitimos cambiar el restaurante
    // desde la edición de un local existente.
    document.getElementById(
        "idRestaurante"
    ).disabled = true;

    document.getElementById(
        "tituloFormulario"
    ).textContent = "Editar local";

    document.getElementById(
        "btnGuardarLocal"
    ).textContent = "Guardar cambios";

    mostrarFormularioLocal();
}


// ==========================================
// MOSTRAR / CERRAR FORMULARIO
// ==========================================

function mostrarFormularioLocal() {
    const panel = document.getElementById(
        "panelFormulario"
    );

    panel.hidden = false;

    panel.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


function cerrarFormularioLocal() {
    document.getElementById(
        "panelFormulario"
    ).hidden = true;

    document.getElementById(
        "formLocal"
    ).reset();

    document.getElementById(
        "idRestaurante"
    ).disabled = false;
}


// ==========================================
// GUARDAR LOCAL
// ==========================================

async function guardarLocal(evento) {
    evento.preventDefault();

    const id = document.getElementById(
        "idLocal"
    ).value;

    const obtenerValor = (campo) => {
        const valor = document.getElementById(
            campo
        ).value.trim();

        return valor || null;
    };

    const fechaApertura = obtenerValor("fechaApertura");
    const capacidad = obtenerValor("capacidadClientes");

    const datos = {
        nombre: obtenerValor("nombre"),
        descripcion: obtenerValor("descripcion"),
        provincia: obtenerValor("provincia"),
        canton: obtenerValor("canton"),
        distrito: obtenerValor("distrito"),
        direccion: obtenerValor("direccion"),
        telefono: obtenerValor("telefono"),
        correo_contacto: obtenerValor("correoContacto"),
        horario_apertura: obtenerValor("horarioApertura"),
        horario_cierre: obtenerValor("horarioCierre"),
        capacidad_clientes: capacidad === null
            ? 0
            : Number(capacidad),
        fecha_apertura: fechaApertura
            ? `${fechaApertura}T00:00:00`
            : null,
        imagen_url: obtenerValor("imagenUrl")
    };

    const boton = document.getElementById(
        "btnGuardarLocal"
    );

    boton.disabled = true;

    try {
        if (id) {
            await api.put(
                `/locales/${id}`,
                datos
            );

            mostrarMensajeLocales(
                "Local actualizado correctamente.",
                "success"
            );
        } else {
            datos.id_restaurante = Number(
                document.getElementById(
                    "idRestaurante"
                ).value
            );

            await api.post("/locales", datos);

            mostrarMensajeLocales(
                "Local registrado correctamente.",
                "success"
            );
        }

        cerrarFormularioLocal();
        await cargarDatosLocales();

    } catch (error) {
        mostrarMensajeLocales(
            "No se pudo guardar el local: " +
            error.message,
            "error"
        );

    } finally {
        boton.disabled = false;
    }
}


// ==========================================
// DESACTIVAR / REACTIVAR LOCAL
// ==========================================

async function cambiarEstadoLocal(id) {
    const local = locales.find(
        l => l.id_local === id
    );

    if (!local) return;

    const nuevoEstado = !local.activo;

    const accion = nuevoEstado
        ? "reactivar"
        : "desactivar";

    const confirmado = window.confirm(
        `¿Deseas ${accion} el local "${local.nombre}"?`
    );

    if (!confirmado) return;

    try {
        await api.put(
            `/locales/${id}`,
            { activo: nuevoEstado }
        );

        mostrarMensajeLocales(
            `Local ${nuevoEstado
                ? "reactivado"
                : "desactivado"} correctamente.`,
            "success"
        );

        await cargarDatosLocales();

    } catch (error) {
        mostrarMensajeLocales(
            "No se pudo cambiar el estado: " +
            error.message,
            "error"
        );
    }
}


// ==========================================
// MENSAJES
// ==========================================

function mostrarMensajeLocales(
    mensaje,
    tipo = "error"
) {
    const contenedor = document.getElementById(
        "mensajeLocales"
    );

    contenedor.textContent = mensaje;
    contenedor.className = `module-message ${tipo}`;

    contenedor.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });
}
