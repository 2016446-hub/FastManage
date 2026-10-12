
const API_URL = "/api";

let csrfToken = null;

async function obtenerTokenCSRF() {
    const respuesta = await fetch(
        `${API_URL}/auth/csrf`,
        {
            method: "GET",
            credentials: "same-origin",
            cache: "no-store"
        }
    );

    if (!respuesta.ok) {
        throw new Error(
            "No se pudo verificar la sesión."
        );
    }

    const datos = await respuesta.json();

    csrfToken = datos.csrf_token;

    return csrfToken;
}

async function apiRequest(endpoint, options = {}) {
    const metodo = (
        options.method || "GET"
    ).toUpperCase();

    const headers = new Headers(
        options.headers || {}
    );

    const requiereCSRF = ![
        "GET",
        "HEAD",
        "OPTIONS"
    ].includes(metodo);

    const rutaPublica = [
        "/auth/login",
        "/auth/registro"
    ].includes(endpoint);

    if (requiereCSRF && !rutaPublica) {
        if (!csrfToken) {
            await obtenerTokenCSRF();
        }

        headers.set(
            "X-CSRF-Token",
            csrfToken
        );
    }

    let body = options.body;

    if (
        body !== undefined &&
        body !== null &&
        !(body instanceof FormData) &&
        typeof body !== "string"
    ) {
        headers.set(
            "Content-Type",
            "application/json"
        );

        body = JSON.stringify(body);
    }

    const respuesta = await fetch(
        `${API_URL}${endpoint}`,
        {
            ...options,
            method: metodo,
            headers,
            body,
            credentials: "same-origin",
            cache: "no-store"
        }
    );

    const datos = respuesta.status === 204
        ? null
        : await respuesta.json().catch(() => null);

    if (!respuesta.ok) {
        let mensaje = "Ocurrió un error inesperado.";

        if (Array.isArray(datos?.detail)) {
            mensaje = datos.detail
                .map(error => error.msg)
                .join(". ");
        } else if (typeof datos?.detail === "string") {
            mensaje = datos.detail;
        }

        if (respuesta.status === 401) {
            csrfToken = null;
        }

        throw new Error(mensaje);
    }

    return datos;
}

const api = {
    get: (ruta) =>
        apiRequest(ruta),

    post: (ruta, datos) =>
        apiRequest(ruta, {
            method: "POST",
            body: datos
        }),

    put: (ruta, datos) =>
        apiRequest(ruta, {
            method: "PUT",
            body: datos
        }),

    patch: (ruta, datos) =>
        apiRequest(ruta, {
            method: "PATCH",
            body: datos
        }),

    delete: (ruta) =>
        apiRequest(ruta, {
            method: "DELETE"
        })
};

const authAPI = {
    registrar: (datos) =>
        api.post("/auth/registro", datos),

    login: async (datos) => {
        csrfToken = null;
        return api.post("/auth/login", datos);
    },

    obtenerPerfil: () =>
        api.get("/auth/me"),

    logout: async () => {
        try {
            return await api.post("/auth/logout");
        } finally {
            csrfToken = null;
        }
    }
};
