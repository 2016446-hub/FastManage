
let empleados = [];
let restaurantesEmpleados = [];

document.addEventListener(
    "DOMContentLoaded",
    iniciarEmpleados
);


// ==========================================
// INICIALIZACIÓN
// ==========================================

async function iniciarEmpleados() {
    configurarEventosEmpleados();

    try {
        const usuario = await authAPI.obtenerPerfil();
        mostrarUsuarioEmpleados(usuario);
    } catch (error) {
        window.location.replace("/login.html");
        return;
    }

    await cargarDatosEmpleados();
}


// ==========================================
// USUARIO Y NAVEGACIÓN
// ==========================================

function mostrarUsuarioEmpleados(usuario) {
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
}


function configurarEventosEmpleados() {
    document.getElementById(
        "btnNuevoEmpleado"
    ).addEventListener(
        "click",
        abrirFormularioNuevoEmpleado
    );

    document.getElementById(
        "btnCancelarFormulario"
    ).addEventListener(
        "click",
        cerrarFormularioEmpleado
    );

    document.getElementById(
        "formEmpleado"
    ).addEventListener(
        "submit",
        guardarEmpleado
    );

    [
        "buscarEmpleado",
        "filtroRestaurante",
        "filtroPuesto",
        "filtroEstado"
    ].forEach(id => {
        const elemento = document.getElementById(id);

        elemento.addEventListener(
            id === "buscarEmpleado" ? "input" : "change",
            mostrarEmpleados
        );
    });

    document.getElementById(
        "btnCerrarSesion"
    ).addEventListener(
        "click",
        cerrarSesionEmpleados
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


async function cerrarSesionEmpleados() {
    const boton = document.getElementById(
        "btnCerrarSesion"
    );

    boton.disabled = true;

    try {
        await authAPI.logout();
        window.location.replace("/login.html");
    } catch (error) {
        mostrarMensajeEmpleados(error.message, "error");
        boton.disabled = false;
    }
}


// ==========================================
// CARGAR DATOS
// ==========================================

async function cargarDatosEmpleados() {
    try {
        const [restaurantes, listaEmpleados] =
            await Promise.all([
                api.get("/restaurantes"),
                api.get("/empleados")
            ]);

        restaurantesEmpleados = restaurantes;
        empleados = listaEmpleados;

        llenarRestaurantesEmpleados();
        llenarPuestosEmpleados();
        mostrarEmpleados();

    } catch (error) {
        mostrarMensajeEmpleados(
            "No se pudieron cargar los empleados: " +
            error.message,
            "error"
        );
    }
}


// ==========================================
// SELECTOR DE RESTAURANTES
// ==========================================

function llenarRestaurantesEmpleados() {
    const selectorFormulario = document.getElementById(
        "idRestaurante"
    );

    const selectorFiltro = document.getElementById(
        "filtroRestaurante"
    );

    const valorFiltro = selectorFiltro.value;

    selectorFormulario.replaceChildren();
    selectorFiltro.replaceChildren();

    selectorFormulario.add(
        new Option("Selecciona un restaurante", "")
    );

    selectorFiltro.add(
        new Option("Todos los restaurantes", "todos")
    );

    restaurantesEmpleados.forEach(restaurante => {
        const etiqueta = restaurante.activo
            ? restaurante.nombre
            : `${restaurante.nombre} (inactivo)`;

        selectorFormulario.add(
            new Option(
                etiqueta,
                String(restaurante.id_restaurante)
            )
        );

        selectorFiltro.add(
            new Option(
                etiqueta,
                String(restaurante.id_restaurante)
            )
        );
    });

    if (Array.from(selectorFiltro.options).some(
        opcion => opcion.value === valorFiltro
    )) {
        selectorFiltro.value = valorFiltro;
    }
}


function obtenerRestauranteEmpleado(id) {
    const restaurante = restaurantesEmpleados.find(
        r => r.id_restaurante === id
    );

    return restaurante
        ? restaurante.nombre
        : "Restaurante no disponible";
}


// ==========================================
// FILTRO DE PUESTOS
// ==========================================

function llenarPuestosEmpleados() {
    const selector = document.getElementById(
        "filtroPuesto"
    );

    const valorAnterior = selector.value;

    const puestos = [
        ...new Set(
            empleados
                .map(empleado => empleado.puesto)
                .filter(Boolean)
        )
    ].sort((a, b) => a.localeCompare(b, "es"));

    selector.replaceChildren();
    selector.add(new Option("Todos los puestos", "todos"));

    puestos.forEach(puesto => {
        selector.add(new Option(puesto, puesto));
    });

    if (puestos.includes(valorAnterior)) {
        selector.value = valorAnterior;
    }
}


// ==========================================
// MOSTRAR EMPLEADOS
// ==========================================

function mostrarEmpleados() {
    const contenedor = document.getElementById(
        "contenedorEmpleados"
    );

    const busqueda = document.getElementById(
        "buscarEmpleado"
    ).value.trim().toLowerCase();

    const filtroRestaurante = document.getElementById(
        "filtroRestaurante"
    ).value;

    const filtroPuesto = document.getElementById(
        "filtroPuesto"
    ).value;

    const filtroEstado = document.getElementById(
        "filtroEstado"
    ).value;

    const filtrados = empleados.filter(empleado => {
        const texto = [
            empleado.nombre,
            empleado.primer_apellido,
            empleado.segundo_apellido,
            empleado.identificacion
        ].filter(Boolean).join(" ").toLowerCase();

        const coincideBusqueda = texto.includes(busqueda);

        const coincideRestaurante =
            filtroRestaurante === "todos" ||
            empleado.id_restaurante ===
                Number(filtroRestaurante);

        const coincidePuesto =
            filtroPuesto === "todos" ||
            empleado.puesto === filtroPuesto;

        const coincideEstado =
            filtroEstado === "todos" ||
            (
                filtroEstado === "activos" &&
                empleado.activo === true
            ) ||
            (
                filtroEstado === "inactivos" &&
                empleado.activo === false
            );

        return coincideBusqueda &&
            coincideRestaurante &&
            coincidePuesto &&
            coincideEstado;
    });

    document.getElementById(
        "contadorEmpleados"
    ).textContent = `${filtrados.length} empleado(s)`;

    contenedor.replaceChildren();

    if (filtrados.length === 0) {
        const mensaje = document.createElement("p");
        mensaje.className = "empty-state";
        mensaje.textContent = "No se encontraron empleados.";

        contenedor.appendChild(mensaje);
        return;
    }

    filtrados.forEach(empleado => {
        const tarjeta = document.createElement("article");
        tarjeta.className = "entity-card";

        const encabezado = document.createElement("div");
        encabezado.className = "entity-card-header";

        const nombre = document.createElement("h4");

        nombre.textContent = [
            empleado.nombre,
            empleado.primer_apellido,
            empleado.segundo_apellido
        ].filter(Boolean).join(" ");

        const estado = document.createElement("span");

        estado.className = empleado.activo
            ? "status-badge status-active"
            : "status-badge status-inactive";

        estado.textContent = empleado.activo
            ? "Activo"
            : "Inactivo";

        encabezado.append(nombre, estado);

        const puesto = document.createElement("p");
        puesto.textContent =
            "Puesto: " + (empleado.puesto || "Sin definir");

        const restaurante = document.createElement("p");
        restaurante.textContent =
            "Restaurante: " +
            obtenerRestauranteEmpleado(empleado.id_restaurante);

        const identificacion = document.createElement("p");
        identificacion.textContent =
            "Identificación: " +
            (empleado.identificacion || "No registrada");

        const contratacion = document.createElement("p");
        contratacion.textContent =
            "Contratación: " +
            (empleado.fecha_contratacion
                ? empleado.fecha_contratacion.slice(0, 10)
                : "No registrada");

        const acciones = document.createElement("div");
        acciones.className = "entity-card-actions";

        const botonEditar = document.createElement("button");
        botonEditar.type = "button";
        botonEditar.className = "btn btn-outline";
        botonEditar.textContent = "Editar";

        botonEditar.addEventListener("click", () => {
            editarEmpleado(empleado.id_empleado);
        });

        const botonEstado = document.createElement("button");
        botonEstado.type = "button";
        botonEstado.className = "btn btn-outline";

        botonEstado.textContent = empleado.activo
            ? "Desactivar"
            : "Reactivar";

        botonEstado.addEventListener("click", () => {
            cambiarEstadoEmpleado(empleado.id_empleado);
        });

        acciones.append(botonEditar, botonEstado);

        tarjeta.append(
            encabezado,
            puesto,
            restaurante,
            identificacion,
            contratacion,
            acciones
        );

        contenedor.appendChild(tarjeta);
    });
}


// ==========================================
// NUEVO EMPLEADO
// ==========================================

function abrirFormularioNuevoEmpleado() {
    const formulario = document.getElementById(
        "formEmpleado"
    );

    formulario.reset();

    document.getElementById("idEmpleado").value = "";

    const selector = document.getElementById(
        "idRestaurante"
    );

    selector.disabled = false;

    Array.from(selector.options).forEach(opcion => {
        if (!opcion.value) return;

        const restaurante = restaurantesEmpleados.find(
            r => r.id_restaurante === Number(opcion.value)
        );

        opcion.disabled = !restaurante?.activo;
    });

    document.getElementById(
        "tituloFormulario"
    ).textContent = "Nuevo empleado";

    document.getElementById(
        "btnGuardarEmpleado"
    ).textContent = "Guardar empleado";

    mostrarFormularioEmpleado();
}


// ==========================================
// EDITAR EMPLEADO
// ==========================================

function editarEmpleado(id) {
    const empleado = empleados.find(
        e => e.id_empleado === id
    );

    if (!empleado) return;

    const asignar = (campo, valor) => {
        document.getElementById(campo).value = valor ?? "";
    };

    asignar("idEmpleado", empleado.id_empleado);
    asignar("idRestaurante", empleado.id_restaurante);
    asignar("identificacion", empleado.identificacion);
    asignar("nombre", empleado.nombre);
    asignar("primerApellido", empleado.primer_apellido);
    asignar("segundoApellido", empleado.segundo_apellido);
    asignar("correo", empleado.correo);
    asignar("telefono", empleado.telefono);
    asignar("puesto", empleado.puesto);
    asignar("tipoContrato", empleado.tipo_contrato);
    asignar("salario", empleado.salario);
    asignar("direccion", empleado.direccion);
    asignar("contactoEmergencia", empleado.contacto_emergencia);
    asignar("telefonoEmergencia", empleado.telefono_emergencia);

    asignar(
        "fechaNacimiento",
        empleado.fecha_nacimiento
            ? empleado.fecha_nacimiento.slice(0, 10)
            : ""
    );

    asignar(
        "fechaContratacion",
        empleado.fecha_contratacion
            ? empleado.fecha_contratacion.slice(0, 10)
            : ""
    );

    // El restaurante no puede cambiarse desde
    // la edición porque existen relaciones
    // laborales vinculadas a ese identificador.
    document.getElementById(
        "idRestaurante"
    ).disabled = true;

    document.getElementById(
        "tituloFormulario"
    ).textContent = "Editar empleado";

    document.getElementById(
        "btnGuardarEmpleado"
    ).textContent = "Guardar cambios";

    mostrarFormularioEmpleado();
}


// ==========================================
// MOSTRAR / CERRAR FORMULARIO
// ==========================================

function mostrarFormularioEmpleado() {
    const panel = document.getElementById(
        "panelFormulario"
    );

    panel.hidden = false;

    panel.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


function cerrarFormularioEmpleado() {
    document.getElementById(
        "panelFormulario"
    ).hidden = true;

    document.getElementById(
        "formEmpleado"
    ).reset();

    document.getElementById(
        "idRestaurante"
    ).disabled = false;
}


// ==========================================
// GUARDAR EMPLEADO
// ==========================================

async function guardarEmpleado(evento) {
    evento.preventDefault();

    const id = document.getElementById(
        "idEmpleado"
    ).value;

    const obtenerValor = campo => {
        const valor = document.getElementById(
            campo
        ).value.trim();

        return valor || null;
    };

    const fechaNacimiento = obtenerValor("fechaNacimiento");
    const fechaContratacion = obtenerValor("fechaContratacion");
    const salario = obtenerValor("salario");

    const datos = {
        identificacion: obtenerValor("identificacion"),
        nombre: obtenerValor("nombre"),
        primer_apellido: obtenerValor("primerApellido"),
        segundo_apellido: obtenerValor("segundoApellido"),
        fecha_nacimiento: fechaNacimiento
            ? `${fechaNacimiento}T00:00:00`
            : null,
        correo: obtenerValor("correo"),
        telefono: obtenerValor("telefono"),
        direccion: obtenerValor("direccion"),
        puesto: obtenerValor("puesto"),
        tipo_contrato: obtenerValor("tipoContrato"),
        fecha_contratacion: fechaContratacion
            ? `${fechaContratacion}T00:00:00`
            : null,
        salario: salario === null ? null : salario,
        contacto_emergencia: obtenerValor("contactoEmergencia"),
        telefono_emergencia: obtenerValor("telefonoEmergencia")
    };

    const boton = document.getElementById(
        "btnGuardarEmpleado"
    );

    boton.disabled = true;

    try {
        if (id) {
            await api.put(
                `/empleados/${id}`,
                datos
            );

            mostrarMensajeEmpleados(
                "Empleado actualizado correctamente.",
                "success"
            );
        } else {
            datos.id_restaurante = Number(
                document.getElementById(
                    "idRestaurante"
                ).value
            );

            // El estado activo se establece
            // automáticamente en el backend.
            await api.post("/empleados", datos);

            mostrarMensajeEmpleados(
                "Empleado registrado correctamente.",
                "success"
            );
        }

        cerrarFormularioEmpleado();
        await cargarDatosEmpleados();

    } catch (error) {
        mostrarMensajeEmpleados(
            "No se pudo guardar el empleado: " +
            error.message,
            "error"
        );

    } finally {
        boton.disabled = false;
    }
}


// ==========================================
// DESACTIVAR / REACTIVAR
// ==========================================

async function cambiarEstadoEmpleado(id) {
    const empleado = empleados.find(
        e => e.id_empleado === id
    );

    if (!empleado) return;

    const accion = empleado.activo
        ? "desactivar"
        : "reactivar";

    const nombre = [
        empleado.nombre,
        empleado.primer_apellido
    ].filter(Boolean).join(" ");

    const advertencia = empleado.activo
        ? "\n\nEl registro del empleado se conservará. " +
          "Revisa sus asignaciones laborales vigentes."
        : "";

    const confirmado = window.confirm(
        `¿Deseas ${accion} a "${nombre}"?` +
        advertencia
    );

    if (!confirmado) return;

    try {
        if (empleado.activo) {
            // DELETE realiza desactivación lógica.
            await api.delete(
                `/empleados/${id}`
            );
        } else {
            // Reactivación mediante actualización.
            await api.put(
                `/empleados/${id}`,
                { activo: true }
            );
        }

        mostrarMensajeEmpleados(
            `Empleado ${empleado.activo
                ? "desactivado"
                : "reactivado"} correctamente.`,
            "success"
        );

        await cargarDatosEmpleados();

    } catch (error) {
        mostrarMensajeEmpleados(
            "No se pudo cambiar el estado: " +
            error.message,
            "error"
        );
    }
}


// ==========================================
// MENSAJES
// ==========================================

function mostrarMensajeEmpleados(
    mensaje,
    tipo = "error"
) {
    const contenedor = document.getElementById(
        "mensajeEmpleados"
    );

    contenedor.textContent = mensaje;
    contenedor.className = `module-message ${tipo}`;

    contenedor.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });
}
