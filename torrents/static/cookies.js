;(function($) {
    $.cookiesLaw = {
        notified: false,
        hide_msg: false,
        start_scripts: false,
        run_scripts: function() {
            if (!this.start_scripts) return;
            this.start_scripts();
            this.start_scripts = false; // avoid duplicate calls
        },
        initialize:function(domains, start_scripts) {
            // Save local variables
            this.start_scripts = start_scripts;
            this.domains = domains;

            // Check local cookie
            var cookie_level = $.cookie("cookie_level");
            this.notified = cookie_level>0;
            this.hide_msg = cookie_level>1;

            // If notified, don't notify again
            if (this.notified) {
                this.final_process();
                return;
            }

            this.visit_domains("notify", function(){
                $.cookie("cookie_level", $.cookiesLaw.hide_msg?2:1, {expires: 3650, path: '/' });
                $.cookiesLaw.final_process();
            });
        },
        visit_domains: function(action, after) {
            // Check geolocation and set cookie for all domains
            var requests = []
            for (var i = 0; i < this.domains.length; i++) {
                requests.push($.ajax({
                    type: 'GET', url: this.domains[i]+"?"+action,
                    async: true, contentType: "application/json", dataType: 'jsonp',
                    success: function(response) {
                        if (response>0) {
                            $.cookiesLaw.notified = true;
                            if (response>1) {
                                $.cookiesLaw.hide_msg = true;
                            }
                        }
                    }
                }));
            }

            // Show alert when finish or run scripts
            $.when.apply($,requests).done(after);
        },
        final_process: function() {
            if (this.notified)
                this.run_scripts();

            if (!this.hide_msg) {
                if (this.notified)
                    trackGAEvent('CookieLaw', "Notified");

                $(function(){
                    show_alert("cookies", "<a href='#' id='cookies_accept'>cerrar</a>Utilizamos cookies propias y de terceros para mejorar nuestros servicios y realizar estadísticas sobre el uso de nuestra web.<br/>Si continua navegando, consideramos que acepta su uso. Puede cambiar la configuración u obtener más información <a id='cookies_info' href='#'>aquí</a>.", "info");
                    $("#cookies_accept").click(function(event){
                        event.preventDefault();
                        $.cookie("cookie_level", 2, {expires: 3650, path: '/' });
                        $.cookiesLaw.visit_domains("accept", function(){
                            $.cookiesLaw.run_scripts();
                            trackGAEvent('CookieLaw', "Close");
                            hide_alert("cookies");
                        });
                    });
                    $("#cookies_info").click(function(event){
                        event.preventDefault();
                        $.cookiesLaw.showMoreInfo();
                    });
                });
            }
        },
        showMoreInfo: function() {
            $.colorbox({html:this.legend, height:"80%", width:"80%",close:"cerrar", fixed:true});
        },
        legend:"<div class='text_page'><h1>Política de cookies</h1><h2>¿Qué es una cookie?</h2><p>Una cookie es un fichero que se descarga en su ordenador al acceder a determinadas páginas web. Las cookies permiten a una página web, entre otras cosas, almacenar y recuperar información sobre los hábitos de navegación de un usuario o de su equipo y, dependiendo de la información que contengan y de la forma en que utilice su equipo, pueden utilizarse para reconocer al usuario. <small><a target='_blank' href='http://www.iabspain.net/privacidadeninternet/conocer'>Más información</a></small></p>\
        <h2>¿Qué tipos de cookies existen?</h2><p>Las cookies se suelen clasificar principalmente por su duración y por el uso que se les da.</p><p>Según su duración, se puede diferenciar entre cookies de sesión, que expiran cuando el usuario cierra el navegador, y las cookies permanentes, que llevan asociada una duración a partir del momento de creación.</p><p>Por otro lado, podemos encontrar 5 tipos de cookies, según su objetivo:</p>\
        <ul><li><strong>Rendimiento</strong>: Este tipo de cookie recuerda sus preferencias para las herramientas que se encuentran en los servicios, por lo que no tiene que volver a configurar el servicio cada vez que usted visita. A modo de ejemplo, en esta tipología se incluyen:\
        <ul><li>Ajustes de volumen de reproductores de vídeo o sonido.</li><li>Las velocidades de transmisión de vídeo que sean compatibles con su navegador.</li><li>Los objetos guardados en el carrito de la compra en los servicios de e-commerce tales como tiendas.</li></ul></li>\
        <li><strong>Geolocalización</strong>: Estas cookies son utilizadas para averiguar en qué país se encuentra cuando se solicita un servicio. Esta cookie es totalmente anónima, y sólo se utiliza para ayudar a orientar el contenido a su ubicación. Permiten establecer la ubicación geográfica del usuario.</li>\
        <li><strong>Analítica</strong>: Cada vez que un usuario visita un servicio, una herramienta de un proveedor externo genera una cookie analítica en el ordenador del usuario. Esta cookie que sólo se genera en la visita, servirá en próximas visitas al mismo servicio para identificar de forma anónima al visitante. Los objetivos principales que se persiguen son:\
        <ul><li>Permitir la identificación anónima de los usuarios navegantes a través de la cookie (identifica navegadores y dispositivos, no personas) y por lo tanto la contabilización aproximada del número de visitantes y su tendencia en el tiempo.</li><li>Identificar de forma anónima los contenidos más visitados y por lo tanto más atractivos para los usuarios.</li><li>Saber si el usuario que está accediendo es nuevo o repite visita.</li></ul></li>\
        <li><strong>Registro</strong>: Las cookies de registro se generan una vez que el usuario se ha registrado o posteriormente ha abierto su sesión, y se utilizan para identificarle en los servicios con los siguientes objetivos:\
        <ul><li>Mantener al usuario identificado de forma que, si cierra un servicio, el navegador o el ordenador y en otro momento u otro día vuelve a entrar en dicho servicio, seguirá identificado, facilitando así su navegación sin tener que volver a identificarse. Esta funcionalidad se puede suprimir si el usuario pulsa la funcionalidad cerrar sesión, de forma que esta cookie se elimina y la próxima vez que entre en el servicio el usuario tendrá que iniciar sesión para estar identificado.</li><li>Comprobar si el usuario está autorizado para acceder a ciertos servicios, por ejemplo, para participar en un concurso.</li></ul></li>\
        <li><strong>Publicidad</strong>: Este tipo de cookies permiten ampliar la información de los anuncios mostrados a cada usuario. Entre otros, se almacena la duración o frecuencia de visualización de posiciones publicitarias, la interacción con las mismas, o los patrones de navegación y/o comportamientos del usuario ya que ayudan a conformar un perfil de interés publicitario. De este modo, permiten ofrecer publicidad afín a los intereses del usuario.</li></ul>\
        <h2>¿Qué cookies usamos en los sitios web de la familia Torrents.com?</h2><p>Utilizamos las siguientes cookies:</p><table cellspacing='1'>\
        <tr><th width='20%'>Nombre</th><th width='15%'>Tipo</th><th width='15%'>Duracion</th><th width='50%'>Objetivo</th></tr>\
        <tr><td>cookie_level</td><td>Rendimiento</td><td>10 años</td><td>Permite saber si el usuario ha sido notificado sobre nuestra política de cookies.</td></tr>\
        <tr><td>adult_confirm</td><td>Rendimiento</td><td>10 años</td><td>Evita preguntar al usuario si es mayor de edad más de una vez.</td></tr>\
        <tr><td>PRUM_EPISODES</td><td>Analítica</td><td>Sesión</td><td rowspan='2'>Servicio provisto por pingdom.com que mide el rendimiento de la página para los usuarios finales.</td></tr>\
        <tr><td>__cfduid</td><td>Analítica</td><td>5 años</td></tr>\
        <tr><td>__utma</td><td>Analítica</td><td>2 años</td><td rowspan='5'>Servicio provisto por google.com que genera estadísticas sobre los accesos al sitio web.</td></tr>\
        <tr><td>__utmb</td><td>Analítica</td><td>30 minutos</td></tr>\
        <tr><td>__utmc</td><td>Analítica</td><td>Sesión</td></tr>\
        <tr><td>__utmz</td><td>Analítica</td><td>6 meses</td></tr>\
        <tr><td>__ga</td><td>Analítica</td><td>2 años</td></tr>\
        </table>\
        <h2>¿Cómo se pueden administrar las cookies?</h2>\
        <p>Puede permitir, bloquear o eliminar las cookies instaladas en su equipo mediante la configuración de las opciones del navegador instalado en su ordenador:</p>\
        <ul><li><a target='_blank' href='http://support.google.com/chrome/bin/answer.py?hl=es&answer=95647'>Google Chrome</a></li><li><a target='_blank' href='http://windows.microsoft.com/es-es/windows7/how-to-manage-cookies-in-internet-explorer-9'>Internet Explorer</a></li><li><a target='_blank' href='http://support.mozilla.org/es/kb/habilitar-y-deshabilitar-cookies-que-los-sitios-we'>Mozilla Firefox</a></li><li><a target='_blank' href='http://support.apple.com/kb/ph5042'>Safari</a></li></ul>\
        <p>Los sitios web de la familia torrents.com continuarán funcionando si se bloquean o eliminan cookies asociadas a estos, aunque es posible que vuelvan a realizar preguntas que ya han sido respondidas.</p></div>"
    };
})(jQuery);
