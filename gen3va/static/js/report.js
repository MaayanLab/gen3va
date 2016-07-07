function createAndManageVisualizations(config) {

    $(function() {
        dataTables();
        watchClustergramWidths();
        plotPCA(config.pcaPlot);
        createClustergram(
            '#genes-heat-map',
            config.genesHeatMap
        );
        createClustergram(
            '#l1000cds2-heat-map',
            config.l1000cds2HeatMap
        );
        createAndWatchEnrichrHeatMaps(config.enrichrHeatMaps);
    });

    var clustergrams = [];

    function createAndWatchEnrichrHeatMaps(enrichrHeatMaps) {
        var $enrichr = $('#enrichr-heat-maps'),
            len = Object.keys(enrichrHeatMaps).length,
            heatMap,
            rootElement,
            i;

        for (i = 0; i < len; i++) {
            heatMap = enrichrHeatMaps[i];
            rootElement = '#' + heatMap.enrichr_library;
            $enrichr.append(
                '<div ' +
                '   id="' + heatMap.enrichr_library + '"' +
                '   class="heat-map enrichr-heat-map"' +
                '></div>'
            );
            createClustergram(rootElement, heatMap);
        }

        showEnrichrHeatMap(enrichrHeatMaps[0].enrichr_library);
        watchEnrichrClustergram($enrichr, enrichrHeatMaps);
    }

    function createClustergram(rootElement, clustergramData) {
        var clustergram = Clustergrammer({
            root: rootElement,
            network_data: clustergramData.network
        });
        clustergrams.push(clustergram);
    }

    function watchEnrichrClustergram($enrichr, enrichrHeatMaps) {
        // When the user selects a new library, toggle the visible library.
        $enrichr.find('select').change(function(evt) {
            var newEnrichrLibrary = $(evt.target).val();
            showEnrichrHeatMap(newEnrichrLibrary);
        });
    }

    function showEnrichrHeatMap(enrichrLibrary) {
        $('.enrichr-heat-map').hide();
        $('#' + enrichrLibrary).show();
    }

    function clustergramExists(clustergram) {
        var i;
        for (i = 0; i < clustergrams.length; i++) {
            if (clustergrams[i].root === clustergram.root) {
                return true;
            }
        }
        return false;
    }

    function dataTables() {
        $('table').DataTable({ iDisplayLength: 5 });
    }

    function watchClustergramWidths() {
        // Debounce this resizing callback because it's fairly intensive.
        $(window).resize(_.debounce(function() {
            $.each(clustergrams, function(i, clustergram) {
                clustergram.resize_viz();
            });
        }, 250));
    }

    function plotPCA(pcaObj) {
        if (typeof pcaObj === 'undefined')
            return;

        // If there is only one data series, use Geneva's blue. Otherwise,
        // let Highcharts figure it out.
        if (pcaObj.series.length == 1) {
            Highcharts.setOptions({
                colors: ['#1689E5']
            });
        }

        var tooltipFormatter = function() { return this.key; },
            mins = pcaObj.ranges[1],
            maxs = pcaObj.ranges[0],
            titles = pcaObj.titles,
            chart;

        chart = new Highcharts.Chart({
            chart: {
                renderTo: 'pca-plot',
                margin: [150, 150, 150, 150],
                type: 'scatter',
                options3d: {
                    enabled: true,
                    alpha: 20,
                    beta: 30,
                    depth: 500
                }
            },
            legend: {
                floating: true,
                layout: 'vertical',
                align: 'left',
                verticalAlign: 'top'
            },
            title: {
                text: '3D PCA plot'
            },
            subtitle: {
                text: 'using x y z coordinates'
            },
            xAxis: {
                title: {text: titles[0]},
                min: mins[0],
                max: maxs[0]
            },
            yAxis: {
                title: {text: titles[1]},
                min: mins[1],
                max: maxs[1]
            },
            zAxis: {
                title: {text: titles[2]},
                min: mins[2],
                max: maxs[2]
            },
            series: pcaObj.series,
            tooltip: {
                formatter: tooltipFormatter,
                useHTML: true,
                backgroundColor: '#7FB800', // green
                borderColor: '#7FB800',
                borderRadius: 0,
                shadow: false,
                style: {
                    color: 'white',
                    fontFamily: 'Roboto',
                    fontWeight: 'bold',
                    padding: 6
                }
            }
        });

        // Add mouse events for rotation
        $(chart.container).bind('mousedown.hc touchstart.hc', function (e) {
            e = chart.pointer.normalize(e);

            var posX = e.pageX,
                posY = e.pageY,
                alpha = chart.options.chart.options3d.alpha,
                beta = chart.options.chart.options3d.beta,
                newAlpha,
                newBeta,
                sensitivity = 5; // lower is more sensitive

            $(document).bind({
                'mousemove.hc touchdrag.hc': function (e) {
                    newBeta = beta + (posX - e.pageX) / sensitivity;
                    chart.options.chart.options3d.beta = newBeta;
                    newAlpha = alpha + (e.pageY - posY) / sensitivity;
                    chart.options.chart.options3d.alpha = newAlpha;
                    chart.redraw(false);
                },
                'mouseup touchend': function () {
                    $(document).unbind('.hc');
                }
            });
        });
    }
}
