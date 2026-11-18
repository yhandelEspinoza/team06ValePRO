(() => {
    'use strict';
    const graficos = [];
    function almacenLeer(clave) { try { return localStorage.getItem(clave); } catch (_) { return null; } }
    function almacenGuardar(clave, valor) { try { localStorage.setItem(clave, valor); } catch (_) {} }


        /* =====================================================
           TEMA CLARO / OSCURO
        ====================================================== */

        const botonTema =
            document.getElementById(
                "botonTema"
            );


        function aplicarTemaGuardado() {

            const temaGuardado =
                almacenLeer(
                    "temaDashboard"
                );


            if (
                temaGuardado === "oscuro"
            ) {

                document.body.classList.add(
                    "modo-oscuro"
                );

            }

        }


        function actualizarIconoTema() {

            const oscuro =
                document.body.classList.contains(
                    "modo-oscuro"
                );


            botonTema.innerHTML =
                oscuro

                    ? '<i class="bi bi-sun-fill"></i>'

                    : '<i class="bi bi-moon-stars-fill"></i>';


            botonTema.title =
                oscuro

                    ? "Cambiar a modo claro"

                    : "Cambiar a modo oscuro";

        }


        aplicarTemaGuardado();

        actualizarIconoTema();



        botonTema.addEventListener(

            "click",

            function() {

                document.body.classList.toggle(
                    "modo-oscuro"
                );


                const oscuro =
                    document.body.classList.contains(
                        "modo-oscuro"
                    );


                almacenGuardar(

                    "temaDashboard",

                    oscuro
                        ? "oscuro"
                        : "claro"

                );


                actualizarIconoTema();

                actualizarColoresGraficos();

            }

        );



        /* =====================================================
           DATOS
        ====================================================== */


        const datosDashboard = document.getElementById('datos-dashboard');
        if (!datosDashboard) return;
        const leer = clave => JSON.parse(datosDashboard.dataset[clave]);
        const colores = ['#2563eb', '#0ea5e9', '#7c3aed', '#16a34a', '#d97706', '#dc2626', '#0891b2'];
        const coloresEstado = {'PENDIENTE FIRMA':'#d97706','PENDIENTE JEFE':'#0ea5e9','APROBADO':'#16a34a','RECHAZADO':'#dc2626'};
        const colorTexto = () => document.body.classList.contains('modo-oscuro') ? '#cbd5e1' : '#64748b';
        function crearGrafico(id, labels, valores, circular=false, dinero=false) {
            const canvas = document.getElementById(id);
            if (!canvas) return null;
            const mensaje = document.createElement('p');
            mensaje.className = 'grafico-mensaje';
            canvas.parentElement.appendChild(mensaje);
            if (!labels.length) {
                canvas.hidden = true;
                mensaje.textContent = dinero && datosDashboard.dataset.montosDisponibles !== 'true'
                    ? 'Montos no disponibles: revise los avisos.' : 'Sin datos para este gráfico.';
                return null;
            }
            if (typeof Chart === 'undefined') {
                canvas.hidden = true;
                mensaje.textContent = 'No se pudo cargar la biblioteca de gráficos. Los indicadores y filtros siguen disponibles.';
                return null;
            }
            try {
                const grafico = new Chart(canvas, {
                    type: circular ? 'doughnut' : 'bar',
                    data: {labels, datasets: [{label: dinero ? 'Monto solicitado' : 'Solicitudes', data: valores,
                        backgroundColor: labels.map((l,i) => id === 'graficoEstados' ? (coloresEstado[l] || colores[i % colores.length]) : colores[i % colores.length]),
                        borderRadius: circular ? 0 : 8, borderWidth: circular ? 3 : 0, maxBarThickness:58}]},
                    options: {responsive:true, maintainAspectRatio:false, animation:{duration:250},
                        plugins:{legend:{display:circular,position:'bottom',labels:{color:colorTexto()}},
                            tooltip:{callbacks:{label:ctx => dinero ? 'S/ ' + Number(ctx.raw).toLocaleString('es-PE',{minimumFractionDigits:2}) : ctx.dataset.label + ': ' + ctx.raw}}},
                        ...(circular ? {cutout:'64%'} : {scales:{x:{ticks:{color:colorTexto()},grid:{display:false}},y:{beginAtZero:true,ticks:{color:colorTexto(),...(dinero ? {callback:v=>'S/ '+v} : {precision:0})}}}})
                    }
                });
                graficos.push(grafico);
                return grafico;
            } catch (_) {
                canvas.hidden = true;
                mensaje.textContent = 'No se pudo dibujar este gráfico.';
                return null;
            }
        }
        crearGrafico('graficoEstados', leer('estadosLabels'), leer('estadosValores'));
        const distribucion = crearGrafico('graficoDistribucion', leer('categoriasLabels'), leer('categoriasValores'), true);
        crearGrafico('graficoAreas', leer('areasLabels'), leer('areasValores'));
        crearGrafico('graficoMontos', leer('montosLabels'), leer('montosValores'), false, true);
        document.getElementById('tipoDistribucion').addEventListener('change', e => {
            const estado = e.target.value === 'estados';
            document.getElementById('tituloDistribucion').textContent = estado ? 'Distribución de estados' : 'Solicitudes por categoría';
            if (distribucion) {
                distribucion.data.labels = leer(estado ? 'estadosLabels' : 'categoriasLabels');
                distribucion.data.datasets[0].data = leer(estado ? 'estadosValores' : 'categoriasValores');
                distribucion.data.datasets[0].backgroundColor = distribucion.data.labels.map((_,i)=>colores[i%colores.length]);
                distribucion.update();
            }
        });
        function actualizarColoresGraficos() {
            graficos.forEach(g => {
                g.options.plugins.legend.labels.color = colorTexto();
                if (g.options.scales.x) {
                    g.options.scales.x.ticks.color = colorTexto();
                    g.options.scales.y.ticks.color = colorTexto();
                }
                g.update();
            });
        }
        const buscador =
            document.getElementById(
                "buscador"
            );


        const filtroEstado =
            document.getElementById(
                "filtroEstado"
            );


        const filtroArea =
            document.getElementById(
                "filtroArea"
            );


        const filtroCategoria =
            document.getElementById(
                "filtroCategoria"
            );


        const botonLimpiar =
            document.getElementById(
                "botonLimpiar"
            );


        const filas =
            document.querySelectorAll(
                "#tablaSolicitudes tbody tr[data-codigo]"
            );


        const contadorResultados =
            document.getElementById(
                "contador-resultados"
            );



        function aplicarFiltros() {

            const texto =
                buscador.value
                    .toLowerCase()
                    .trim();


            const estadoSeleccionado =
                filtroEstado.value
                    .toLowerCase();


            const areaSeleccionada =
                filtroArea.value
                    .toLowerCase();


            const categoriaSeleccionada =
                filtroCategoria.value
                    .toLowerCase();


            let visibles = 0;



            filas.forEach(

                function(fila) {

                    const codigo =
                        fila.dataset.codigo;


                    const solicitante =
                        fila.dataset.solicitante;


                    const area =
                        fila.dataset.area;


                    const categoria =
                        fila.dataset.categoria;


                    const estado =
                        fila.dataset.estado;



                    const coincideTexto =

                        codigo.includes(texto)

                        ||

                        solicitante.includes(texto)

                        ||

                        area.includes(texto)

                        ||

                        categoria.includes(texto);



                    const coincideEstado =

                        estadoSeleccionado === ""

                        ||

                        estado ===
                        estadoSeleccionado;



                    const coincideArea =

                        areaSeleccionada === ""

                        ||

                        area ===
                        areaSeleccionada;



                    const coincideCategoria =

                        categoriaSeleccionada === ""

                        ||

                        categoria ===
                        categoriaSeleccionada;



                    const mostrar =

                        coincideTexto

                        &&

                        coincideEstado

                        &&

                        coincideArea

                        &&

                        coincideCategoria;



                    fila.style.display =
                        mostrar
                            ? ""
                            : "none";


                    if (mostrar) {
                        visibles++;
                    }

                }

            );


            document.getElementById('sinResultados').hidden = visibles > 0;
            contadorResultados.textContent =
                visibles
                +
                " resultado(s)";

        }



        buscador.addEventListener(
            "input",
            aplicarFiltros
        );


        filtroEstado.addEventListener(
            "change",
            aplicarFiltros
        );


        filtroArea.addEventListener(
            "change",
            aplicarFiltros
        );


        filtroCategoria.addEventListener(
            "change",
            aplicarFiltros
        );



        botonLimpiar.addEventListener(

            "click",

            function() {

                buscador.value =
                    "";

                filtroEstado.value =
                    "";

                filtroArea.value =
                    "";

                filtroCategoria.value =
                    "";

                aplicarFiltros();

            }

        );


        aplicarFiltros();

        /* =====================================================
           FASE 2B - DETALLE Y FIRMA
        ====================================================== */
        const vp2ModalDetalle = document.getElementById("vp2ModalDetalle");
        const vp2ModalFirma = document.getElementById("vp2ModalFirma");
        const vp2FirmaFrame = document.getElementById("vp2FirmaFrame");
        const vp2FirmaLink = document.getElementById("vp2FirmaLink");

        function vp2Texto(id, valor) {
            const el = document.getElementById(id);
            if (el) el.textContent = String(valor || "").trim() || "-";
        }

        function vp2Abrir(modal) {
            modal._opener = document.activeElement;
            modal.classList.add("vp2-activo");
            modal.querySelector("button").focus();
            document.body.classList.add("vp2-modal-open");
        }

        function vp2Cerrar(modal) {
            modal.classList.remove("vp2-activo");
            modal._opener?.focus();
            if (!document.querySelector(".vp2-modal.vp2-activo")) {
                document.body.classList.remove("vp2-modal-open");
            }
            if (modal === vp2ModalFirma) {
                vp2FirmaFrame.removeAttribute("src");
            }
        }

        function vp2UrlSegura(valor) {
            try {
                const url = new URL(String(valor || '').trim());
                return url.protocol === 'https:' && !url.username && !url.password ? url.href : '';
            } catch (_) { return ''; }
        }
        function vp2PreviewDrive(valor) {
            const seguro = vp2UrlSegura(valor);
            if (!seguro) return '';
            const url = new URL(seguro);
            const match = url.pathname.match(/^\/file\/d\/([a-zA-Z0-9_-]+)/);
            if (url.hostname === 'drive.google.com' && match) return 'https://drive.google.com/file/d/' + match[1] + '/preview';
            return seguro;
        }
        document.querySelectorAll(".js-vp2-detalle").forEach(function(boton) {
            boton.addEventListener("click", function() {
                const d = boton.dataset;
                vp2Texto("vp2dCodigo", d.codigo);
                vp2Texto("vp2dEstado", d.estado);
                vp2Texto("vp2dSolicitante", d.solicitante);
                vp2Texto("vp2dNombre", ((d.nombres || "") + " " + (d.apellidos || "")).trim());
                vp2Texto("vp2dDocumento", d.documento);
                vp2Texto("vp2dCorreo", d.correo);
                vp2Texto("vp2dCargo", d.cargo);
                vp2Texto("vp2dArea", d.area);
                vp2Texto("vp2dCentro", d.centroCosto);
                vp2Texto("vp2dCategoria", d.categoria);
                vp2Texto("vp2dMonto", d.monto);
                vp2Texto("vp2dUso", d.uso);
                vp2Texto("vp2dRegistro", d.registro);
                vp2Texto("vp2dFirma", d.firmaEstado);
                vp2Texto("vp2dMotivo", d.motivo);
                vp2Abrir(vp2ModalDetalle);
            });
        });

        document.querySelectorAll(".js-vp2-firma").forEach(function(boton) {
            boton.addEventListener("click", function() {
                const d = boton.dataset;
                const original = vp2UrlSegura(d.firmaUrl);
                vp2Texto("vp2fCodigo", d.codigo);
                vp2Texto("vp2fSolicitante", d.solicitante);
                vp2Texto("vp2fTipo", d.firmaTipo);
                vp2Texto("vp2fEstado", d.firmaEstado);
                vp2Texto("vp2fRegistro", d.firmaRegistro);
                const preview = vp2PreviewDrive(original);
                if (preview) vp2FirmaFrame.src = preview;
                vp2FirmaLink.href = original || "#";
                vp2FirmaLink.style.display = original ? "inline-flex" : "none";
                vp2Abrir(vp2ModalFirma);
            });
        });

        document.querySelectorAll(".js-vp2-cerrar").forEach(function(boton) {
            boton.addEventListener("click", function() {
                vp2Cerrar(boton.closest(".vp2-modal"));
            });
        });

        [vp2ModalDetalle, vp2ModalFirma].forEach(function(modal) {
            modal.addEventListener("click", function(e) {
                if (e.target === modal) vp2Cerrar(modal);
            });
        });

        document.addEventListener("keydown", function(e) {
            if (e.key !== "Escape") return;
            if (vp2ModalFirma.classList.contains("vp2-activo")) vp2Cerrar(vp2ModalFirma);
            else if (vp2ModalDetalle.classList.contains("vp2-activo")) vp2Cerrar(vp2ModalDetalle);
        });


})();
