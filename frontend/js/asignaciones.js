
let asignaciones = [];
let restaurantesAsignaciones = [];
let localesAsignaciones = [];
let empleadosAsignaciones = [];

document.addEventListener(
    "DOMContentLoaded",
    iniciarAsignaciones
);


// ==========================================
// INICIALIZACIÓN
// ==========================================

async function iniciarAsignaciones() {
    configurarEventosAsignaciones();

    try {
        const usuario = await authAPI.obtenerPerfil();
        mostrarUsuarioAsignaciones(usuario);
    } catch (error) {
        window.location.replace("/login.html");
        return;
    }

    await cargarDatosAsignaciones();
}


// ==========================================
// USUARIO Y NAVEGACIÓN
// ==========================================

function mostrarUsuarioAsignaciones(usuario) {
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


function configurarEventosAsignaciones() {
    document.getElementById(
        "btnNuevaAsignacion"
    ).addEventListener(
        "click",
        abrirNuevaAsignacion
    );

    document.getElementById(
        "btnCancelarFormulario"
    ).addEventListener(
        "click",
        cerrarFormularioAsignacion
    );

    document.getElementById(
        "formAsignacion"
    ).addEventListener(
        "submit",
        guardarAsignacion
    );

    document.getElementById(
        "idRestaurante"
    ).addEventListener(
        "change",
        actualizarSelectoresFormulario
    );

    document.getElementById(
        "filtroRestaurante"
    ).addEventListener("change", () => {
        llenarFiltroLocales();
        mostrarAsignaciones();
    });

    [
        "filtroLocal",
        "filtroEstado"
    ].forEach(id => {
        document.getElementById(id)
            .addEventListener(
                "change",
                mostrarAsignaciones
            );
    });

    document.getElementById(
        "buscarEmpleado"
    ).addEventListener(
        "input",
        mostrarAsignaciones
    );

    document.getElementById(
        "btnCerrarSesion"
    ).addEventListener(
        "click",
        cerrarSesionAsignaciones
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


async function cerrarSesionAsignaciones() {
    const boton = document.getElementById(
        "btnCerrarSesion"
    );

    boton.disabled = true;

    try {
        await authAPI.logout();
        window.location.replace("/login.html");
    } catch (error) {
        mostrarMensajeAsignaciones(
            error.message,
            "error"
        );
        boton.disabled = false;
    }
}


// ==========================================
// CARGAR DATOS
// ==========================================

async function cargarDatosAsignaciones() {
    try {
        const [
            restaurantes,
            locales,
            empleados,
            listaAsignaciones
        ] = await Promise.all([
            api.get("/restaurantes"),
            api.get("/locales"),
            api.get("/empleados?incluir_todos=true"),
            api.get("/asignaciones")
        ]);

        restaurantesAsignaciones = restaurantes;
        localesAsignaciones = locales;
        empleadosAsignaciones = empleados;
        asignaciones = listaAsignaciones;

        llenarFiltroRestaurantes();
        llenarFiltroLocales();
        llenarRestaurantesFormulario();

        actualizarEstadisticasAsignaciones();
        mostrarAsignaciones();

    } catch (error) {
        mostrarMensajeAsignaciones(
            "No se pudieron cargar los datos: " +
            error.message,
            "error"
        );
    }
}


// ==========================================
// FUNCIONES AUXILIARES
// ==========================================

function obtenerRestauranteAsignacion(id) {
    return restaurantesAsignaciones.find(
        r => r.id_restaurante === Number(id)
    );
}


function obtenerLocalAsignacion(id) {
    return localesAsignaciones.find(
        l => l.id_local === Number(id)
    );
}


function obtenerEmpleadoAsignacion(id) {
    return empleadosAsignaciones.find(
        e => e.id_empleado === Number(id)
    );
}


function nombreEmpleadoAsignacion(empleado) {
    if (!empleado) {
        return "Empleado no disponible";
    }

    return [
        empleado.nombre,
        empleado.primer_apellido,
        empleado.segundo_apellido
    ].filter(Boolean).join(" ");
}


function formatearFechaAsignacion(valor) {
    if (!valor) return "No registrada";

    const fecha = new Date(valor);

    if (Number.isNaN(fecha.getTime())) {
        return String(valor);
    }

    return new Intl.DateTimeFormat("es-CR", {
        dateStyle: "medium",
        timeStyle: "short"
    }).format(fecha);
}


function crearParrafoAsignacion(etiqueta, valor) {
    const parrafo = document.createElement("p");
    parrafo.textContent = `${etiqueta}: ${valor}`;
    return parrafo;
}


// ==========================================
// FILTROS
// ==========================================

function llenarFiltroRestaurantes() {
    const selector = document.getElementById(
        "filtroRestaurante"
    );

    const anterior = selector.value;

    selector.replaceChildren();
    selector.add(
        new Option("Todos los restaurantes", "todos")
    );

    restaurantesAsignaciones.forEach(restaurante => {
        selector.add(
            new Option(
                restaurante.nombre,
                String(restaurante.id_restaurante)
            )
        );
    });

    if (Array.from(selector.options).some(
        opcion => opcion.value === anterior
    )) {
        selector.value = anterior;
    }
}


function llenarFiltroLocales() {
    const selector = document.getElementById(
        "filtroLocal"
    );

    const restaurante = document.getElementById(
        "filtroRestaurante"
    ).value;

    const anterior = selector.value;

    selector.replaceChildren();
    selector.add(new Option("Todos los locales", "todos"));

    localesAsignaciones
        .filter(local =>
            restaurante === "todos" ||
            local.id_restaurante === Number(restaurante)
        )
        .forEach(local => {
            selector.add(
                new Option(
                    local.nombre,
                    String(local.id_local)
                )
            );
        });

    if (Array.from(selector.options).some(
        opcion => opcion.value === anterior
    )) {
        selector.value = anterior;
    }
}


// ==========================================
// ESTADÍSTICAS
// ==========================================

function actualizarEstadisticasAsignaciones() {
    const activas = asignaciones.filter(
        asignacion => asignacion.activo === true
    ).length;

    const finalizadas = asignaciones.filter(
        asignacion => asignacion.activo === false
    ).length;

    document.getElementById(
        "totalAsignaciones"
    ).textContent = asignaciones.length;

    document.getElementById(
        "asignacionesActivas"
    ).textContent = activas;

    document.getElementById(
        "asignacionesFinalizadas"
    ).textContent = finalizadas;
}


// ==========================================
// MOSTRAR ASIGNACIONES
// ==========================================

function mostrarAsignaciones() {
    const contenedor = document.getElementById(
        "contenedorAsignaciones"
    );

    const restauranteFiltro = document.getElementById(
        "filtroRestaurante"
    ).value;

    const localFiltro = document.getElementById(
        "filtroLocal"
    ).value;

    const estadoFiltro = document.getElementById(
        "filtroEstado"
    ).value;

    const busqueda = document.getElementById(
        "buscarEmpleado"
    ).value.trim().toLowerCase();

    const filtradas = asignaciones.filter(asignacion => {
        const empleado = obtenerEmpleadoAsignacion(
            asignacion.id_empleado
        );

        const nombre = nombreEmpleadoAsignacion(
            empleado
        ).toLowerCase();

        const coincideBusqueda = nombre.includes(busqueda);

        const coincideRestaurante =
            restauranteFiltro === "todos" ||
            asignacion.id_restaurante ===
                Number(restauranteFiltro);

        const coincideLocal =
            localFiltro === "todos" ||
            asignacion.id_local === Number(localFiltro);

        const coincideEstado =
            estadoFiltro === "todos" ||
            (
                estadoFiltro === "activas" &&
                asignacion.activo === true
            ) ||
            (
                estadoFiltro === "finalizadas" &&
                asignacion.activo === false
            );

        return coincideBusqueda &&
            coincideRestaurante &&
            coincideLocal &&
            coincideEstado;
    });

    document.getElementById(
        "contadorAsignaciones"
    ).textContent =
        `${filtradas.length} asignación(es)`;

    contenedor.replaceChildren();

    if (filtradas.length === 0) {
        const mensaje = document.createElement("p");
        mensaje.className = "empty-state";
        mensaje.textContent =
            "No se encontraron asignaciones.";

        contenedor.appendChild(mensaje);
        return;
    }

    filtradas.forEach(asignacion => {
        const restaurante = obtenerRestauranteAsignacion(
            asignacion.id_restaurante
        );

        const local = obtenerLocalAsignacion(
            asignacion.id_local
        );

        const empleado = obtenerEmpleadoAsignacion(
            asignacion.id_empleado
        );

        const tarjeta = document.createElement("article");
        tarjeta.className = "entity-card";

        const encabezado = document.createElement("div");
        encabezado.className = "entity-card-header";

        const nombre = document.createElement("h4");
        nombre.textContent = nombreEmpleadoAsignacion(
            empleado
        );

        const estado = document.createElement("span");
        estado.className = asignacion.activo
            ? "status-badge status-active"
            : "status-badge status-inactive";

        estado.textContent = asignacion.activo
            ? "Vigente"
            : "Finalizada";

        encabezado.append(nombre, estado);

        const datos = [
            crearParrafoAsignacion(
                "Restaurante",
                restaurante?.nombre || "No disponible"
            ),
            crearParrafoAsignacion(
                "Local",
                local?.nombre || "No disponible"
            ),
            crearParrafoAsignacion(
                "Turno",
                asignacion.turno || "No definido"
            ),
            crearParrafoAsignacion(
                "Inicio",
                formatearFechaAsignacion(
                    asignacion.fecha_asignacion
                )
            )
        ];

        if (!asignacion.activo) {
            datos.push(
                crearParrafoAsignacion(
                    "Finalización",
                    formatearFechaAsignacion(
                        asignacion.fecha_finalizacion
                    )
                )
            );
        }

        if (asignacion.observaciones) {
            datos.push(
                crearParrafoAsignacion(
                    "Observaciones",
                    asignacion.observaciones
                )
            );
        }

        tarjeta.append(encabezado, ...datos);

        if (asignacion.activo) {
            const acciones = document.createElement("div");
            acciones.className = "entity-card-actions";

            const botonEditar = document.createElement(
                "button"
            );
            botonEditar.type = "button";
            botonEditar.className = "btn btn-outline";
            botonEditar.textContent = "Editar";

            botonEditar.addEventListener("click", () => {
                editarAsignacion(
                    asignacion.id_asignacion
                );
            });

            const botonFinalizar = document.createElement(
                "button"
            );
            botonFinalizar.type = "button";
            botonFinalizar.className = "btn btn-outline";
            botonFinalizar.textContent = "Finalizar";

            botonFinalizar.addEventListener("click", () => {
                finalizarAsignacion(
                    asignacion.id_asignacion
                );
            });

            acciones.append(botonEditar, botonFinalizar);
            tarjeta.appendChild(acciones);
        }

        contenedor.appendChild(tarjeta);
    });
}


// ==========================================
// SELECTORES DEL FORMULARIO
// ==========================================

function llenarRestaurantesFormulario() {
    const selector = document.getElementById(
        "idRestaurante"
    );

    selector.replaceChildren();

    selector.add(
        new Option("Selecciona un restaurante", "")
    );

    restaurantesAsignaciones
        .filter(restaurante => restaurante.activo)
        .forEach(restaurante => {
            selector.add(
                new Option(
                    restaurante.nombre,
                    String(restaurante.id_restaurante)
                )
            );
        });

    actualizarSelectoresFormulario();
}


function actualizarSelectoresFormulario() {
    const idRestaurante = Number(
        document.getElementById("idRestaurante").value
    );

    const selectorLocal = document.getElementById(
        "idLocal"
    );

    const selectorEmpleado = document.getElementById(
        "idEmpleado"
    );

    selectorLocal.replaceChildren();
    selectorEmpleado.replaceChildren();

    selectorLocal.add(
        new Option("Selecciona un local", "")
    );

    selectorEmpleado.add(
        new Option("Selecciona un empleado", "")
    );

    if (!idRestaurante) return;

    localesAsignaciones
        .filter(local =>
            local.id_restaurante === idRestaurante &&
            local.activo === true
        )
        .forEach(local => {
            selectorLocal.add(
                new Option(
                    local.nombre,
                    String(local.id_local)
                )
            );
        });

    empleadosAsignaciones
        .filter(empleado =>
            empleado.id_restaurante === idRestaurante &&
            empleado.activo === true
        )
        .forEach(empleado => {
            selectorEmpleado.add(
                new Option(
                    nombreEmpleadoAsignacion(empleado),
                    String(empleado.id_empleado)
                )
            );
        });
}


// ==========================================
// NUEVA ASIGNACIÓN
// ==========================================

function abrirNuevaAsignacion() {
    document.getElementById(
        "formAsignacion"
    ).reset();

    document.getElementById(
        "idAsignacion"
    ).value = "";

    [
        "idRestaurante",
        "idLocal",
        "idEmpleado",
        "fechaAsignacion"
    ].forEach(id => {
        document.getElementById(id).disabled = false;
    });

    actualizarSelectoresFormulario();

    document.getElementById(
        "tituloFormulario"
    ).textContent = "Nueva asignación";

    document.getElementById(
        "btnGuardarAsignacion"
    ).textContent = "Guardar asignación";

    mostrarFormularioAsignacion();
}


// ==========================================
// EDITAR ASIGNACIÓN
// ==========================================

function editarAsignacion(id) {
    const asignacion = asignaciones.find(
        a => a.id_asignacion === id
    );

    if (!asignacion || !asignacion.activo) return;

    document.getElementById(
        "idAsignacion"
    ).value = asignacion.id_asignacion;

    // Los campos de relaciones se muestran
    // como referencia, pero no son editables.
    const restaurante = document.getElementById(
        "idRestaurante"
    );

    const local = document.getElementById("idLocal");
    const empleado = document.getElementById("idEmpleado");

    // Reconstruimos los selectores para incluir
    // la relación actual, incluso si alguna
    // entidad fue desactivada posteriormente.
    restaurante.replaceChildren();
    restaurante.add(
        new Option(
            obtenerRestauranteAsignacion(
                asignacion.id_restaurante
            )?.nombre || "Restaurante",
            String(asignacion.id_restaurante)
        )
    );

    local.replaceChildren();
    local.add(
        new Option(
            obtenerLocalAsignacion(
                asignacion.id_local
            )?.nombre || "Local",
            String(asignacion.id_local)
        )
    );

    empleado.replaceChildren();
    empleado.add(
        new Option(
            nombreEmpleadoAsignacion(
                obtenerEmpleadoAsignacion(
                    asignacion.id_empleado
                )
            ),
            String(asignacion.id_empleado)
        )
    );

    restaurante.disabled = true;
    local.disabled = true;
    empleado.disabled = true;

    const fecha = document.getElementById(
        "fechaAsignacion"
    );

    fecha.value = asignacion.fecha_asignacion
        ? asignacion.fecha_asignacion.slice(0, 16)
        : "";

    fecha.disabled = true;

    document.getElementById(
        "turno"
    ).value = asignacion.turno || "";

    document.getElementById(
        "observaciones"
    ).value = asignacion.observaciones || "";

    document.getElementById(
        "tituloFormulario"
    ).textContent = "Editar asignación";

    document.getElementById(
        "btnGuardarAsignacion"
    ).textContent = "Guardar cambios";

    mostrarFormularioAsignacion();
}


// ==========================================
// MOSTRAR / CERRAR FORMULARIO
// ==========================================

function mostrarFormularioAsignacion() {
    const panel = document.getElementById(
        "panelFormulario"
    );

    panel.hidden = false;

    panel.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


function cerrarFormularioAsignacion() {
    document.getElementById(
        "panelFormulario"
    ).hidden = true;

    document.getElementById(
        "formAsignacion"
    ).reset();

    [
        "idRestaurante",
        "idLocal",
        "idEmpleado",
        "fechaAsignacion"
    ].forEach(id => {
        document.getElementById(id).disabled = false;
    });

    llenarRestaurantesFormulario();
}


// ==========================================
// GUARDAR ASIGNACIÓN
// ==========================================

async function guardarAsignacion(evento) {
    evento.preventDefault();

    const id = document.getElementById(
        "idAsignacion"
    ).value;

    const turno = document.getElementById(
        "turno"
    ).value.trim();

    const observaciones = document.getElementById(
        "observaciones"
    ).value.trim();

    const boton = document.getElementById(
        "btnGuardarAsignacion"
    );

    boton.disabled = true;

    try {
        if (id) {
            // En una asignación existente solo
            // se pueden editar estos campos.
            await api.put(
                `/asignaciones/${id}`,
                {
                    turno: turno || null,
                    observaciones: observaciones || null
                }
            );

            mostrarMensajeAsignaciones(
                "Asignación actualizada correctamente.",
                "success"
            );

        } else {
            const idRestaurante = Number(
                document.getElementById(
                    "idRestaurante"
                ).value
            );

            const idLocal = Number(
                document.getElementById(
                    "idLocal"
                ).value
            );

            const idEmpleado = Number(
                document.getElementById(
                    "idEmpleado"
                ).value
            );

            if (!idRestaurante || !idLocal || !idEmpleado) {
                throw new Error(
                    "Selecciona un restaurante, local y empleado."
                );
            }

            const datos = {
                id_restaurante: idRestaurante,
                id_local: idLocal,
                id_empleado: idEmpleado,
                turno: turno || null,
                observaciones: observaciones || null
            };

            const fechaAsignacion = document.getElementById(
                "fechaAsignacion"
            ).value;

            // Si no se introduce una fecha,
            // el backend aplica su valor por defecto.
            if (fechaAsignacion) {
                datos.fecha_asignacion =
                    fechaAsignacion.length === 16
                        ? `${fechaAsignacion}:00`
                        : fechaAsignacion;
            }

            await api.post("/asignaciones", datos);

            mostrarMensajeAsignaciones(
                "Asignación registrada correctamente.",
                "success"
            );
        }

        cerrarFormularioAsignacion();
        await cargarDatosAsignaciones();

    } catch (error) {
        mostrarMensajeAsignaciones(
            "No se pudo guardar la asignación: " +
            error.message,
            "error"
        );

    } finally {
        boton.disabled = false;
    }
}


// ==========================================
// FINALIZAR ASIGNACIÓN
// ==========================================

async function finalizarAsignacion(id) {
    const asignacion = asignaciones.find(
        a => a.id_asignacion === id
    );

    if (!asignacion || !asignacion.activo) return;

    const empleado = obtenerEmpleadoAsignacion(
        asignacion.id_empleado
    );

    const nombre = nombreEmpleadoAsignacion(empleado);

    const confirmado = window.confirm(
        `¿Deseas finalizar la asignación de "${nombre}"?\n\n` +
        "La asignación se conservará en el historial " +
        "y no podrá volver a editarse."
    );

    if (!confirmado) return;

    try {
        // DELETE es una finalización lógica:
        // activo=false y fecha_finalizacion registrada.
        await api.delete(
            `/asignaciones/${id}`
        );

        mostrarMensajeAsignaciones(
            "Asignación finalizada correctamente.",
            "success"
        );

        await cargarDatosAsignaciones();

    } catch (error) {
        mostrarMensajeAsignaciones(
            "No se pudo finalizar la asignación: " +
            error.message,
            "error"
        );
    }
}


// ==========================================
// MENSAJES
// ==========================================

function mostrarMensajeAsignaciones(
    mensaje,
    tipo = "error"
) {
    const contenedor = document.getElementById(
        "mensajeAsignaciones"
    );

    contenedor.textContent = mensaje;
    contenedor.className = `module-message ${tipo}`;

    contenedor.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });
}
