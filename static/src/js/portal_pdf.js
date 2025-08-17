odoo.define('portal_sale_pdf.portal', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var core = require('web.core');

    // Widget específico para el portal del cliente
    publicWidget.registry.PortalPDFViewer = publicWidget.Widget.extend({
        selector: '.portal-pdf-preview',
        events: {
            'click .btn-fullscreen': '_onFullscreen',
            'click .btn-refresh-pdf': '_onRefreshPDF',
        },

        start: function () {
            this._super.apply(this, arguments);
            this._setupPDFViewer();
            return this._super.apply(this, arguments);
        },

        _setupPDFViewer: function () {
            var self = this;
            var $iframe = this.$('.portal-pdf-iframe');
            
            if ($iframe.length) {
                // Manejar el evento de carga del iframe
                $iframe.on('load', function () {
                    self._onPDFLoaded();
                });

                // Manejar errores de carga
                $iframe.on('error', function () {
                    self._onPDFError();
                });

                // Agregar indicador de carga
                this._showLoadingIndicator();
            }
        },

        _onPDFLoaded: function () {
            this._hideLoadingIndicator();
            this._addKeyboardShortcuts();
        },

        _onPDFError: function () {
            this._hideLoadingIndicator();
            this._showErrorMessage();
        },

        _showLoadingIndicator: function () {
            var $container = this.$('.pdf-container');
            $container.addClass('loading');
            
            var $loading = $('<div class="pdf-loading-overlay">' +
                '<div class="d-flex align-items-center justify-content-center h-100">' +
                '<i class="fa fa-spinner fa-spin fa-2x text-primary me-3"></i>' +
                '<span>Cargando documento PDF...</span>' +
                '</div></div>');
            
            $container.append($loading);
        },

        _hideLoadingIndicator: function () {
            this.$('.pdf-loading-overlay').fadeOut(300, function () {
                $(this).remove();
            });
        },

        _showErrorMessage: function () {
            var $container = this.$('.pdf-container');
            var $error = $('<div class="alert alert-danger">' +
                '<i class="fa fa-exclamation-triangle"></i> ' +
                'Error al cargar el documento PDF. ' +
                '<a href="#" class="btn-refresh-pdf">Intentar de nuevo</a>' +
                '</div>');
            
            $container.html($error);
        },

        _onFullscreen: function (ev) {
            ev.preventDefault();
            var iframe = this.$('.portal-pdf-iframe')[0];
            
            if (iframe) {
                if (iframe.requestFullscreen) {
                    iframe.requestFullscreen();
                } else if (iframe.mozRequestFullScreen) {
                    iframe.mozRequestFullScreen();
                } else if (iframe.webkitRequestFullscreen) {
                    iframe.webkitRequestFullscreen();
                } else if (iframe.msRequestFullscreen) {
                    iframe.msRequestFullscreen();
                }
            }
        },

        _onRefreshPDF: function (ev) {
            ev.preventDefault();
            var $iframe = this.$('.portal-pdf-iframe');
            
            if ($iframe.length) {
                this._showLoadingIndicator();
                $iframe[0].src = $iframe[0].src; // Recargar iframe
            }
        },

        _addKeyboardShortcuts: function () {
            var self = this;
            
            $(document).on('keydown.portal_pdf', function (ev) {
                // F11 para pantalla completa
                if (ev.key === 'F11') {
                    ev.preventDefault();
                    self._onFullscreen(ev);
                }
                
                // Ctrl+R para recargar PDF
                if (ev.ctrlKey && ev.key === 'r') {
                    ev.preventDefault();
                    self._onRefreshPDF(ev);
                }
            });
        },

        destroy: function () {
            $(document).off('keydown.portal_pdf');
            this._super.apply(this, arguments);
        }
    });

    // Widget para mejorar la experiencia de descarga
    publicWidget.registry.PortalDownloadButton = publicWidget.Widget.extend({
        selector: 'a[href*="/web/content/"]',
        events: {
            'click': '_onDownloadClick',
        },

        _onDownloadClick: function (ev) {
            var $btn = $(ev.currentTarget);
            
            // Agregar indicador visual de descarga
            var originalText = $btn.html();
            $btn.html('<i class="fa fa-spinner fa-spin"></i> Descargando...');
            $btn.prop('disabled', true);
            
            // Restaurar botón después de un tiempo
            setTimeout(function () {
                $btn.html(originalText);
                $btn.prop('disabled', false);
            }, 2000);
        }
    });

    // Widget para información adicional del PDF
    publicWidget.registry.PortalPDFInfo = publicWidget.Widget.extend({
        selector: '.portal-pdf-info',
        
        start: function () {
            this._addTooltips();
            return this._super.apply(this, arguments);
        },

        _addTooltips: function () {
            // Agregar tooltips informativos
            this.$('[data-toggle="tooltip"]').tooltip();
            
            // Agregar información adicional si es necesario
            var $info = this.$('.pdf-info-details');
            if ($info.length === 0) {
                $info = $('<div class="pdf-info-details mt-2"></div>');
                this.$el.append($info);
            }
        }
    });

    // Funciones utilitarias globales para el portal
    window.portalPDFUtils = {
        
        openPDFInNewWindow: function (url) {
            var newWindow = window.open(url, '_blank', 
                'width=1000,height=800,scrollbars=yes,resizable=yes');
            
            if (!newWindow) {
                alert('Por favor, permite las ventanas emergentes para ver el PDF.');
            }
            
            return newWindow;
        },

        downloadPDF: function (url, filename) {
            var link = document.createElement('a');
            link.href = url;
            link.download = filename || 'documento.pdf';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        },

        printPDF: function (url) {
            var printWindow = this.openPDFInNewWindow(url);
            
            if (printWindow) {
                printWindow.onload = function () {
                    setTimeout(function () {
                        printWindow.print();
                    }, 1000);
                };
            }
        }
    };

    return {
        PortalPDFViewer: publicWidget.registry.PortalPDFViewer,
        PortalDownloadButton: publicWidget.registry.PortalDownloadButton,
        PortalPDFInfo: publicWidget.registry.PortalPDFInfo
    };
});