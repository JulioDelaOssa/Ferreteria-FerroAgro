document.addEventListener("DOMContentLoaded", function () {
    const clientesDataElement = document.getElementById("clientesVentaData");
    let clientes = [];

    if (clientesDataElement) {
        try {
            clientes = JSON.parse(clientesDataElement.textContent);
        } catch (error) {
            clientes = [];
        }
    }

    const documentoInput = document.getElementById("clienteDocumento") || document.getElementById("cliente_documento");
    const nombreInput = document.getElementById("clienteNombre") || document.getElementById("cliente_nombre");
    const telefonoInput = document.getElementById("clienteTelefono") || document.getElementById("cliente_telefono");
    const correoInput = document.getElementById("clienteCorreo") || document.getElementById("cliente_correo");
    const clienteMensaje = document.getElementById("clienteEstado") || document.getElementById("clienteMensaje");
    const clienteModoInput = document.getElementById("clienteModo");
    const clienteIdInput = document.getElementById("clienteId");

    const clienteNombreBox = document.getElementById("clienteNombreBox");
    const clienteExtraBox = document.getElementById("clienteExtraBox");
    const clienteTelefonoBox = document.getElementById("clienteTelefonoBox");
    const clienteCorreoBox = document.getElementById("clienteCorreoBox");
    const btnNuevoCliente = document.getElementById("mostrarNuevoCliente") || document.getElementById("btnNuevoCliente");
    const clienteNuevoAccion = document.getElementById("clienteNuevoAccion");
    const clienteWidget = document.querySelector(".cliente-documento-widget");

    const productosVenta = document.getElementById("productosVenta");
    const btnAgregarProducto = document.getElementById("btnAgregarProducto");
    const totalVenta = document.getElementById("totalVenta");
    const totalInput = document.getElementById("totalInput");

    let temporizadorBusqueda = null;

    function cambiarVisibilidad(elemento, visible, display) {
        if (!elemento) {
            return;
        }

        elemento.hidden = !visible;
        elemento.style.display = visible ? display : "none";
    }

    function mostrarCamposExtraCliente(visible) {
        cambiarVisibilidad(clienteExtraBox, visible, "grid");
        cambiarVisibilidad(clienteTelefonoBox, visible, "block");
        cambiarVisibilidad(clienteCorreoBox, visible, "block");
    }

    function limpiarDatosCliente(limpiarDocumento) {
        if (limpiarDocumento && documentoInput) {
            documentoInput.value = "";
        }

        if (clienteModoInput) {
            clienteModoInput.value = "";
        }

        if (clienteIdInput) {
            clienteIdInput.value = "";
        }

        if (nombreInput) {
            nombreInput.value = "";
            nombreInput.readOnly = false;
            nombreInput.required = false;
        }

        if (telefonoInput) {
            telefonoInput.value = "";
        }

        if (correoInput) {
            correoInput.value = "";
        }
    }

    function ocultarCamposCliente() {
        cambiarVisibilidad(clienteNombreBox, false, "block");
        mostrarCamposExtraCliente(false);
        cambiarVisibilidad(clienteNuevoAccion || btnNuevoCliente, false, "inline-flex");
        limpiarDatosCliente(false);

        if (clienteMensaje) {
            clienteMensaje.textContent = "Ingresa el documento para validar si el cliente ya existe.";
        }
    }

    function buscarClienteLocal(documento) {
        return clientes.find(function (cliente) {
            return String(cliente.documento || "").trim() === documento;
        });
    }

    function mostrarClienteExistente(cliente) {
        cambiarVisibilidad(clienteNombreBox, true, "block");
        mostrarCamposExtraCliente(false);
        cambiarVisibilidad(clienteNuevoAccion || btnNuevoCliente, false, "inline-flex");

        if (clienteModoInput) {
            clienteModoInput.value = "existente";
        }

        if (clienteIdInput) {
            clienteIdInput.value = cliente.id || "";
        }

        nombreInput.value = cliente.nombre || cliente.cliente_nombre || "";
        nombreInput.readOnly = true;
        nombreInput.required = true;

        if (telefonoInput) {
            telefonoInput.value = "";
        }

        if (correoInput) {
            correoInput.value = "";
        }

        clienteMensaje.textContent = "Cliente existente encontrado.";
    }

    function mostrarBotonNuevoCliente() {
        cambiarVisibilidad(clienteNombreBox, false, "block");
        mostrarCamposExtraCliente(false);
        cambiarVisibilidad(clienteNuevoAccion || btnNuevoCliente, true, "inline-flex");

        if (clienteModoInput) {
            clienteModoInput.value = "";
        }

        if (clienteIdInput) {
            clienteIdInput.value = "";
        }

        if (nombreInput) {
            nombreInput.value = "";
            nombreInput.readOnly = false;
            nombreInput.required = false;
        }

        if (telefonoInput) {
            telefonoInput.value = "";
        }

        if (correoInput) {
            correoInput.value = "";
        }

        clienteMensaje.textContent = "Cliente no encontrado. Puedes registrarlo como nuevo cliente.";
    }

    function mostrarFormularioNuevoCliente() {
        cambiarVisibilidad(clienteNombreBox, true, "block");
        mostrarCamposExtraCliente(true);
        cambiarVisibilidad(clienteNuevoAccion || btnNuevoCliente, false, "inline-flex");

        if (clienteModoInput) {
            clienteModoInput.value = "nuevo";
        }

        if (clienteIdInput) {
            clienteIdInput.value = "";
        }

        nombreInput.value = "";
        nombreInput.readOnly = false;
        nombreInput.required = true;

        if (telefonoInput) {
            telefonoInput.value = "";
        }

        if (correoInput) {
            correoInput.value = "";
        }

        clienteMensaje.textContent = "Completa los datos del nuevo cliente.";
        nombreInput.focus();
    }

    function buscarCliente(documento) {
        const clienteLocal = buscarClienteLocal(documento);

        fetch(`/clientes/buscar/?documento=${encodeURIComponent(documento)}`)
            .then(function (response) {
                if (!response.ok) {
                    return null;
                }

                return response.json();
            })
            .then(function (data) {
                if (!data) {
                    if (clienteLocal) {
                        mostrarClienteExistente(clienteLocal);
                    } else {
                        mostrarBotonNuevoCliente();
                    }

                    return;
                }

                if (data.existe === true || data.existe === "true") {
                    mostrarClienteExistente({
                        id: data.id || (clienteLocal ? clienteLocal.id : ""),
                        nombre: data.nombre || data.cliente_nombre || (clienteLocal ? clienteLocal.nombre : "")
                    });
                } else {
                    mostrarBotonNuevoCliente();
                }
            })
            .catch(function () {
                if (clienteLocal) {
                    mostrarClienteExistente(clienteLocal);
                } else {
                    mostrarBotonNuevoCliente();
                }
            });
    }

    function formatoPesos(valor) {
        return new Intl.NumberFormat("es-CO", {
            style: "currency",
            currency: "COP",
            minimumFractionDigits: 0
        }).format(valor || 0);
    }

    function actualizarFila(fila) {
        const productoSelect = fila.querySelector(".producto-select");
        const cantidadInput = fila.querySelector(".cantidad-input");
        const precioInput = fila.querySelector(".precio-input");
        const subtotalInput = fila.querySelector(".subtotal-input");

        const opcion = productoSelect.options[productoSelect.selectedIndex];
        const precio = parseFloat(opcion.dataset.precio || 0);
        const stock = parseInt(opcion.dataset.stock || 0);
        let cantidad = parseInt(cantidadInput.value || 0);

        if (cantidad < 1) {
            cantidad = 1;
            cantidadInput.value = 1;
        }

        if (stock > 0 && cantidad > stock) {
            cantidad = stock;
            cantidadInput.value = stock;
        }

        const subtotal = precio * cantidad;

        precioInput.value = precio > 0 ? formatoPesos(precio) : "";
        subtotalInput.value = subtotal > 0 ? formatoPesos(subtotal) : "";

        actualizarTotal();
    }

    function actualizarTotal() {
        let total = 0;

        document.querySelectorAll(".producto-venta-item").forEach(function (fila) {
            const productoSelect = fila.querySelector(".producto-select");
            const cantidadInput = fila.querySelector(".cantidad-input");

            const opcion = productoSelect.options[productoSelect.selectedIndex];
            const precio = parseFloat(opcion.dataset.precio || 0);
            const cantidad = parseInt(cantidadInput.value || 0);

            total += precio * cantidad;
        });

        if (totalVenta) {
            totalVenta.textContent = formatoPesos(total);
        }

        if (totalInput) {
            totalInput.value = total;
        }
    }

    function activarEventosFila(fila) {
        const productoSelect = fila.querySelector(".producto-select");
        const cantidadInput = fila.querySelector(".cantidad-input");
        const btnEliminar = fila.querySelector(".btn-eliminar-producto");

        productoSelect.addEventListener("change", function () {
            actualizarFila(fila);
        });

        cantidadInput.addEventListener("input", function () {
            actualizarFila(fila);
        });

        btnEliminar.addEventListener("click", function () {
            const filas = document.querySelectorAll(".producto-venta-item");

            if (filas.length > 1) {
                fila.remove();
                actualizarTotal();
            }
        });
    }

    if (documentoInput && nombreInput && clienteNombreBox && btnNuevoCliente && clienteMensaje) {
        if (clienteWidget && clienteWidget.dataset.initialMode === "existente" && nombreInput.value.trim()) {
            mostrarClienteExistente({
                id: clienteIdInput ? clienteIdInput.value : "",
                nombre: nombreInput.value.trim()
            });
        } else if (clienteWidget && clienteWidget.dataset.initialMode === "nuevo") {
            cambiarVisibilidad(clienteNombreBox, true, "block");
            mostrarCamposExtraCliente(true);
            cambiarVisibilidad(clienteNuevoAccion || btnNuevoCliente, false, "inline-flex");

            if (clienteModoInput) {
                clienteModoInput.value = "nuevo";
            }

            nombreInput.readOnly = false;
            nombreInput.required = true;
        } else {
            ocultarCamposCliente();
        }

        documentoInput.addEventListener("input", function () {
            const documento = documentoInput.value.trim();

            clearTimeout(temporizadorBusqueda);

            if (documento.length < 1) {
                ocultarCamposCliente();
                return;
            }

            clienteMensaje.textContent = "Validando cliente...";

            temporizadorBusqueda = setTimeout(function () {
                buscarCliente(documento);
            }, 500);
        });

        btnNuevoCliente.addEventListener("click", function () {
            mostrarFormularioNuevoCliente();
        });
    }

    if (productosVenta && btnAgregarProducto) {
        document.querySelectorAll(".producto-venta-item").forEach(function (fila) {
            activarEventosFila(fila);
        });

        btnAgregarProducto.addEventListener("click", function () {
            const primeraFila = document.querySelector(".producto-venta-item");
            const nuevaFila = primeraFila.cloneNode(true);

            nuevaFila.querySelector(".producto-select").value = "";
            nuevaFila.querySelector(".cantidad-input").value = 1;
            nuevaFila.querySelector(".precio-input").value = "";
            nuevaFila.querySelector(".subtotal-input").value = "";

            productosVenta.appendChild(nuevaFila);
            activarEventosFila(nuevaFila);
            actualizarTotal();
        });

        actualizarTotal();
    }
});
